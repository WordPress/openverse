"""
See the issue for context and motivation: https://github.com/WordPress/openverse/issues/4452

This DAG triggers a run of the batched update DAG. It generates a new list of tags by
trimming all existing tags and re-inserting only the distinct tags of the resulting list of tags.

Only records before the CC Search -> Openverse transition are affected. As such, because all
audio records are dated after that transition, we only need to scan images.
"""

from datetime import datetime, timedelta
from textwrap import dedent

from airflow.decorators import dag, task
from airflow.models.abstractoperator import AbstractOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from common.constants import DAG_DEFAULT_ARGS, POSTGRES_CONN_ID
from common.sql import PostgresHook
from database.batched_update.constants import DAG_ID as BATCHED_UPDATE_DAG_ID


DAG_ID = "decode_and_deduplicate_image_tags"

HAS_RAW_ESCAPED_UNICODE = (
    r'(@.name like_regex "\\\\(x)([\\da-f]{2})|\\\\(u)([\\da-f]{4})" flag "i")'
)


@task
def ensure_ov_unistr(
    postgres_conn_id: str = POSTGRES_CONN_ID,
    task: AbstractOperator = None,
):
    """
    Create a naïve implementation of Postgres 14+ ``unistr``.

    We are on Postgres 13 and have to do without ``unistr``. For all intents and purposes,
    this implementation solves the problem for us.

    The ``ov`` prefix prevents clashing with the built-in should we upgrade.
    """

    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id,
        default_statement_timeout=PostgresHook.get_execution_timeout(task),
        log_sql=True,
    )

    return postgres.run(
        dedent(
            """
            CREATE OR REPLACE FUNCTION ov_unistr (string text)
                RETURNS text
            AS $$
                return string.encode().decode("unicode_escape") if string else string
            $$ LANGUAGE plpython3u;
            """
        )
    )


@dag(
    dag_id=DAG_ID,
    schedule=None,
    start_date=datetime(2024, 6, 3),
    tags=["database"],
    doc_md=__doc__,
    max_active_runs=1,
    default_args=DAG_DEFAULT_ARGS,
)
def decode_and_deduplicate_image_tags():
    ensure_ov_unistr() >> TriggerDagRunOperator(
        task_id="trigger_batched_update",
        trigger_dag_id=BATCHED_UPDATE_DAG_ID,
        wait_for_completion=True,
        retries=0,
        conf={
            "query_id": DAG_ID,
            "table_name": "image",
            # jsonb_path_query_first will return null if the first argument is null,
            # and so is safe for tagless works
            "select_query": dedent(
                f"""
                WHERE jsonb_path_query_first(
                    image.tags,
                    '$[*] ? {HAS_RAW_ESCAPED_UNICODE}'
                ) IS NOT NULL
                """
            ).strip(),
            "update_query": dedent(
                f"""
                SET updated_on = NOW(),
                    tags = (
                        SELECT jsonb_agg(deduplicated.tag) FROM (
                            SELECT DISTINCT ON (all_tags.tag->'name', all_tags.tag->'provider')
                                all_tags.tag tag
                            FROM (
                                SELECT
                                    jsonb_array_elements(
                                        separated_tags.no_escape || (
                                            SELECT jsonb_agg(
                                                jsonb_set(
                                                    to_escape,
                                                    '{{name}}',
                                                    to_jsonb(ov_unistr(to_escape->>'name'))
                                                )
                                            ) FROM jsonb_array_elements(separated_tags.needs_escape) AS to_escape
                                        )
                                    ) tag
                                FROM (
                                    SELECT
                                        jsonb_path_query_array(image.tags, '$[*] ? (!{HAS_RAW_ESCAPED_UNICODE})') no_escape,
                                        jsonb_path_query_array(image.tags, '$[*] ? {HAS_RAW_ESCAPED_UNICODE}') needs_escape
                                ) AS separated_tags
                            ) AS all_tags
                        ) AS deduplicated
                    )
                """
            ).strip(),
            "update_timeout": int(timedelta(hours=10).total_seconds()),
            "dry_run": False,
        },
    )


decode_and_deduplicate_image_tags()

"""
See the issue for context and motivation: https://github.com/WordPress/openverse/issues/4452

This DAG triggers a run of the batched update DAG. It generates a new list of tags by
trimming all existing tags and re-inserting only the distinct tags of the resulting list of tags.
"""

from datetime import datetime, timedelta
from pathlib import Path
from textwrap import dedent, indent

from airflow.decorators import dag, task
from airflow.models.abstractoperator import AbstractOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from common.constants import DAG_DEFAULT_ARGS, MEDIA_TYPES, POSTGRES_CONN_ID
from common.sql import PostgresHook
from database.batched_update.constants import DAG_ID as BATCHED_UPDATE_DAG_ID


DAG_ID = "decode_and_deduplicate_tags"

DOUBLE_BACKSLASH_ESCAPE = r"\\(x)([\da-f]{2})" "|" r"\\(u)([\da-f]{4})"
NO_BACKSLASH_ESCAPE = r"(u)([\da-f]{4})"

PG_ESCAPED_DOUBLE_BACKSLASH_ESCAPE = DOUBLE_BACKSLASH_ESCAPE.replace("\\", "\\\\")
PG_ESCAPED_NO_BACKSLASH_ESCAPE = NO_BACKSLASH_ESCAPE.replace("\\", "\\\\")

MAYBE_NEEDS_DECODING = f'(@.name like_regex "{PG_ESCAPED_DOUBLE_BACKSLASH_ESCAPE}" flag "i" || @.name like_regex "{PG_ESCAPED_NO_BACKSLASH_ESCAPE}" flag "i")'
"""
JSONB query for tags that might need decoding.

The "maybe" is operative, because we need to *try* to decode strings like
'ciudaddelassiencias' where ``udadd`` _looks_ like a unicode pattern, but isn't.

However, are there strings where this will fail. We won't accidentally decode `udadd` because `dadd`
is a surrogate character, unable to be URI encoded. ``convert_grp`` catches that.

However, take "cade" from "Leucadendron". It corresponds to the Hangul character 쫞.

If we try to "best guess" this, with the strategy we've implemented, Leucadendron will be turned into
"Leu쫞ndron". Clearly that's incorrect.

Therefore, this strategy simply will not work to solve the "no backslash escape"'d strings.

Can we skip those entirely???
"""


OV_DECODE_BROKEN_UNISTR_CODE_ARGUMENT_NAME = "string"
OV_DECODE_BROKEN_UNISTR_CODE = (
    (Path(__file__).parent / "ov_decode_broken_unistr__plpython3u.py.tpl")
    .read_text()
    .format(
        DOUBLE_BACKSLASH_ESCAPE=DOUBLE_BACKSLASH_ESCAPE,
        NO_BACKSLASH_ESCAPE=NO_BACKSLASH_ESCAPE,
        ARGUMENT_NAME=OV_DECODE_BROKEN_UNISTR_CODE_ARGUMENT_NAME,
    )
)

# Add testing data
"""
UPDATE image
SET tags = tags || '[{"name": "ciudaddelassiencias", "provider": "flickr"}, {"name": "muséo", "provider": "flickr"}, {"name": "muséo", "provider": "recognition", "accuracy": 0.96}, {"name": "uploaded by me", "provider": "flickr"}, {}, {"name": "unknown", "provider": "recognition", "accuracy": 0.86}, {"name": "mus\\xe9o", "provider": "flickr"}, {"name": "mus\\u00e9o", "provider": "flickr"}, {"name": "musu00e9o", "provider": "flickr"}, {"name": "mus\\u00e9o", "provider": "flickr"}, {"name": "mus\\u00E9o", "provider": "flickr"}]'::jsonb
WHERE identifier IN (SELECT identifier FROM image WHERE provider = 'flickr' AND tags IS NOT NULL LIMIT 10);
"""

# Query data for matching
"""
select t from (select jsonb_path_query_array(
     tags,
     '$[*] ? (@.name like_regex "\\\\(x)([\\da-f]{2})|\\\\(u)([\\da-f]{4})" flag "i" || @.name like_regex "(u)([\\da-f]{4})" flag
 "i")'
 ) t from image) as tt where jsonb_array_length(tt.t) > 0;
"""

# Clean up testing data
"""
UPDATE image SET tags = jsonb_path_query_array(
    tags,
    '$[*] ? (!(@.name like_regex "\\\\(x)([\\da-f]{2})|\\\\(u)([\\da-f]{4})" flag "i" || @.name like_regex "(u)([\\da-f]{4})" flag "i"))'
);
"""


@task
def ensure_ov_decode_broken_unistr_function(
    postgres_conn_id: str = POSTGRES_CONN_ID,
    task: AbstractOperator = None,
):
    """
    Create a PL/Python function based on https://github.com/WordPress/openverse/pull/4143

    Ideally we'd be able to implement this logic in PSQL directly, but we're on version 13 of Postgres,
    and therefore missing some key features that would make this more straightforward in regular SQL.

    In particular, we do not have access to ``unistr``, for processing unicode escaped strings.
    That would replace the entire DOUBLE_BACKSLASH_ESCAPE condition in ``decode_data``.

    It could all be done in SQL, but PL/Python is available, and (provided it doesn't carry a significant performance
    issue), we don't need to re-write the already-working code that Olga worked on in the linked PR.
    """

    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id,
        default_statement_timeout=PostgresHook.get_execution_timeout(task),
        log_sql=True,
    )

    indented_function_code = indent(OV_DECODE_BROKEN_UNISTR_CODE, " " * 4 * 4)
    return postgres.run(
        dedent(
            f"""
            CREATE OR REPLACE FUNCTION ov_decode_broken_unistr_function ({OV_DECODE_BROKEN_UNISTR_CODE_ARGUMENT_NAME} text)
                RETURNS text
            AS $$
{indented_function_code}
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
def decode_and_deduplicate_tags():
    ensure_func = ensure_ov_decode_broken_unistr_function()

    ensure_func >> TriggerDagRunOperator.partial(
        task_id=DAG_ID,
        trigger_dag_id=BATCHED_UPDATE_DAG_ID,
        wait_for_completion=True,
        execution_timeout=timedelta(hours=5),
        max_active_tis_per_dag=2,
        map_index_template="""{{ task.conf['table_name'] }}""",
        retries=0,
    ).expand(
        conf=[
            {
                "query_id": f"{DAG_ID}_{media_type}",
                "table_name": media_type,
                # jsonb_path_query_first will return null if the first argument is null,
                # and so is safe for tagless works
                "select_query": dedent(
                    f"""
                    WHERE jsonb_path_query_first(
                        {media_type}.tags,
                        '$[*] ? {MAYBE_NEEDS_DECODING}'
                    ) IS NOT NULL
                    """
                ).strip(),
                "update_query": dedent(
                    f"""
                    SET updated_on = now(),
                    tags = (
                        SELECT
                            jsonb_agg(
                                jsonb_set(
                                    decoded.tag,
                                    '{{name}}',
                                    to_jsonb(decoded.fixed_name)
                                )
                            )
                        FROM (
                            SELECT DISTINCT ON (fixed_name, tag->'provider')
                                ov_decode_broken_unistr_function(tag->>'name') fixed_name,
                                tag
                            FROM jsonb_array_elements({media_type}.tags || '[]'::jsonb) tag
                        ) decoded
                    )
                    """
                ).strip(),
                "dry_run": False,
            }
            for media_type in MEDIA_TYPES
        ]
    )


decode_and_deduplicate_tags()

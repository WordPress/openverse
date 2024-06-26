"""
See the issue for context and motivation: https://github.com/WordPress/openverse/issues/4199

This DAG triggers a run of the batched update DAG. It generates a new list of tags by
trimming all existing tags and re-inserting only the distinct tags of the resulting list of tags.
"""

from datetime import datetime, timedelta
from textwrap import dedent

from airflow.decorators import dag
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from common.constants import DAG_DEFAULT_ARGS, MEDIA_TYPES
from database.batched_update.constants import DAG_ID as BATCHED_UPDATE_DAG_ID


DAG_ID = "trim_and_deduplicate_tags"


@dag(
    dag_id=DAG_ID,
    schedule=None,
    start_date=datetime(2024, 6, 3),
    tags=["database"],
    doc_md=__doc__,
    max_active_runs=1,
    default_args=DAG_DEFAULT_ARGS,
)
def trim_and_deduplicate_tags():
    TriggerDagRunOperator.partial(
        task_id=DAG_ID,
        trigger_dag_id=BATCHED_UPDATE_DAG_ID,
        wait_for_completion=True,
        max_active_tis_per_dag=2,
        map_index_template="""{{ task.conf['table_name'] }}""",
        retries=0,
    ).expand(
        conf=[
            {
                "query_id": f"{DAG_ID}_{media_type}",
                "table_name": media_type,
                "select_query": (
                    "WHERE "
                    + (
                        ""
                        if media_type == "audio"
                        # We've identified these image providers in particular definitely have tags that need trimming, so we can narrow the query starting there at least
                        else (
                            "provider IN ('flickr', 'geographorguk', 'thingiverse', 'animaldiversity', 'clevelandmuseum', 'digitaltmuseum') AND "
                        )
                    )
                    + (
                        f"""EXISTS (SELECT 1 FROM jsonb_array_elements({media_type}.tags) AS t WHERE t->>'name' ILIKE ' %' OR t->>'name' ILIKE '% ')"""
                    )
                ),
                "update_query": (
                    "SET updated_on = NOW(), "
                    + dedent(
                        f"""
                        tags = (
                            SELECT
                                jsonb_agg(
                                    jsonb_set(
                                        deduped.tag,
                                        '{{name}}',
                                        to_jsonb(deduped.trimmed_name)
                                    )
                                )
                            FROM (
                                SELECT DISTINCT ON (trimmed_name, tag->'provider')
                                    trim(tag->>'name') trimmed_name,
                                    tag
                                FROM jsonb_array_elements({media_type}.tags || '[]'::jsonb) tag
                            ) deduped
                        )
                        """
                    )
                ),
                "update_timeout": int(timedelta(hours=5).total_seconds()),
                "dry_run": False,
            }
            for media_type in MEDIA_TYPES
        ]
    )


trim_and_deduplicate_tags()

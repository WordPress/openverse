"""
# Trim and Deduplicate Tags

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
    max_active_runs=1,
    default_args=DAG_DEFAULT_ARGS,
)
def trim_and_deduplicate_tags():
    TriggerDagRunOperator.partial(
        task_id=DAG_ID,
        trigger_dag_id=BATCHED_UPDATE_DAG_ID,
        wait_for_completion=True,
        execution_timeout=timedelta(hours=5),
        max_active_tis_per_dag=1,
        map_index_template="""{{ task.conf['table_name'] }}""",
        retries=0,
    ).expand(
        conf=[
            {
                "query_id": f"{DAG_ID}_{media_type}",
                "table_name": media_type,
                # Just iterate through all the rows, don't bother sub-selecting as it's impossible to reasonably do so for trimming
                "select_query": "WHERE true",
                "update_query": dedent(
                    """SET tags = (
                        SELECT
                            jsonb_strip_nulls(jsonb_agg(trimed_and_deduped))
                        FROM (
                            SELECT DISTINCT ON (trim("name"))
                                trim("name") "name",
                                provider,
                                accuracy
                            FROM
                                jsonb_to_recordset(tags || '[]'::jsonb) as x("name" text, provider text, accuracy float)
                        ) trimed_and_deduped
                    )"""
                ),
                "dry_run": False,
            }
            for media_type in MEDIA_TYPES
        ]
    )


trim_and_deduplicate_tags()

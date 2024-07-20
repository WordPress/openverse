"""
Catalog Data Cleaner DAG

Use the TSV files created during the cleaning step of the ingestion process to bring
the changes into the catalog database and make the updates permanent.

The DAG has a structure similar to the batched_update DAG, but with a few key
differences:
  1. Given the structure of the TSV, it updates a single column at a time.
  2. The batch updates are parallelized to speed up the process. The maximum number of
     active tasks is limited to 3 (at first to try it out and) to avoid overwhelming
     the database.
  3. It needs slightly different SQL queries to update the data. One change for example,
     is that it only works with the `image` table given that is the only one where the
     cleaning steps are applied to in the ingestion server.
"""

import logging
from datetime import timedelta

from airflow.decorators import dag, task
from airflow.models import Variable
from airflow.models.abstractoperator import AbstractOperator
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.utils.trigger_rule import TriggerRule

from common import slack
from common.constants import DAG_DEFAULT_ARGS, POSTGRES_CONN_ID
from common.sql import (
    RETURN_ROW_COUNT,
    PGExecuteQueryOperator,
    PostgresHook,
    single_value,
)
from database.batched_update.batched_update import run_sql
from database.catalog_cleaner import constants


logger = logging.getLogger(__name__)


@task
def count_dirty_rows_and_notify(temp_table_name: str, task: AbstractOperator = None):
    """Get the number of rows in the temp table before the updates."""
    count = run_sql.function(
        dry_run=False,
        sql_template=f"SELECT COUNT(*) FROM {temp_table_name}",
        query_id=f"{temp_table_name}_count",
        handler=single_value,
        task=task,
    )
    column = temp_table_name.split("_")[-1]
    notify_slack.function(
        text=f"Starting the cleaning process in upstream DB for column `{column}`."
        f" Expecting {count:,} rows affected given `{temp_table_name}` table."
    )
    return count


@task
def get_batches(total_row_count: int, batch_size: int) -> list[tuple[int, int]]:
    """Return a list of tuples with the start and end row_id for each batch."""
    return [(i, i + batch_size) for i in range(0, total_row_count, batch_size)]


@task(map_index_template="{{ index_template }}")
def update_batch(
    batch: tuple[int, int],
    temp_table_name: str,
    column: str,
    task: AbstractOperator = None,
):
    batch_start, batch_end = batch
    logger.info(f"Going through row_id {batch_start:,} to {batch_end:,}.")

    # Includes the formatted batch range in the context to be used as the index
    # template for easier identification of the tasks in the UI.
    context = get_current_context()
    context["index_template"] = f"{batch_start}__{batch_end}"

    pg = PostgresHook(
        postgres_conn_id=POSTGRES_CONN_ID,
        default_statement_timeout=PostgresHook.get_execution_timeout(task),
    )
    query = constants.UPDATE_SQL.format(
        column=column,
        temp_table_name=temp_table_name,
        batch_start=batch_start,
        batch_end=batch_end,
    )
    count = pg.run(query, handler=RETURN_ROW_COUNT)
    return count


@task
def sum_up_counts(counts: list[int]) -> int:
    return sum(counts)


@task
def notify_slack(text):
    slack.send_message(
        text=text,
        username=constants.SLACK_USERNAME,
        icon_emoji=constants.SLACK_ICON,
        dag_id=constants.DAG_ID,
    )


@dag(
    dag_id=constants.DAG_ID,
    default_args={
        **DAG_DEFAULT_ARGS,
        "retries": 0,
        "execution_timeout": timedelta(days=7),
    },
    schedule=None,
    catchup=False,
    tags=["database"],
    doc_md=__doc__,
    render_template_as_native_obj=True,
    params={
        "s3_bucket": Param(
            default="openverse-catalog",
            type="string",
            description="The S3 bucket where the TSV file is stored.",
        ),
        "s3_path": Param(
            default="shared/data-refresh-cleaned-data/<file_name>.tsv",
            type="string",
            description="The S3 path to the TSV file within the bucket.",
        ),
        "column": Param(
            type="string",
            enum=["url", "creator_url", "foreign_landing_url"],
            description="The column of the table to apply the updates.",
        ),
        "batch_size": Param(
            default=10000,
            type="integer",
            description="The number of records to update per batch.",
        ),
    },
)
def catalog_cleaner():
    aws_region = Variable.get("AWS_DEFAULT_REGION", default_var="us-east-1")
    max_concurrent_tasks = Variable.get(
        "CLEANER_MAX_CONCURRENT_DB_UPDATE_TASKS", default_var=3, deserialize_json=True
    )

    column = "{{ params.column }}"
    temp_table_name = f"temp_cleaned_image_{column}"

    create_table = PGExecuteQueryOperator(
        task_id="create_temp_table",
        postgres_conn_id=POSTGRES_CONN_ID,
        sql=constants.CREATE_TEMP_TABLE_SQL.format(
            temp_table_name=temp_table_name, column=column
        ),
    )

    load = PGExecuteQueryOperator(
        task_id="load_temp_table_from_s3",
        postgres_conn_id=POSTGRES_CONN_ID,
        sql=constants.IMPORT_SQL.format(
            temp_table_name=temp_table_name,
            column=column,
            bucket="{{ params.s3_bucket }}",
            s3_path_to_file="{{ params.s3_path }}",
            aws_region=aws_region,
        ),
    )

    create_index = PGExecuteQueryOperator(
        task_id="create_temp_table_index",
        postgres_conn_id=POSTGRES_CONN_ID,
        sql=constants.CREATE_INDEX_SQL.format(temp_table_name=temp_table_name),
    )

    count = count_dirty_rows_and_notify(temp_table_name)

    batches = get_batches(total_row_count=count, batch_size="{{ params.batch_size }}")

    updates = (
        update_batch.override(
            max_active_tis_per_dag=max_concurrent_tasks,
            retries=0,
        )
        .partial(temp_table_name=temp_table_name, column=column)
        .expand(batch=batches)
    )

    total = sum_up_counts(updates)

    drop = PGExecuteQueryOperator(
        task_id="drop_temp_table",
        postgres_conn_id=POSTGRES_CONN_ID,
        sql=constants.DROP_SQL.format(temp_table_name=temp_table_name),
        execution_timeout=timedelta(minutes=1),
    )

    notify_success = notify_slack.override(task_id="notify_success")(
        f"Upstream cleaning was completed successfully updating column `{column}` for"
        f" {total} rows.",
    )

    notify_failure = notify_slack.override(
        task_id="notify_failure", trigger_rule=TriggerRule.ONE_FAILED
    )("Upstream cleaning failed. Check the logs for more information.")

    create_table >> load >> create_index >> count

    # Make explicit the dependency from total (sum_up_counts task) to show it in the graph
    updates >> [drop, total] >> notify_success

    drop >> notify_failure


catalog_cleaner()

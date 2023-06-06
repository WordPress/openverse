import logging
from datetime import timedelta

from airflow.decorators import task
from airflow.models.abstractoperator import AbstractOperator

from common import slack
from common.constants import POSTGRES_CONN_ID
from common.sql import PostgresHook
from database.batched_update.constants import (
    DAG_ID,
    RETURN_ROW_COUNT,
    SLACK_ICON,
    SLACK_USERNAME,
    TEMP_TABLE_NAME,
    UPDATE_BATCH_QUERY,
)


logger = logging.getLogger(__name__)


@task
def run_sql(
    dry_run: bool,
    sql_template: str,
    query_id: str,
    log_sql: bool = True,
    postgres_conn_id: str = POSTGRES_CONN_ID,
    task: AbstractOperator = None,
    timeout: timedelta = None,
    **kwargs,
):
    query = sql_template.format(
        temp_table_name=TEMP_TABLE_NAME.format(query_id=query_id), **kwargs
    )
    if dry_run:
        logger.info(
            "This is a dry run: no SQL will be executed. To perform the updates,"
            " rerun the DAG with the conf option `'dry_run': false`."
        )
        logger.info(query)
        return 0

    postgres = PostgresHook(
        postgres_conn_id=POSTGRES_CONN_ID,
        default_statement_timeout=(
            timeout if timeout else PostgresHook.get_execution_timeout(task)
        ),
        log_sql=log_sql,
    )

    return postgres.run(query, handler=RETURN_ROW_COUNT)


@task
def update_batches(
    expected_row_count: int,
    batch_size: int,
    dry_run: bool,
    table_name: str,
    query_id: str,
    update_query: str,
    update_timeout: int,
    postgres_conn_id=POSTGRES_CONN_ID,
    task: AbstractOperator = None,
    **kwargs,
):
    # We iterate over row_index, which is 1-indexed
    batch_start = 1
    total_count = 0

    while batch_start <= expected_row_count:
        batch_end = batch_start + batch_size

        logger.info(f"Updating rows with id {batch_start} through {batch_end}.")
        count = run_sql.function(
            dry_run=dry_run,
            sql_template=UPDATE_BATCH_QUERY,
            query_id=query_id,
            # Only log the query the first time, so as not to spam the logs
            log_sql=batch_start == 1,
            timeout=update_timeout,
            task=task,
            table_name=table_name,
            update_query=update_query,
            batch_start=batch_start,
            batch_end=batch_end,
            postgres_conn_id=postgres_conn_id,
        )

        total_count += count
        batch_start = batch_end
        logger.info(
            f"Updated {total_count} rows. {expected_row_count - total_count} remaining."
        )

    return total_count


@task
def notify_slack(text: str) -> None:
    slack.send_message(
        text,
        username=SLACK_USERNAME,
        icon_emoji=SLACK_ICON,
        dag_id=DAG_ID,
    )

import logging
from datetime import timedelta

from airflow.decorators import task
from airflow.models.abstractoperator import AbstractOperator

from common import slack
from common.constants import POSTGRES_CONN_ID
from common.sql import PostgresHook
from database.batched_update import constants


logger = logging.getLogger(__name__)


def _single_value(cursor):
    try:
        row = cursor.fetchone()
        return row[0]
    except Exception as e:
        raise ValueError("Unable to extract expected row data from cursor") from e


@task.branch
def resume_update(
    resume_update: bool,
):
    """
    Return True to short circuit temp table creation if this DagRun is
    resuming from an existing temp table.

    A DAG can be resumed only if `
    """
    if resume_update:
        # Skip table creation and indexing
        return constants.GET_EXPECTED_COUNT_TASK_ID
    return constants.CREATE_TEMP_TABLE_TASK_ID


@task
def get_expected_update_count(query_id: str, batch_start: int | None, dry_run: bool):
    """
    Get the number of records left to update, when resuming an update
    on an existing temp table.
    """
    total_count = run_sql.function(
        dry_run=dry_run,
        sql_template=constants.SELECT_TEMP_TABLE_QUERY,
        query_id=query_id,
        handler=_single_value,
    )

    if batch_start:
        total_count -= batch_start
    return max(total_count, 0)


@task
def run_sql(
    dry_run: bool,
    sql_template: str,
    query_id: str,
    log_sql: bool = True,
    postgres_conn_id: str = POSTGRES_CONN_ID,
    task: AbstractOperator = None,
    timeout: timedelta = None,
    handler: callable = constants.RETURN_ROW_COUNT,
    **kwargs,
):
    query = sql_template.format(
        temp_table_name=constants.TEMP_TABLE_NAME.format(query_id=query_id), **kwargs
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

    return postgres.run(query, handler=handler)


@task
def update_batches(
    expected_row_count: int,
    batch_size: int,
    dry_run: bool,
    table_name: str,
    query_id: str,
    update_query: str,
    update_timeout: int,
    batch_start: int = 0,
    postgres_conn_id: str = POSTGRES_CONN_ID,
    task: AbstractOperator = None,
    **kwargs,
):
    updated_count = 0

    while batch_start <= expected_row_count:
        batch_end = batch_start + batch_size

        logger.info(f"Updating rows with id {batch_start} through {batch_end}.")
        count = run_sql.function(
            dry_run=dry_run,
            sql_template=constants.UPDATE_BATCH_QUERY,
            query_id=query_id,
            # Only log the query the first time, so as not to spam the logs
            log_sql=batch_start == 1,
            postgres_conn_id=postgres_conn_id,
            task=task,
            timeout=update_timeout,
            table_name=table_name,
            update_query=update_query,
            batch_start=batch_start,
            batch_end=batch_end,
        )

        updated_count += count
        batch_start = batch_end
        logger.info(
            f"Updated {updated_count} rows. {expected_row_count - updated_count}"
            " remaining."
        )

    return updated_count


@task
def notify_slack(text: str, dry_run: bool) -> None:
    if not dry_run:
        slack.send_message(
            text,
            username=constants.SLACK_USERNAME,
            icon_emoji=constants.SLACK_ICON,
            dag_id=constants.DAG_ID,
        )
    else:
        logger.info(text)

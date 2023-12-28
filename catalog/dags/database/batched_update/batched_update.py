import logging
from datetime import timedelta

from airflow.decorators import task
from airflow.models import Variable
from airflow.models.abstractoperator import AbstractOperator

from common import slack
from common.constants import POSTGRES_CONN_ID
from common.sql import RETURN_ROW_COUNT, PostgresHook, single_value
from database.batched_update import constants


logger = logging.getLogger(__name__)


@task.branch
def resume_update(
    resume_update: bool,
):
    """
    Return True to short circuit temp table creation if this DagRun is
    resuming from an existing temp table.
    """
    if resume_update:
        # Skip table creation and indexing
        return constants.GET_EXPECTED_COUNT_TASK_ID
    return constants.CREATE_TEMP_TABLE_TASK_ID


@task
def get_expected_update_count(
    query_id: str, total_row_count: int | None, dry_run: bool
):
    """Get the number of records in the temp table."""
    # If we created the temp table as part of this DagRun, the total row count is
    # passed in through XComs and is simply forwarded.
    if total_row_count is not None:
        return total_row_count

    # If `resume_update` is True, we skip the table creation task and the count will
    # not be available in XComs. We instead explicitly query the table for the count.
    return run_sql.function(
        dry_run=dry_run,
        sql_template=constants.SELECT_TEMP_TABLE_COUNT_QUERY,
        query_id=query_id,
        handler=single_value,
    )


@task
def run_sql(
    dry_run: bool,
    sql_template: str,
    query_id: str,
    log_sql: bool = True,
    postgres_conn_id: str = POSTGRES_CONN_ID,
    task: AbstractOperator = None,
    timeout: timedelta = None,
    handler: callable = RETURN_ROW_COUNT,
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
        postgres_conn_id=postgres_conn_id,
        default_statement_timeout=(
            timeout if timeout else PostgresHook.get_execution_timeout(task)
        ),
        log_sql=log_sql,
    )

    return postgres.run(query, handler=handler)


@task
def update_batches(
    total_row_count: int,
    batch_size: int,
    dry_run: bool,
    table_name: str,
    query_id: str,
    update_query: str,
    update_timeout: int,
    batch_start_var: str,
    postgres_conn_id: str = POSTGRES_CONN_ID,
    task: AbstractOperator = None,
    **kwargs,
):
    if total_row_count == 0:
        return 0

    # Progress is tracked in an Airflow variable. When the task run starts, we resume
    # from the start point set by this variable (defaulted to 0). This prevents the
    # task from starting over at the beginning on retries.
    initial_batch_start = Variable.get(batch_start_var, 0, deserialize_json=True)
    logger.info(f"Starting at {initial_batch_start:,}")

    updated_count = 0
    batch_start = initial_batch_start
    while batch_start <= total_row_count:
        batch_end = batch_start + batch_size

        logger.info(f"Updating rows with id {batch_start:,} through {batch_end:,}.")
        count = run_sql.function(
            dry_run=dry_run,
            sql_template=constants.UPDATE_BATCH_QUERY,
            query_id=query_id,
            # Only log the query the first time, so as not to spam the logs
            log_sql=batch_start == initial_batch_start,
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

        # Update the Airflow variable to the next value of batch_start.
        Variable.set(batch_start_var, batch_end)

        percent_complete = (min(batch_end, total_row_count) / total_row_count) * 100
        logger.info(
            f"Updated {updated_count:,} rows. {percent_complete:.2f}% complete."
        )

    return updated_count


@task
def drop_temp_airflow_variable(airflow_var: str):
    Variable.delete(airflow_var)


@task
def notify_slack(text: str, dry_run: bool, count: int | None = None) -> str:
    """
    Send a message to Slack, or simply log if this is a dry run.
    If a `count` is supplied, it is formatted and inserted into the text. This is
    necessary because `count` is a value pulled from XComs, and cannot be formatted
    in the task arguments.
    """

    if count is not None:
        # Print integers with comma separator
        text = text.format(count=f"{count:,}")

    if not dry_run:
        slack.send_message(
            text,
            username=constants.SLACK_USERNAME,
            icon_emoji=constants.SLACK_ICON,
            dag_id=constants.DAG_ID,
        )
    else:
        logger.info(text)

    return text

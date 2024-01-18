import logging
from datetime import timedelta

from airflow.decorators import task
from airflow.models.abstractoperator import AbstractOperator

from common import slack
from common.constants import POSTGRES_CONN_ID
from common.sql import RETURN_ROW_COUNT, PostgresHook
from common.storage.columns import DELETED_ON, Column, PROVIDER, FOREIGN_ID
from common.storage.db_columns import (
    setup_db_columns_for_media_type,
    setup_deleted_db_columns_for_media_type,
)
from database.delete_records import constants


logger = logging.getLogger(__name__)


def run_sql(
    sql_template: str,
    postgres_conn_id: str = POSTGRES_CONN_ID,
    task: AbstractOperator = None,
    timeout: timedelta = None,
    handler: callable = RETURN_ROW_COUNT,
    **kwargs,
):
    query = sql_template.format(**kwargs)

    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id,
        default_statement_timeout=(
            timeout if timeout else PostgresHook.get_execution_timeout(task)
        ),
    )

    return postgres.run(query, handler=handler)


@task
@setup_deleted_db_columns_for_media_type
@setup_db_columns_for_media_type
def create_deleted_records(
    *,
    select_query: str,
    deleted_reason: str,
    media_type: str,
    db_columns: list[Column] = None,
    deleted_db_columns: list[Column] = None,
    task: AbstractOperator = None,
    postgres_conn_id: str = POSTGRES_CONN_ID,
):
    """
    Select records from the given media table using the select query, and then for each
    record create a corresponding record in the Deleted Media table.
    """

    destination_cols = ", ".join([col.db_name for col in deleted_db_columns])

    # To build the source columns, we first list all columns in the main media table
    source_cols = ", ".join([col.db_name for col in db_columns])

    # Then add the deleted-media specific columns.
    # `deleted_on` is set to its insert value to get the current timestamp:
    source_cols += f", {DELETED_ON.get_insert_value()}"
    # `deleted_reason` is set to the given string
    source_cols += f", '{deleted_reason}'"

    # The provider, foreign_id pair uniquely identifies a record. When trying to
    # add a record to the deleted_media table, if the record's (provider, foreign_id)
    # pair is already present in the table, no additional record will be added and the
    # existing record in the deleted_media table will not be updated. This preserves the
    # record exactly as it was when it was first deleted.
    unique_cols = f"({PROVIDER.db_name}, md5({FOREIGN_ID.db_name}))"

    return run_sql(
        sql_template=constants.CREATE_RECORDS_QUERY,
        postgres_conn_id=postgres_conn_id,
        task=task,
        destination_table=f"deleted_{media_type}",
        destination_cols=destination_cols,
        source_table=media_type,
        source_cols=source_cols,
        select_query=select_query,
        unique_cols=unique_cols,
    )


@task
def delete_records_from_media_table(
    table: str, select_query: str, postgres_conn_id: str = POSTGRES_CONN_ID
):
    """Delete records matching the select_query from the given media table."""
    return run_sql(
        sql_template=constants.DELETE_RECORDS_QUERY,
        table=table,
        select_query=select_query,
    )


@task
def notify_slack(deleted_records_count: int, table_name: str, select_query: str) -> str:
    """Send a message to Slack."""
    text = (
        f"Deleted {deleted_records_count:,} records from the"
        f" `{table_name}` table matching query: `{select_query}`"
    )
    slack.send_message(
        text,
        username=constants.SLACK_USERNAME,
        icon_emoji=constants.SLACK_ICON,
        dag_id=constants.DAG_ID,
    )

    return text

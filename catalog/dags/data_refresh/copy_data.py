"""
TODO Update

TaskGroup for doing the copy data step

"""

import logging
from textwrap import dedent

from airflow.decorators import task, task_group
from airflow.models import Variable
from airflow.models.abstractoperator import AbstractOperator
from airflow.models.connection import Connection

from common.constants import (
    POSTGRES_API_CONN_IDS,
    POSTGRES_CONN_ID,
    PRODUCTION,
    SQL_INFO_BY_MEDIA_TYPE,
    Environment,
)
from common.sql import RETURN_ROW_COUNT, PostgresHook
from data_refresh import queries
from data_refresh.data_refresh_types import DataRefreshConfig


logger = logging.getLogger(__name__)


# TODO pull out of batched_update.py
@task
def _run_sql(
    postgres_conn_id: str,
    sql_template: str,
    task: AbstractOperator = None,
    timeout: float = None,
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
def get_shared_columns(
    upstream_conn_id: str,
    downstream_conn_id: str,
    upstream_table_name: str,
    downstream_table_name: str,
):
    upstream_pg = PostgresHook(
        postgres_conn_id=upstream_conn_id, default_statement_timeout=10.0
    )
    downstream_pg = PostgresHook(
        postgres_conn_id=downstream_conn_id, default_statement_timeout=10.0
    )

    query = "SELECT * FROM {table} LIMIT 0;"
    handler = lambda cursor: {desc[0] for desc in cursor.description}  # noqa: E731

    upstream_cols = upstream_pg.run(
        query.format(table=upstream_table_name), handler=handler
    )

    downstream_cols = downstream_pg.run(
        query.format(table=downstream_table_name), handler=handler
    )

    return list(upstream_cols.intersection(downstream_cols))


@task
def create_fdw_extension(downstream_conn_id: str):
    downstream_pg = PostgresHook(
        postgres_conn_id=downstream_conn_id, default_statement_timeout=10.0
    )

    # Create the FDW if it doesn't exist
    try:
        downstream_pg.run(queries.CREATE_FDW_EXTENSION_QUERY)
    except Exception as e:
        # TODO
        logger.error(e)
        logger.error("Extension already exists, possible race condition")


@task
def initialize_fdw(
    upstream_conn_id: str,
    downstream_conn_id: str,
    table_name: str,
    task: AbstractOperator = None,
):
    """
    table_name: str name of the table that will be copied via this FDW.

    Create an FDW extension if it does not exist and prepare it for copying.
    """

    # Initialize the FDW from the upstream DB to the downstream DB.
    # The FDW is used when copying data. It creates a new schema named
    # upstream in the downstream DB through which the upstream table
    # can be accessed.

    upstream_connection = Connection.get_connection_from_secrets(upstream_conn_id)

    _run_sql.function(
        postgres_conn_id=downstream_conn_id,
        sql_template=queries.CREATE_FDW_QUERY,
        task=task,
        # timeout,
        # handler
        host=upstream_connection.host,
        port=upstream_connection.port,
        dbname=upstream_connection.schema,
        user=upstream_connection.login,
        password=upstream_connection.password,
        table_name=table_name,
    )


@task
def get_record_limit():
    """
    Check and retrieve the limit of records to ingest for the environment in which
    Airflow is running.

    If a limit is explicitly configured, it is always used. Otherwise, production
    defaults to no limit, and all other environments default to 100,000.
    """
    if configured_limit := Variable.get(
        "DATA_REFRESH_LIMIT", default_var=None, deserialize_json=True
    ):
        return configured_limit

    # Note this is different from the target environment of the data refresh DAG;
    # instead, it is the environment in which Airflow is running (local testing
    # vs the production catalog). TODO should this be changed?
    environment = Variable.get("ENVIRONMENT", default_var="local")
    if environment == PRODUCTION:
        # Never limit the record count in production.
        return None

    # Default for non-production environments where no limit has explicitly
    # been set.
    return 100_000


@task
def copy_data(
    postgres_conn_id: str,
    limit: int | None,
    table_name: str,
    temp_table_name: str,
    columns: list[str],
    task: AbstractOperator = None,
):
    sql_template = queries.ADVANCED_COPY_DATA_QUERY

    # If a limit is configured, add the appropriate conditions onto the
    # select/insert
    if limit:
        sql_template += dedent(
            """
            ORDER BY identifier
            LIMIT {limit};
            """
        )

    return _run_sql.function(
        postgres_conn_id=postgres_conn_id,
        sql_template=sql_template,
        task=task,
        temp_table_name=temp_table_name,
        columns=", ".join(columns),
        upstream_table_name=table_name,
        deleted_table_name=f"api_deleted{table_name}",
        limit=limit,
    )


@task_group(group_id="copy_upstream_table")
def copy_upstream_table(
    environment: Environment, data_refresh_config: DataRefreshConfig
):
    downstream_conn_id = POSTGRES_API_CONN_IDS.get(environment)
    upstream_conn_id = POSTGRES_CONN_ID

    table_name = SQL_INFO_BY_MEDIA_TYPE.get(data_refresh_config.media_type).media_table
    temp_table_name = f"temp_import_{table_name}"

    shared_cols = get_shared_columns(
        upstream_conn_id=upstream_conn_id,
        downstream_conn_id=downstream_conn_id,
        upstream_table_name=table_name,
        downstream_table_name=table_name,
    )

    create_fdw = create_fdw_extension(downstream_conn_id=downstream_conn_id)

    init_fdw = initialize_fdw(
        upstream_conn_id=upstream_conn_id,
        downstream_conn_id=downstream_conn_id,
        table_name=table_name,
    )

    limit = get_record_limit()

    create_temp_table = _run_sql.override(task_id="create_temp_table")(
        postgres_conn_id=downstream_conn_id,
        sql_template=queries.CREATE_TEMP_TABLE_QUERY,
        # timeout,
        temp_table_name=temp_table_name,
        downstream_table_name=table_name,
    )

    setup_id_columns = _run_sql.override(task_id="setup_id_columns")(
        postgres_conn_id=downstream_conn_id,
        sql_template=queries.ID_COLUMN_SETUP_QUERY,
        # timeout,
        temp_table_name=temp_table_name,
    )

    setup_tertiary_columns = _run_sql.override(task_id="setup_tertiary_columns")(
        postgres_conn_id=downstream_conn_id,
        sql_template=queries.METRIC_COLUMN_SETUP_QUERY,
        # timeout,
        temp_table_name=temp_table_name,
    )

    copy = copy_data.override(execution_timeout=data_refresh_config.copy_data_timeout)(
        postgres_conn_id=downstream_conn_id,
        limit=limit,
        table_name=table_name,
        temp_table_name=temp_table_name,
        columns=shared_cols,
    )

    add_primary_key = _run_sql.override(task_id="add_primary_key")(
        postgres_conn_id=downstream_conn_id,
        sql_template=queries.ADD_PRIMARY_KEY_QUERY,
        # timeout,
        temp_table_name=temp_table_name,
    )

    drop_fdw = _run_sql.override(task_id="drop_fdw")(
        postgres_conn_id=downstream_conn_id,
        sql_template=queries.DROP_SERVER_QUERY,
        # timeout,
    )

    # TODO: This will be moved into the `promote` TaskGroup eventually. This is
    # a temporary task to prevent dangling temp_tables while testing locally.
    drop_temp_table = _run_sql.override(task_id="drop_temp_table")(
        postgres_conn_id=downstream_conn_id,
        sql_template=f"DROP TABLE {temp_table_name};",
        # timeout,
    )

    # Set up dependencies
    create_fdw >> init_fdw >> copy

    create_temp_table >> setup_id_columns >> setup_tertiary_columns
    setup_tertiary_columns >> copy
    copy >> add_primary_key >> drop_fdw >> drop_temp_table
    return

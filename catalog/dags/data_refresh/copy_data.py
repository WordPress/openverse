"""
# Copy Data TaskGroup

This module contains the Airflow tasks used for copying upstream (Catalog)
tables into new temporary tables in the downstream (API) database. This
is one of the initial steps of the data refresh. These temporary tables
will later be used to create new Elasticsearch indices, and ultimately
will be promoted to the live media tables in the API.

"""

import logging
from dataclasses import asdict
from datetime import timedelta
from textwrap import dedent

from airflow.decorators import task, task_group
from airflow.models import Variable
from airflow.models.abstractoperator import AbstractOperator
from airflow.models.connection import Connection

from common.constants import (
    POSTGRES_API_CONN_IDS,
    POSTGRES_CONN_ID,
    PRODUCTION,
    Environment,
)
from common.sql import PostgresHook, run_sql
from data_refresh import queries
from data_refresh.data_refresh_types import DataRefreshConfig


logger = logging.getLogger(__name__)


DEFAULT_DATA_REFRESH_LIMIT = 10_000


@task(max_active_tis_per_dagrun=1)
def initialize_fdw(
    upstream_conn_id: str,
    downstream_conn_id: str,
    media_type: str,
    task: AbstractOperator = None,
):
    """Create the FDW and prepare it for copying."""
    upstream_connection = Connection.get_connection_from_secrets(upstream_conn_id)
    fdw_name = f"upstream_{media_type}"

    run_sql.function(
        postgres_conn_id=downstream_conn_id,
        sql_template=queries.CREATE_FDW_QUERY,
        task=task,
        fdw_name=fdw_name,
        host=upstream_connection.host,
        port=upstream_connection.port,
        dbname=upstream_connection.schema,
        user=upstream_connection.login,
        password=upstream_connection.password,
    )

    return fdw_name


@task(
    max_active_tis_per_dagrun=1,
    map_index_template="{{ task.op_kwargs['upstream_table_name'] }}",
)
def create_schema(
    downstream_conn_id: str, upstream_table_name: str, fdw_name: str
) -> str:
    """
    Create a new schema in the downstream DB through which the upstream table
    can be accessed. Returns the schema name.
    """
    downstream_pg = PostgresHook(
        postgres_conn_id=downstream_conn_id, default_statement_timeout=10.0
    )

    schema_name = f"upstream_{upstream_table_name}_schema"
    downstream_pg.run(
        queries.CREATE_SCHEMA_QUERY.format(
            fdw_name=fdw_name,
            schema_name=schema_name,
            upstream_table_name=upstream_table_name,
        ),
        handler=None,
    )
    return schema_name


@task
def get_record_limit() -> int | None:
    """
    Check and retrieve the limit of records to ingest for the environment in which
    Airflow is running.

    If a limit is explicitly configured, it is always used. Otherwise, production
    defaults to no limit, and all other environments default to 10,000.
    """
    try:
        # If a limit is explicitly configured, always use it.
        return Variable.get("DATA_REFRESH_LIMIT", deserialize_json=True)
    except KeyError:
        # Defaults when no limit is explicitly configured.
        # Note `environment` differs from the target env of the data refresh DAG;
        # instead, it is the environment in which Airflow is running (local testing
        # vs the production catalog).
        environment = Variable.get("ENVIRONMENT", default_var="local")
        if environment == PRODUCTION:
            # Never limit the record count in production.
            return None

        return DEFAULT_DATA_REFRESH_LIMIT


@task(
    max_active_tis_per_dagrun=1,
    map_index_template="{{ task.op_kwargs['upstream_table_name'] }}",
)
def get_shared_columns(
    upstream_conn_id: str,
    downstream_conn_id: str,
    upstream_table_name: str,
    downstream_table_name: str,
) -> list[str]:
    """Get a list of column identifiers shared between two tables."""
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


@task(
    # Ensure that only one table is being copied at a time.
    max_active_tis_per_dagrun=1,
    map_index_template="{{ task.op_kwargs['upstream_table_name'] }}",
)
def copy_data(
    postgres_conn_id: str,
    limit: int | None,
    sql_template: str,
    temp_table_name: str,
    schema_name: str,
    upstream_table_name: str,
    deleted_table_name: str,
    columns: list[str],
    task: AbstractOperator = None,
):
    """Copy data from the upstream table into the downstream temp table."""
    # If a limit is configured, add the appropriate conditions onto the
    # select/insert
    if limit:
        if "identifier" in columns:
            sql_template += dedent(
                """
                ORDER BY identifier"""
            )
        sql_template += dedent(
            """
        LIMIT {limit};"""
        )

    return run_sql.function(
        postgres_conn_id=postgres_conn_id,
        sql_template=sql_template,
        task=task,
        temp_table_name=temp_table_name,
        columns=", ".join(columns),
        schema_name=schema_name,
        upstream_table_name=upstream_table_name,
        deleted_table_name=deleted_table_name,
        limit=limit,
    )


@task_group(group_id="copy_upstream_table")
def copy_upstream_table(
    upstream_conn_id: str,
    downstream_conn_id: str,
    fdw_name: str,
    copy_timeout: timedelta,
    primary_key_timeout: timedelta,
    limit: int,
    upstream_table_name: str,
    downstream_table_name: str,
    tertiary_column_query: str,
    copy_data_query: str,
    temp_table_name: str,
    deleted_table_name: str,
):
    """
    Copy an individual table from the upstream DB into a new temporary table
    in the downstream DB.
    """
    shared_cols = get_shared_columns(
        upstream_conn_id=upstream_conn_id,
        downstream_conn_id=downstream_conn_id,
        upstream_table_name=upstream_table_name,
        downstream_table_name=downstream_table_name,
    )

    schema = create_schema(
        downstream_conn_id=downstream_conn_id,
        upstream_table_name=upstream_table_name,
        fdw_name=fdw_name,
    )

    create_temp_table = run_sql.override(
        task_id="create_temp_table",
        map_index_template="{{ task.op_kwargs['temp_table_name'] }}",
    )(
        postgres_conn_id=downstream_conn_id,
        sql_template=queries.CREATE_TEMP_TABLE_QUERY,
        temp_table_name=temp_table_name,
        downstream_table_name=downstream_table_name,
    )

    setup_id_columns = run_sql.override(
        task_id="setup_id_columns",
        map_index_template="{{ task.op_kwargs['temp_table_name'] }}",
    )(
        postgres_conn_id=downstream_conn_id,
        sql_template=queries.ID_COLUMN_SETUP_QUERY,
        temp_table_name=temp_table_name,
    )

    setup_tertiary_columns = run_sql.override(
        task_id="setup_tertiary_columns",
        map_index_template="{{ task.op_kwargs['temp_table_name'] }}",
    )(
        postgres_conn_id=downstream_conn_id,
        sql_template=tertiary_column_query,
        temp_table_name=temp_table_name,
    )

    copy = copy_data.override(execution_timeout=copy_timeout)(
        postgres_conn_id=downstream_conn_id,
        limit=limit,
        sql_template=copy_data_query,
        temp_table_name=temp_table_name,
        schema_name=schema,
        upstream_table_name=upstream_table_name,
        deleted_table_name=deleted_table_name,
        columns=shared_cols,
    )

    add_primary_key = run_sql.override(
        task_id="add_primary_key",
        map_index_template="{{ task.op_kwargs['temp_table_name'] }}",
        execution_timeout=primary_key_timeout,
    )(
        postgres_conn_id=downstream_conn_id,
        sql_template=queries.ADD_PRIMARY_KEY_QUERY,
        temp_table_name=temp_table_name,
    )

    create_temp_table >> setup_id_columns >> setup_tertiary_columns
    setup_tertiary_columns >> copy
    copy >> add_primary_key

    return


@task_group(group_id="copy_upstream_tables")
def copy_upstream_tables(
    target_environment: Environment, data_refresh_config: DataRefreshConfig
):
    """
    For each upstream table associated with the given media type, create a new
    temp table in the downstream DB and copy all the upstream data into it.
    These temp tables will later replace the main media tables in the API.

    This task does _not_ apply all indices and constraints, merely copies
    the data.
    """
    downstream_conn_id = POSTGRES_API_CONN_IDS.get(target_environment)
    upstream_conn_id = POSTGRES_CONN_ID

    create_fdw = run_sql.override(task_id="create_fdw")(
        postgres_conn_id=downstream_conn_id,
        sql_template=queries.CREATE_FDW_EXTENSION_QUERY,
    )

    init_fdw = initialize_fdw(
        upstream_conn_id=upstream_conn_id,
        downstream_conn_id=downstream_conn_id,
        media_type=data_refresh_config.media_type,
    )

    limit = get_record_limit()

    # Copy all tables mapped for this media type
    copy_tables = copy_upstream_table.partial(
        upstream_conn_id=upstream_conn_id,
        downstream_conn_id=downstream_conn_id,
        fdw_name=init_fdw,
        copy_timeout=data_refresh_config.copy_data_timeout,
        primary_key_timeout=data_refresh_config.add_primary_key_timeout,
        limit=limit,
    ).expand_kwargs([asdict(tm) for tm in data_refresh_config.table_mappings])

    drop_fdw = run_sql.override(task_id="drop_fdw")(
        postgres_conn_id=downstream_conn_id,
        sql_template=queries.DROP_SERVER_QUERY,
        fdw_name=init_fdw,
    )

    # Set up dependencies
    create_fdw >> init_fdw >> copy_tables >> drop_fdw

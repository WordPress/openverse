from textwrap import dedent

from psycopg2.sql import SQL, Identifier
from psycopg2.sql import Literal as PgLiteral

from ingestion_server.constants.internal_types import ApproachType


def get_existence_queries(model: str, table: str = None) -> tuple[SQL, SQL]:
    """
    Get the query for checking whether a media is deleted or mature.

    Returns two SQL queries for checking if an identifier exists in the deleted or the
    mature tables for the media respectively. The media tables are assumed to be named
    with the prefixes "api_deleted" and "api_mature" respectively.

    :param model: the name to use for the deleted and mature tables
    :param table: the name of the media table to check entries in
    :return: the queries to check if for presence in the deleted/mature table
    """

    if not table:
        table = model  # By default, tables are named after the model.

    exists_in_table = (
        "EXISTS(SELECT 1 FROM {table} " "WHERE identifier = {identifier}) AS {name}"
    )
    exists_in_deleted_table = SQL(exists_in_table).format(
        table=Identifier(f"api_deleted{model}"),
        identifier=Identifier(table, "identifier"),
        name=Identifier("deleted"),
    )
    exists_in_mature_table = SQL(exists_in_table).format(
        table=Identifier(f"api_mature{model}"),
        identifier=Identifier(table, "identifier"),
        name=Identifier("mature"),
    )
    return exists_in_deleted_table, exists_in_mature_table


def get_create_ext_query():
    """
    Get the query for creating the ``postgres_fdw`` extension, if it does not exist.

    :return: the SQL query for creating the FDW extension
    """

    return SQL("CREATE EXTENSION IF NOT EXISTS postgres_fdw;")


def get_fdw_query(
    host: str, port: int, dbname: str, user: str, password: str, table: str
):
    """
    Get the query for creating a new FDW from the upstream DB to the downstream DB.

    This FDW will be used when copying data. It creates a new schema named "upstream"
    in the downstream DB through which the upstream table can be accessed.

    :param host: the hostname of the upstream DB relative to the downstream
    :param port: the exposed port of the upstream DB accessible from downstream
    :param dbname: the name of the upstream database
    :param user: the user name with access to the upstream database
    :param password: the password of the given ``user``
    :param table: the table name to copy via this FDW
    :return: the SQL query for creating a new FDW
    """

    return SQL(
        """
        DROP SERVER IF EXISTS upstream CASCADE;
        CREATE SERVER upstream FOREIGN DATA WRAPPER postgres_fdw
          OPTIONS (host {host}, dbname {dbname}, port {port});

        CREATE USER MAPPING IF NOT EXISTS FOR deploy SERVER upstream
          OPTIONS (user {user}, password {password});

        DROP SCHEMA IF EXISTS upstream_schema CASCADE;
        CREATE SCHEMA upstream_schema AUTHORIZATION deploy;

        IMPORT FOREIGN SCHEMA public LIMIT TO ({table})
          FROM SERVER upstream INTO upstream_schema;
    """
    ).format(
        host=PgLiteral(host),
        port=PgLiteral(str(port)),
        dbname=PgLiteral(dbname),
        user=PgLiteral(user),
        password=PgLiteral(password),
        table=Identifier(table),
    )


def get_copy_data_query(
    upstream_table: str,
    downstream_table: str,
    columns: list[str],
    approach: ApproachType,
    limit: int | None = 100_000,
):
    """
    Get the query for copying data from an upstream table to a temp downstream table.

    This temporary table in the downstream DB will eventually replace the permanent one.
    This query uses the "temp_import_" prefix on the temporary table and avoids entries
    from the deleted table with the "api_deleted" prefix. After the copying process,
    the "upstream" schema is dropped and the FDW is closed.

    When running this on a non-production environment, the results will be ordered
    by `identifier` to simulate a random sample and only the first 100k records
    will be pulled from the upstream database.

    :param upstream_table: the name of the upstream table being copied
    :param downstream_table: the name of the downstream table being replaced
    :param columns: the names of the columns to copy from upstream
    :param approach: whether to use advanced logic specific to media ingestion
    :param limit: number of rows to copy when
    :return: the SQL query for copying the data
    """

    table_creation = dedent(
        """
    DROP TABLE IF EXISTS {temp_table};
    CREATE TABLE {temp_table} (LIKE {downstream_table} INCLUDING DEFAULTS
        INCLUDING CONSTRAINTS);
    """
    )

    id_column_setup = dedent(
        """
    ALTER TABLE {temp_table} ADD COLUMN IF NOT EXISTS
        id serial;
    CREATE TEMP SEQUENCE IF NOT EXISTS id_temp_seq;
    ALTER TABLE {temp_table} ALTER COLUMN
        id SET DEFAULT nextval('id_temp_seq'::regclass);
    """
    )

    timestamp_column_setup = dedent(
        """
    ALTER TABLE {temp_table} ALTER COLUMN
        created_on SET DEFAULT CURRENT_TIMESTAMP;
    ALTER TABLE {temp_table} ALTER COLUMN
        updated_on SET DEFAULT CURRENT_TIMESTAMP;
    """
    )

    metric_column_setup = dedent(
        """
    ALTER TABLE {temp_table} ADD COLUMN IF NOT EXISTS
        standardized_popularity double precision;
    ALTER TABLE {temp_table} ALTER COLUMN
        view_count SET DEFAULT 0;
    """
    )

    conclusion = dedent(
        """
    ALTER TABLE {temp_table} ADD PRIMARY KEY (id);
    DROP SERVER upstream CASCADE;
    """
    )

    if approach == "basic":
        tertiary_column_setup = timestamp_column_setup
        select_insert = dedent(
            """
        INSERT INTO {temp_table} ({columns}) SELECT {columns} FROM {upstream_table}
        """
        )
    else:  # approach == 'advanced'
        tertiary_column_setup = metric_column_setup
        select_insert = dedent(
            """
        INSERT INTO {temp_table} ({columns})
            SELECT {columns}
            FROM {upstream_table} AS u
            WHERE NOT EXISTS(
                SELECT FROM {deleted_table} WHERE identifier = u.identifier
            )
        """
        )

    # If a limit is requested, add the condition onto the select at the very end
    if limit:
        select_insert += "    LIMIT {limit}"

    # Always add a semi-colon at the end
    select_insert += ";"

    steps = [
        table_creation,
        id_column_setup,
        tertiary_column_setup,
        select_insert,
        conclusion,
    ]

    return SQL("".join(steps)).format(
        downstream_table=Identifier(downstream_table),
        temp_table=Identifier(f"temp_import_{downstream_table}"),
        upstream_table=Identifier("upstream_schema", upstream_table),
        deleted_table=Identifier(f"api_deleted{downstream_table}"),
        columns=SQL(",").join([Identifier(col) for col in columns]),
        limit=PgLiteral(limit),
    )


def get_go_live_query(table: str, index_mapping: dict[str, str]):
    """
    Get the query for replacing the old table with new temporary table.

    The temporary table with the "temp_import_" prefix replaces the un-prefixed
    old table.

    :param table: the name of the old table being replaced with the temp
    :return: the SQL query for replacing the old table with new temporary table
    """
    alters = [
        SQL("ALTER INDEX {new} RENAME TO {old};").format(
            new=Identifier(new), old=Identifier(old)
        )
        for new, old in index_mapping.items()
    ]

    return SQL(
        """
        DROP TABLE {table};
        {alters}
        ALTER TABLE {temp_table} RENAME TO {table};
    """
    ).format(
        table=Identifier(table),
        alters=SQL("\n        ").join(alters),
        temp_table=Identifier(f"temp_import_{table}"),
    )

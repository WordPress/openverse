from psycopg2.sql import SQL, Identifier, Literal


def get_existence_queries(table):
    """
    Get the query for checking whether an identifier exists in the deleted or
    the mature tables for the media. The media tables are assumed to be named
    with the prefixes "api_deleted" and "api_mature" respectively.

    :param table: the name of the media table to check entries in
    :return: the queries to check if for presence in the deleted/mature table
    """

    exists_in_table = (
        'EXISTS(SELECT 1 FROM {table} '
        'WHERE identifier = {identifier}) AS {name}'
    )
    exists_in_deleted_table = SQL(exists_in_table).format(
        table=Identifier(f'api_deleted{table}'),
        identifier=Identifier(table, "identifier"),
        name=Identifier('deleted'),
    )
    exists_in_mature_table = SQL(exists_in_table).format(
        table=Identifier(f'api_mature{table}'),
        identifier=Identifier(table, "identifier"),
        name=Identifier('mature'),
    )
    return exists_in_deleted_table, exists_in_mature_table


def get_fdw_query(host: str, port: int,
                  dbname: str, user: str, password: str,
                  table: str):
    """
    Get the query for creating a new FDW to be used when copying data from the
    upstream DB to the downstream DB. It creates a new schema named "upstream"
    in which the upstream table can be accessed.

    :param host: the hostname of the upstream DB relative to the downstream
    :param port: the exposed port of the upstream DB accessible from downstream
    :param dbname: the name of the upstream database
    :param user: the user name with access to the upstream database
    :param password: the password of the given ``user``
    :param table: the table name to copy via this FDW
    :return: the SQL query for creating a new FDW
    """

    return SQL('''
        CREATE EXTENSION IF NOT EXISTS postgres_fdw;

        DROP SERVER IF EXISTS upstream CASCADE;
        CREATE SERVER upstream FOREIGN DATA WRAPPER postgres_fdw
          OPTIONS (host {host}, dbname {dbname}, port {port});

        CREATE USER MAPPING IF NOT EXISTS FOR deploy SERVER upstream
          OPTIONS (user {user}, password {password});

        DROP SCHEMA IF EXISTS upstream_schema CASCADE;
        CREATE SCHEMA upstream_schema AUTHORIZATION deploy;

        IMPORT FOREIGN SCHEMA public LIMIT TO ({table})
          FROM SERVER upstream INTO upstream_schema;
    ''').format(
        host=Literal(host),
        port=Literal(str(port)),
        dbname=Literal(dbname),
        user=Literal(user),
        password=Literal(password),
        table=Identifier(table),
    )


def get_copy_data_query(table: str, columns: list[str]):
    """
    Get the query for copying data from the upstream table to a temporary table
    in the downstream database. This temporary table will replace the permanent
    one later on. This query uses the "temp_import_" prefix on the temporary
    table and avoids entries from the deleted table with the "api_deleted"
    prefix. After the copying process, the "upstream" schema is dropped.

    :table: the name of the downstream table being replaced
    :columns: the names of the columns to copy from upstream
    """

    return SQL('''
        DROP TABLE IF EXISTS {temp_table};
        CREATE TABLE {temp_table} (LIKE {table} INCLUDING CONSTRAINTS);
        CREATE TEMP SEQUENCE IF NOT EXISTS id_temp_seq;

        ALTER TABLE {temp_table} ADD COLUMN IF NOT EXISTS
          standardized_popularity double precision;
        ALTER TABLE {temp_table} ADD COLUMN IF NOT EXISTS
          id serial;
        ALTER TABLE {temp_table} ALTER COLUMN
          view_count SET DEFAULT 0;
        ALTER TABLE {temp_table} ALTER COLUMN
          id SET DEFAULT nextval('id_temp_seq'::regclass);

        INSERT INTO {temp_table} ({columns})
          SELECT {columns} from {upstream_table} AS u
          WHERE NOT EXISTS(
            SELECT FROM {deleted_table} WHERE identifier = u.identifier
          );

        ALTER TABLE {temp_table} ADD PRIMARY KEY (id);

        DROP SERVER upstream CASCADE;
    ''').format(
        table=Identifier(table),
        temp_table=Identifier(f'temp_import_{table}'),
        upstream_table=Identifier('upstream_schema', f'{table}_view'),
        deleted_table=Identifier(f'api_deleted{table}'),
        columns=SQL(',').join([Identifier(col) for col in columns]),
    )


def get_go_live_query(table: str):
    """
    Get the query for replacing the old table with new temporary table. The
    temporary table with the "temp_import_" prefix replaces the un-prefixed
    old table.

    :param table: the name of the old table being replaced with the temp
    :return: the SQL query for replacing the old table with new temporary table
    """

    return SQL('''
        DROP TABLE {table};
        ALTER TABLE {temp_table} RENAME TO {table};
    ''').format(
        table=Identifier(table),
        temp_table=Identifier(f'temp_import_{table}'),
    )

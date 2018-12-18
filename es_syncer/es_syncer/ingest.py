import os
import psycopg2
import datetime
import logging as log
from es_syncer.indexer import database_connect

"""
Copy updates from the intermediary database to the API database.
"""

UPSTREAM_DB_HOST = os.environ.get('UPSTREAM_DB_HOST', 'upstream_db')
UPSTREAM_DB_PORT = os.environ.get('UPSTREAM_DB_PORT', 5432)
UPSTREAM_DB_PASSWORD = os.environ.get('UPSTREAM_DB_PASSWORD', 'deploy')


def _get_shared_cols(conn1, conn2, table):
    """
    Given two database connections and a table name, return the list of columns
    that the two tables have in common.
    """
    with conn1.cursor() as cur1, conn2.cursor() as cur2:
        get_tables = ("SELECT * FROM {} LIMIT 0".format(table))
        cur1.execute(get_tables)
        conn1_cols = set([desc[0] for desc in cur1.description])
        cur2.execute(get_tables)
        conn2_cols = set([desc[0] for desc in cur2.description])
    return list(conn1_cols.intersection(conn2_cols))


def _get_indices(conn, table):
    """
    Using the existing table as a template, generate CREATE INDEX statements for
    the new table.

    :param conn: A connection to the API database.
    :param table: The table to be updated.
    :return: A list of CREATE INDEX statements.
    """
    def _clean_idxs(indices):
        # Remove names of indices. We don't want to collide with the old names;
        # we want the database to generate them for us upon recreating the
        # table.
        cleaned = []
        for index in indices:
            # The index name is always after CREATE [UNIQUE] INDEX; delete it.
            tokens = index[0].split(' ')
            index_idx = tokens.index('INDEX')
            del tokens[index_idx + 1]
            # The table name is always after ON. Rename it to match the
            # temporary copy of the data.
            on_idx = tokens.index('ON')
            table_name_idx = on_idx + 1
            schema_name, table_name = tokens[table_name_idx].split('.')
            new_table_name = 'temp_import_{}'.format(table_name)
            tokens[table_name_idx] = schema_name + '.' + new_table_name
            cleaned.append(' '.join(tokens))

        return cleaned

    # Get all of the old indices from the existing table.
    get_idxs = "SELECT indexdef FROM pg_indexes WHERE tablename = '{}'"\
        .format(table)

    with conn.cursor() as cur:
        cur.execute(get_idxs)
        idxs = cur.fetchall()
    cleaned_idxs = _clean_idxs(idxs)
    return cleaned_idxs


def get_upstream_updates(table, progress, finish_time):
    """
    Import updates from the upstream CC Catalog database into the API.

    :param table: The upstream table to copy.
    :param progress: multiprocessing.Value float for sharing task progress
    :param finish_time: multiprocessing.Value int for sharing finish timestamp
    :return:
    """
    downstream_db = database_connect()
    upstream_db = psycopg2.connect(
        dbname='openledger',
        user='deploy',
        port=UPSTREAM_DB_PORT,
        password=UPSTREAM_DB_PASSWORD,
        host=UPSTREAM_DB_HOST,
        connect_timeout=5
    )
    query_cols = ','.join(_get_shared_cols(downstream_db, upstream_db, table))
    upstream_db.close()
    # Connect to upstream database and create references to foreign tables.
    log.info('(Re)initializing foreign data wrapper')
    init_fdw = '''
        CREATE EXTENSION IF NOT EXISTS postgres_fdw;
        DROP SERVER IF EXISTS upstream CASCADE;
        CREATE SERVER upstream FOREIGN DATA WRAPPER postgres_fdw
        OPTIONS (host '{host}', dbname 'openledger', port '{port}');

        CREATE USER MAPPING IF NOT EXISTS FOR deploy SERVER upstream
        OPTIONS (user 'deploy', password '{passwd}');
        DROP SCHEMA IF EXISTS upstream_schema CASCADE;
        CREATE SCHEMA upstream_schema AUTHORIZATION deploy;

        IMPORT FOREIGN SCHEMA public
        LIMIT TO ({table}) FROM SERVER upstream INTO upstream_schema;
    '''.format(host=UPSTREAM_DB_HOST, passwd=UPSTREAM_DB_PASSWORD, table=table,
               port=UPSTREAM_DB_PORT)
    # 1. Import data into a temporary table
    # 2. Recreate indices from the original table
    # 3. Promote the temporary table and delete the original.
    copy_data = '''
        DROP TABLE IF EXISTS temp_import_{table};
        CREATE TABLE temp_import_{table} (LIKE {table} INCLUDING CONSTRAINTS);
        INSERT INTO temp_import_{table} ({cols})
        SELECT {cols} from upstream_schema.{table};
    '''.format(table=table, cols=query_cols)
    create_index_statements = ';\n'.join(_get_indices(downstream_db, table))

    go_live = '''
        DROP TABLE {table};
        ALTER TABLE temp_import_{table} RENAME TO {table};
    '''.format(table=table)

    with downstream_db.cursor() as downstream_cur:
        log.info('Copying upstream data...')
        downstream_cur.execute(init_fdw)
        downstream_cur.execute(copy_data)
        log.info('Copying finished! Recreating database indices...')
        progress.value = 70.0
        downstream_cur.execute(create_index_statements)
        log.info('Done creating indices! Going live...')
        downstream_cur.execute(go_live)
    downstream_db.commit()
    downstream_db.close()

    if progress is not None:
        progress.value = 100.0
    if finish_time is not None:
        finish_time.value = datetime.datetime.utcnow().timestamp()
    return

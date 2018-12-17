import os
import psycopg2
import datetime
import logging as log
from es_syncer.indexer import database_connect

"""
Copy updates from the intermediary database to the API database.
"""

UPSTREAM_DB_HOST = os.environ.get('UPSTREAM_DB_HOST', 'localhost')
UPSTREAM_DB_PORT = os.environ.get('UPSTREAM_DB_PORT', 5432)
UPSTREAM_DB_PASSWORD = os.environ.get('UPSTREAM_DB_PASSWORD', 'deploy')


def _get_shared_cols(conn1, conn2, table_name):
    """
    Given two database connections and a table name, return the list of columns
    that the two tables have in common.
    """
    with conn1.cursor() as cur1, conn2.cursor() as cur2:
        get_tables = ("SELECT * FROM {} LIMIT 0".format(table_name))
        cur1.execute(get_tables)
        conn1_cols = set([desc[0] for desc in cur1.description])
        cur2.execute(get_tables)
        conn2_cols = set([desc[0] for desc in cur2.description])
    return list(conn1_cols.intersection(conn2_cols))


def get_upstream_updates(table, progress, finish_time):
    """
    Import updates from the upstream CC Catalog database into the API.

    :param table: The upstream table to copy.
    :param progress: Interprocess variable for sharing task progress
    :param finish_time: Interprocess variable for sharing finish time
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
    from remote_pdb import RemotePdb
    RemotePdb('127.0.0.1', 4444).set_trace()
    # Connect to upstream server and create references to foreign tables.
    log.info('(Re)initializing foreign data wrapper')
    init_fdw = '''
        CREATE EXTENSION IF NOT EXISTS postgres_fdw;
        CREATE SERVER IF NOT EXISTS upstream FOREIGN DATA WRAPPER postgres_fdw
        OPTIONS (host '{host}', dbname 'openledger', port '5432');

        CREATE USER MAPPING FOR deploy SERVER upstream
        OPTIONS (user 'deploy', password '{passwd}');
        CREATE SCHEMA IF NOT EXISTS upstream_schema AUTHORIZATION deploy;

        IMPORT FOREIGN SCHEMA public
        LIMIT TO ({table}) FROM SERVER upstream INTO upstream_schema;
    '''.format(host=UPSTREAM_DB_HOST, passwd=UPSTREAM_DB_PASSWORD, table=table)
    log.info('Copying upstream data. This may take a while.')
    copy_data = '''
        CREATE TABLE importing_{table} (LIKE {table});
        INSERT INTO importing_{table} ({cols})
        SELECT {cols} from upstream_schema.{table};
    '''.format(table=table, cols=query_cols)

    with downstream_db.cursor() as downstream_cur:
        downstream_cur.execute(init_fdw)
        downstream_cur.execute(copy_data)
    downstream_db.commit()
    downstream_db.close()
    # Postgres doesn't offer progress estimates, so the best we can do is notify
    # the calling process that the task has finished.
    if progress is not None:
        progress.value = 100.0
    if finish_time is not None:
        finish_time.value = datetime.datetime.utcnow().timestamp()

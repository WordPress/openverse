import os
import psycopg2
import time
import logging as log
import io
from es_syncer.indexer import database_connect, DB_BUFFER_SIZE

"""
Copy updates from the intermediary database to the API database.
"""

UPSTREAM_DB_HOST = os.environ.get('UPSTREAM_DB_HOST', 'localhost')
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
    return conn1_cols.intersection(conn2_cols)


def consume(table, since_date):
    """
    Import updates from the upstream CC Catalog database into the API.

    :param table: The upstream table to copy.
    :param since_date: Copy data from upstream updated after this date.
    :return:
    """
    downstream_db = database_connect()
    upstream_db = psycopg2.connect(
        dbname='openledger',
        user='deploy',
        password=UPSTREAM_DB_PASSWORD,
        host=UPSTREAM_DB_HOST,
        connect_timeout=5
    )
    query_cols = _get_shared_cols(downstream_db, upstream_db, table)
    downstream_db.close()
    upstream_query = 'SELECT {} FROM {} WHERE updated_on >= \'{}\''\
        .format(','.join(query_cols), table, since_date)
    cursor_name = table + '_consume_cursor'
    with upstream_db.cursor(name=cursor_name) as upstream_cur:
        upstream_cur.itersize = DB_BUFFER_SIZE
        upstream_cur.execute(upstream_query)
        while True:
            dl_start_time = time.time()
            chunk = upstream_cur.fetchmany(upstream_cur.itersize)
            dl_end_time = time.time() - dl_start_time
            dl_rate = len(chunk) / dl_end_time
            if not chunk:
                break
            log.info(
                'PSQL ingest down: batch_size={}, downloaded_per_second={}'
                .format(len(chunk), dl_rate)
            )
            _import(chunk, upstream_cur.description, table)
    upstream_db.close()


def _import(chunk, columns, origin_table):
    """
    Insert a chunk of data into the downstream database.

    :param chunk: A server-side cursor chunk.
    :param columns: The columns from the table schema. Order matters.
    :param origin_table: The name of the original table.
    :return:
    """
    upstream_cols = {idx: col[0] for idx, col in enumerate(columns)}
    downstream_db = database_connect()
    with downstream_db.cursor() as downstream_cur:
        downstream_cols = {
            col[0]: idx for idx, col in enumerate(downstream_cur.description)
        }
        csv_items = io.StringIO()
        for row in chunk:
            csv_row = [None for _ in row]
            for idx, col in enumerate(row):
                col_name = upstream_cols[idx]
                downstream_idx = downstream_cols[col_name]
                csv_row[downstream_idx] = col

    downstream_db.close()

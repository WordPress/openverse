from collections import namedtuple
import os

import psycopg2
import pytest

from util.loader import sql


TEST_ID = 'testing'
POSTGRES_CONN_ID = os.getenv('TEST_CONN_ID')
POSTGRES_TEST_URI = os.getenv('AIRFLOW_CONN_POSTGRES_OPENLEDGER_TESTING')
TEST_LOAD_TABLE = f'provider_image_data{TEST_ID}'


RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'test_resources'
)


@pytest.fixture
def postgres():
    Postgres = namedtuple('Postgres', ['cursor', 'connection'])
    conn = psycopg2.connect(POSTGRES_TEST_URI)
    cur = conn.cursor()
    drop_command = f'DROP TABLE IF EXISTS {TEST_LOAD_TABLE}'
    cur.execute(drop_command)
    conn.commit()
    yield Postgres(cursor=cur, connection=conn)
    cur.execute(drop_command)
    cur.close()
    conn.commit()
    conn.close()


def test_create_if_not_exists_loading_table_creates_table(postgres):
    postgres_conn_id = POSTGRES_CONN_ID
    identifier = TEST_ID
    load_table = TEST_LOAD_TABLE
    sql.create_if_not_exists_loading_table(postgres_conn_id, identifier)

    check_query = (
        f"SELECT EXISTS ("
        f"SELECT FROM pg_tables WHERE tablename='{load_table}');"
    )
    postgres.cursor.execute(check_query)
    check_result = postgres.cursor.fetchone()[0]
    print(check_result)
    assert check_result


def test_create_if_not_exists_errors_if_run_twice_with_same_id(postgres):
    postgres_conn_id = POSTGRES_CONN_ID
    identifier = TEST_ID
    sql.create_if_not_exists_loading_table(postgres_conn_id, identifier)
    with pytest.raises(Exception):
        sql.create_if_not_exists_loading_table(postgres_conn_id, identifier)


def test_create_load_chain_loads_good_tsv(postgres, tmpdir):
    postgres_conn_id = POSTGRES_CONN_ID
    identifier = TEST_ID
    load_table = TEST_LOAD_TABLE
    tsv_file_name = os.path.join(RESOURCES, 'none_missing.tsv')
    with open(tsv_file_name) as f:
        f_data = f.read()

    test_tsv = 'test.tsv'
    path = tmpdir.join(test_tsv)
    path.write(f_data)

    sql.create_if_not_exists_loading_table(postgres_conn_id, identifier)
    sql.import_data_to_intermediate_table(
        postgres_conn_id,
        str(path),
        identifier
    )
    check_query = f"SELECT COUNT (*) FROM {load_table};"
    postgres.cursor.execute(check_query)
    num_rows = postgres.cursor.fetchone()[0]
    assert num_rows == 10

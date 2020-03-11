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

CREATE_LOAD_TABLE_QUERY = (
        f'CREATE TABLE public.{TEST_LOAD_TABLE} ('
        f'foreign_identifier character varying(3000), '
        f'foreign_landing_url character varying(1000), '
        f'url character varying(3000), '
        f'thumbnail character varying(3000), '
        f'width integer, '
        f'height integer, '
        f'filesize character varying(100), '
        f'license character varying(50), '
        f'license_version character varying(25), '
        f'creator character varying(2000), '
        f'creator_url character varying(2000), '
        f'title character varying(5000), '
        f'meta_data jsonb, '
        f'tags jsonb, '
        f'watermarked boolean, '
        f'provider character varying(80), '
        f'source character varying(80)'
        f');'
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


@pytest.fixture
def postgres_with_load_table():
    Postgres = namedtuple('Postgres', ['cursor', 'connection'])
    conn = psycopg2.connect(POSTGRES_TEST_URI)
    cur = conn.cursor()
    drop_command = f'DROP TABLE IF EXISTS {TEST_LOAD_TABLE}'
    cur.execute(drop_command)
    conn.commit()
    create_command = CREATE_LOAD_TABLE_QUERY
    cur.execute(create_command)
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


def test_import_data_loads_good_tsv(postgres_with_load_table, tmpdir):
    postgres_conn_id = POSTGRES_CONN_ID
    identifier = TEST_ID
    load_table = TEST_LOAD_TABLE
    tsv_file_name = os.path.join(RESOURCES, 'none_missing.tsv')
    with open(tsv_file_name) as f:
        f_data = f.read()

    test_tsv = 'test.tsv'
    path = tmpdir.join(test_tsv)
    path.write(f_data)

    sql.import_data_to_intermediate_table(
        postgres_conn_id,
        str(path),
        identifier
    )
    check_query = f'SELECT COUNT (*) FROM {load_table};'
    postgres_with_load_table.cursor.execute(check_query)
    num_rows = postgres_with_load_table.cursor.fetchone()[0]
    assert num_rows == 10


def test_import_data_deletes_null_url_rows(postgres_with_load_table, tmpdir):
    postgres_conn_id = POSTGRES_CONN_ID
    identifier = TEST_ID
    load_table = TEST_LOAD_TABLE
    tsv_file_name = os.path.join(RESOURCES, 'url_missing.tsv')
    with open(tsv_file_name) as f:
        f_data = f.read()

    test_tsv = 'test.tsv'
    path = tmpdir.join(test_tsv)
    path.write(f_data)

    sql.import_data_to_intermediate_table(
        postgres_conn_id,
        str(path),
        identifier
    )
    null_url_check = f'SELECT COUNT (*) FROM {load_table} WHERE url IS NULL;'
    postgres_with_load_table.cursor.execute(null_url_check)
    null_url_num_rows = postgres_with_load_table.cursor.fetchone()[0]
    remaining_row_count = f'SELECT COUNT (*) FROM {load_table};'
    postgres_with_load_table.cursor.execute(remaining_row_count)
    remaining_rows = postgres_with_load_table.cursor.fetchone()[0]

    assert null_url_num_rows == 0
    assert remaining_rows == 2


def test_import_data_deletes_null_license_rows(
        postgres_with_load_table, tmpdir
):
    postgres_conn_id = POSTGRES_CONN_ID
    identifier = TEST_ID
    load_table = TEST_LOAD_TABLE
    tsv_file_name = os.path.join(RESOURCES, 'license_missing.tsv')
    with open(tsv_file_name) as f:
        f_data = f.read()

    test_tsv = 'test.tsv'
    path = tmpdir.join(test_tsv)
    path.write(f_data)

    sql.import_data_to_intermediate_table(
        postgres_conn_id,
        str(path),
        identifier
    )
    license_check = (
        f'SELECT COUNT (*) FROM {load_table} WHERE license IS NULL;'
    )
    postgres_with_load_table.cursor.execute(license_check)
    null_license_num_rows = postgres_with_load_table.cursor.fetchone()[0]
    remaining_row_count = f'SELECT COUNT (*) FROM {load_table};'
    postgres_with_load_table.cursor.execute(remaining_row_count)
    remaining_rows = postgres_with_load_table.cursor.fetchone()[0]

    assert null_license_num_rows == 0
    assert remaining_rows == 2


def test_import_data_deletes_null_foreign_landing_url_rows(
        postgres_with_load_table, tmpdir
):
    postgres_conn_id = POSTGRES_CONN_ID
    identifier = TEST_ID
    load_table = TEST_LOAD_TABLE
    tsv_file_name = os.path.join(RESOURCES, 'foreign_landing_url_missing.tsv')
    with open(tsv_file_name) as f:
        f_data = f.read()

    test_tsv = 'test.tsv'
    path = tmpdir.join(test_tsv)
    path.write(f_data)

    sql.import_data_to_intermediate_table(
        postgres_conn_id,
        str(path),
        identifier
    )
    foreign_landing_url_check = (
        f'SELECT COUNT (*) FROM {load_table} '
        f'WHERE foreign_landing_url IS NULL;'
    )
    postgres_with_load_table.cursor.execute(foreign_landing_url_check)
    null_foreign_landing_url_num_rows = (
        postgres_with_load_table.cursor.fetchone()[0]
    )
    remaining_row_count = f'SELECT COUNT (*) FROM {load_table};'
    postgres_with_load_table.cursor.execute(remaining_row_count)
    remaining_rows = postgres_with_load_table.cursor.fetchone()[0]

    assert null_foreign_landing_url_num_rows == 0
    assert remaining_rows == 3

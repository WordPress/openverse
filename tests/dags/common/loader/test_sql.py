import json
import logging
import os
import time
from collections import namedtuple
from unittest import mock

import psycopg2
import pytest
from airflow.models import TaskInstance
from common.constants import IMAGE
from common.loader import sql
from common.loader.sql import TSV_COLUMNS, create_column_definitions
from common.storage import columns as col
from common.storage.db_columns import IMAGE_TABLE_COLUMNS
from flaky import flaky
from psycopg2.errors import InvalidTextRepresentation


POSTGRES_CONN_ID = os.getenv("TEST_CONN_ID")
POSTGRES_TEST_URI = os.getenv("AIRFLOW_CONN_POSTGRES_OPENLEDGER_TESTING")
S3_LOCAL_ENDPOINT = os.getenv("S3_LOCAL_ENDPOINT")
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
SECRET_KEY = os.getenv("AWS_SECRET_KEY")

RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)), "test_resources")

LOADING_TABLE_COLUMN_DEFINITIONS = create_column_definitions(
    TSV_COLUMNS[IMAGE], is_loading=True
)

CREATE_LOAD_TABLE_QUERY = f"""CREATE TABLE public.{{}} (
  {LOADING_TABLE_COLUMN_DEFINITIONS}
);"""

IMAGE_TABLE_COLUMN_DEFINITIONS = create_column_definitions(IMAGE_TABLE_COLUMNS)

CREATE_IMAGE_TABLE_QUERY = f"""CREATE TABLE public.{{}} (
  {IMAGE_TABLE_COLUMN_DEFINITIONS}
);"""

UNIQUE_CONDITION_QUERY = (
    "CREATE UNIQUE INDEX {table}_provider_fid_idx"
    " ON public.{table}"
    " USING btree (provider, md5(foreign_identifier));"
)


PostgresRef = namedtuple("PostgresRef", ["cursor", "connection"])
ti = mock.Mock(spec=TaskInstance)
ti.xcom_pull.return_value = None

COLUMN_NAMES = [column.db_name for column in IMAGE_TABLE_COLUMNS]

# ids for main database columns
updated_idx = COLUMN_NAMES.index(col.UPDATED_ON.db_name)
ingestion_idx = COLUMN_NAMES.index(col.INGESTION_TYPE.db_name)
provider_idx = COLUMN_NAMES.index(col.PROVIDER.db_name)
source_idx = COLUMN_NAMES.index(col.SOURCE.db_name)
fid_idx = COLUMN_NAMES.index(col.FOREIGN_ID.db_name)
land_url_idx = COLUMN_NAMES.index(col.LANDING_URL.db_name)
url_idx = COLUMN_NAMES.index(col.DIRECT_URL.db_name)
thm_idx = COLUMN_NAMES.index(col.THUMBNAIL.db_name)
filesize_idx = COLUMN_NAMES.index(col.FILESIZE.db_name)
license_idx = COLUMN_NAMES.index(col.LICENSE.db_name)
version_idx = COLUMN_NAMES.index(col.LICENSE_VERSION.db_name)
creator_idx = COLUMN_NAMES.index(col.CREATOR.db_name)
creator_url_idx = COLUMN_NAMES.index(col.CREATOR_URL.db_name)
title_idx = COLUMN_NAMES.index(col.TITLE.db_name)
metadata_idx = COLUMN_NAMES.index(col.META_DATA.db_name)
tags_idx = COLUMN_NAMES.index(col.TAGS.db_name)
synced_idx = COLUMN_NAMES.index(col.LAST_SYNCED.db_name)
removed_idx = COLUMN_NAMES.index(col.REMOVED.db_name)
watermarked_idx = COLUMN_NAMES.index(col.WATERMARKED.db_name)
width_idx = COLUMN_NAMES.index(col.WIDTH.db_name)
height_idx = COLUMN_NAMES.index(col.HEIGHT.db_name)


def create_query_values(
    column_values: dict,
    columns=None,
):
    if columns is None:
        columns = TSV_COLUMNS[IMAGE]
    result = []
    for column in columns:
        val = column_values.get(column.db_name)
        if val is None:
            val = "null"
        else:
            val = f"'{str(val)}'"
        result.append(val)
    return ",".join(result)


@pytest.fixture
def load_table(identifier):
    # Parallelized tests need to use distinct database tables
    return f"provider_data_image_{identifier}"


@pytest.fixture
def postgres(load_table) -> PostgresRef:
    conn = psycopg2.connect(POSTGRES_TEST_URI)
    cur = conn.cursor()
    drop_command = f"DROP TABLE IF EXISTS {load_table}"
    cur.execute(drop_command)
    conn.commit()

    yield PostgresRef(cursor=cur, connection=conn)

    cur.execute(drop_command)
    cur.close()
    conn.commit()
    conn.close()


@pytest.fixture
def postgres_with_load_table(postgres: PostgresRef, load_table) -> PostgresRef:
    create_command = CREATE_LOAD_TABLE_QUERY.format(load_table)
    postgres.cursor.execute(create_command)
    postgres.connection.commit()

    yield postgres


@pytest.fixture
def postgres_with_load_and_image_table(load_table, image_table):
    conn = psycopg2.connect(POSTGRES_TEST_URI)
    cur = conn.cursor()
    drop_load_table_query = f"DROP TABLE IF EXISTS {load_table} CASCADE;"
    drop_image_table_query = f"DROP TABLE IF EXISTS {image_table} CASCADE;"
    drop_image_index_query = f"DROP INDEX IF EXISTS {image_table}_provider_fid_idx;"

    logging.info(f"dropping load table: {drop_load_table_query}")
    logging.info(f"dropping image table: {drop_image_table_query}")
    cur.execute(drop_load_table_query)
    cur.execute(drop_image_table_query)
    cur.execute(drop_image_index_query)
    cur.execute(CREATE_LOAD_TABLE_QUERY.format(load_table))
    cur.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;')
    cur.execute(CREATE_IMAGE_TABLE_QUERY.format(image_table))
    cur.execute(UNIQUE_CONDITION_QUERY.format(table=image_table))

    conn.commit()

    yield PostgresRef(cursor=cur, connection=conn)

    cur.execute(drop_load_table_query)
    cur.execute(drop_image_table_query)
    cur.execute(drop_image_index_query)
    cur.close()
    conn.commit()
    conn.close()


def _load_local_tsv(tmpdir, bucket, tsv_file_name, identifier):
    """
    This wraps sql.load_local_data_to_intermediate_table so we can test it
    under various conditions.
    """
    tsv_file_path = os.path.join(RESOURCES, tsv_file_name)
    with open(tsv_file_path) as f:
        f_data = f.read()

    test_tsv = "test.tsv"
    path = tmpdir.join(test_tsv)
    path.write(f_data)

    sql.load_local_data_to_intermediate_table(POSTGRES_CONN_ID, str(path), identifier)


def _load_s3_tsv(tmpdir, bucket, tsv_file_name, identifier):
    tsv_file_path = os.path.join(RESOURCES, tsv_file_name)
    key = "path/to/object/{tsv_file_name}"
    bucket.upload_file(tsv_file_path, key)
    sql.load_s3_data_to_intermediate_table(
        POSTGRES_CONN_ID, bucket.name, key, identifier
    )


def test_create_loading_table_creates_table(postgres, load_table, identifier):
    postgres_conn_id = POSTGRES_CONN_ID
    sql.create_loading_table(postgres_conn_id, identifier)

    check_query = (
        f"SELECT EXISTS (SELECT FROM pg_tables WHERE tablename='{load_table}');"
    )
    postgres.cursor.execute(check_query)
    check_result = postgres.cursor.fetchone()[0]
    assert check_result


def test_create_loading_table_errors_if_run_twice_with_same_id(postgres, identifier):
    postgres_conn_id = POSTGRES_CONN_ID
    sql.create_loading_table(postgres_conn_id, identifier)
    with pytest.raises(Exception):
        sql.create_loading_table(postgres_conn_id, identifier)


@flaky
@pytest.mark.parametrize("load_function", [_load_local_tsv, _load_s3_tsv])
def test_loaders_load_good_tsv(
    postgres_with_load_table,
    tmpdir,
    empty_s3_bucket,
    load_function,
    load_table,
    identifier,
):
    load_function(tmpdir, empty_s3_bucket, "none_missing.tsv", identifier)
    check_query = f"SELECT COUNT (*) FROM {load_table};"
    postgres_with_load_table.cursor.execute(check_query)
    num_rows = postgres_with_load_table.cursor.fetchone()[0]
    assert num_rows == 10


@pytest.mark.parametrize("load_function", [_load_local_tsv])
def test_delete_less_than_max_malformed_rows(
    postgres_with_load_table,
    tmpdir,
    empty_s3_bucket,
    load_function,
    load_table,
    identifier,
):
    load_function(
        tmpdir, empty_s3_bucket, "malformed_less_than_max_rows.tsv", identifier
    )
    check_query = f"SELECT COUNT (*) FROM {load_table};"
    postgres_with_load_table.cursor.execute(check_query)
    num_rows = postgres_with_load_table.cursor.fetchone()[0]
    assert num_rows == 6


@pytest.mark.parametrize("load_function", [_load_local_tsv])
def test_delete_max_malformed_rows(
    postgres_with_load_table,
    tmpdir,
    empty_s3_bucket,
    load_function,
    load_table,
    identifier,
):
    load_function(tmpdir, empty_s3_bucket, "malformed_max_rows.tsv", identifier)
    check_query = f"SELECT COUNT (*) FROM {load_table};"
    postgres_with_load_table.cursor.execute(check_query)
    num_rows = postgres_with_load_table.cursor.fetchone()[0]
    assert num_rows == 3


@pytest.mark.parametrize("load_function", [_load_local_tsv])
def test_delete_more_than_max_malformed_rows(
    postgres_with_load_table, tmpdir, empty_s3_bucket, load_function, identifier
):
    with pytest.raises(InvalidTextRepresentation):
        load_function(
            tmpdir, empty_s3_bucket, "malformed_more_than_max_rows.tsv", identifier
        )


@flaky
@pytest.mark.parametrize("load_function", [_load_local_tsv, _load_s3_tsv])
def test_loaders_delete_null_url_rows(
    postgres_with_load_table,
    tmpdir,
    empty_s3_bucket,
    load_function,
    load_table,
    identifier,
):
    load_function(tmpdir, empty_s3_bucket, "url_missing.tsv", identifier)
    null_url_check = f"SELECT COUNT (*) FROM {load_table} WHERE url IS NULL;"
    postgres_with_load_table.cursor.execute(null_url_check)
    null_url_num_rows = postgres_with_load_table.cursor.fetchone()[0]
    remaining_row_count = f"SELECT COUNT (*) FROM {load_table};"
    postgres_with_load_table.cursor.execute(remaining_row_count)
    remaining_rows = postgres_with_load_table.cursor.fetchone()[0]

    assert null_url_num_rows == 0
    assert remaining_rows == 2


@flaky
@pytest.mark.parametrize("load_function", [_load_local_tsv, _load_s3_tsv])
def test_loaders_delete_null_license_rows(
    postgres_with_load_table,
    tmpdir,
    empty_s3_bucket,
    load_function,
    load_table,
    identifier,
):
    load_function(tmpdir, empty_s3_bucket, "license_missing.tsv", identifier)
    license_check = f"SELECT COUNT (*) FROM {load_table} WHERE license IS NULL;"
    postgres_with_load_table.cursor.execute(license_check)
    null_license_num_rows = postgres_with_load_table.cursor.fetchone()[0]
    remaining_row_count = f"SELECT COUNT (*) FROM {load_table};"
    postgres_with_load_table.cursor.execute(remaining_row_count)
    remaining_rows = postgres_with_load_table.cursor.fetchone()[0]

    assert null_license_num_rows == 0
    assert remaining_rows == 2


@flaky
@pytest.mark.parametrize("load_function", [_load_local_tsv, _load_s3_tsv])
def test_loaders_delete_null_foreign_landing_url_rows(
    postgres_with_load_table,
    tmpdir,
    empty_s3_bucket,
    load_function,
    load_table,
    identifier,
):
    load_function(
        tmpdir, empty_s3_bucket, "foreign_landing_url_missing.tsv", identifier
    )
    foreign_landing_url_check = (
        f"SELECT COUNT (*) FROM {load_table} " f"WHERE foreign_landing_url IS NULL;"
    )
    postgres_with_load_table.cursor.execute(foreign_landing_url_check)
    null_foreign_landing_url_num_rows = postgres_with_load_table.cursor.fetchone()[0]
    remaining_row_count = f"SELECT COUNT (*) FROM {load_table};"
    postgres_with_load_table.cursor.execute(remaining_row_count)
    remaining_rows = postgres_with_load_table.cursor.fetchone()[0]

    assert null_foreign_landing_url_num_rows == 0
    assert remaining_rows == 3


@pytest.mark.parametrize("load_function", [_load_local_tsv, _load_s3_tsv])
def test_data_loaders_delete_null_foreign_identifier_rows(
    postgres_with_load_table,
    tmpdir,
    empty_s3_bucket,
    load_function,
    load_table,
    identifier,
):
    load_function(tmpdir, empty_s3_bucket, "foreign_identifier_missing.tsv", identifier)
    foreign_identifier_check = (
        f"SELECT COUNT (*) FROM {load_table} " f"WHERE foreign_identifier IS NULL;"
    )
    postgres_with_load_table.cursor.execute(foreign_identifier_check)
    null_foreign_identifier_num_rows = postgres_with_load_table.cursor.fetchone()[0]
    remaining_row_count = f"SELECT COUNT (*) FROM {load_table};"
    postgres_with_load_table.cursor.execute(remaining_row_count)
    remaining_rows = postgres_with_load_table.cursor.fetchone()[0]

    assert null_foreign_identifier_num_rows == 0
    assert remaining_rows == 1


@pytest.mark.parametrize("load_function", [_load_local_tsv, _load_s3_tsv])
def test_import_data_deletes_duplicate_foreign_identifier_rows(
    postgres_with_load_table,
    tmpdir,
    empty_s3_bucket,
    load_function,
    load_table,
    identifier,
):
    load_function(
        tmpdir, empty_s3_bucket, "foreign_identifier_duplicate.tsv", identifier
    )
    foreign_id_duplicate_check = (
        f"SELECT COUNT (*) FROM {load_table} " f"WHERE foreign_identifier='135257';"
    )
    postgres_with_load_table.cursor.execute(foreign_id_duplicate_check)
    foreign_id_duplicate_num_rows = postgres_with_load_table.cursor.fetchone()[0]
    remaining_row_count = f"SELECT COUNT (*) FROM {load_table};"
    postgres_with_load_table.cursor.execute(remaining_row_count)
    remaining_rows = postgres_with_load_table.cursor.fetchone()[0]

    assert foreign_id_duplicate_num_rows == 1
    assert remaining_rows == 3


def test_upsert_records_inserts_one_record_to_empty_image_table(
    postgres_with_load_and_image_table, tmpdir, load_table, image_table, identifier
):
    postgres_conn_id = POSTGRES_CONN_ID

    FID = "a"
    LAND_URL = "https://images.com/a"
    IMG_URL = "https://images.com/a/img.jpg"
    THM_URL = "https://images.com/a/img_small.jpg"
    WIDTH = 1000
    HEIGHT = 500
    FILESIZE = 2000
    LICENSE = "cc0"
    VERSION = "1.0"
    CREATOR = "Alice"
    CREATOR_URL = "https://alice.com"
    TITLE = "My Great Pic"
    META_DATA = '{"description": "what a cool picture"}'
    TAGS = '["fun", "great"]'
    WATERMARKED = "f"
    PROVIDER = "images_provider"
    SOURCE = "images_source"
    INGESTION_TYPE = "test_ingestion"

    query_values = create_query_values(
        {
            col.FOREIGN_ID.db_name: FID,
            col.LANDING_URL.db_name: LAND_URL,
            col.DIRECT_URL.db_name: IMG_URL,
            col.THUMBNAIL.db_name: THM_URL,
            col.FILESIZE.db_name: FILESIZE,
            col.LICENSE.db_name: LICENSE,
            col.LICENSE_VERSION.db_name: VERSION,
            col.CREATOR.db_name: CREATOR,
            col.CREATOR_URL.db_name: CREATOR_URL,
            col.TITLE.db_name: TITLE,
            col.META_DATA.db_name: META_DATA,
            col.TAGS.db_name: TAGS,
            col.WATERMARKED.db_name: WATERMARKED,
            col.PROVIDER.db_name: PROVIDER,
            col.SOURCE.db_name: SOURCE,
            col.INGESTION_TYPE.db_name: INGESTION_TYPE,
            col.WIDTH.db_name: WIDTH,
            col.HEIGHT.db_name: HEIGHT,
        }
    )
    load_data_query = f"""INSERT INTO {load_table} VALUES(
        {query_values}
        );"""
    postgres_with_load_and_image_table.cursor.execute(load_data_query)
    postgres_with_load_and_image_table.connection.commit()
    sql.upsert_records_to_db_table(postgres_conn_id, identifier, db_table=image_table)
    postgres_with_load_and_image_table.cursor.execute(f"SELECT * FROM {image_table};")
    actual_rows = postgres_with_load_and_image_table.cursor.fetchall()
    actual_row = actual_rows[0]
    assert len(actual_rows) == 1
    assert actual_row[ingestion_idx] == INGESTION_TYPE
    assert actual_row[provider_idx] == PROVIDER
    assert actual_row[source_idx] == SOURCE
    assert actual_row[fid_idx] == FID
    assert actual_row[land_url_idx] == LAND_URL
    assert actual_row[url_idx] == IMG_URL
    assert actual_row[thm_idx] == THM_URL
    assert actual_row[filesize_idx] == FILESIZE
    assert actual_row[license_idx] == LICENSE
    assert actual_row[version_idx] == VERSION
    assert actual_row[creator_idx] == CREATOR
    assert actual_row[creator_url_idx] == CREATOR_URL
    assert actual_row[title_idx] == TITLE
    assert actual_row[metadata_idx] == json.loads(META_DATA)
    assert actual_row[tags_idx] == json.loads(TAGS)
    assert actual_row[watermarked_idx] is False
    assert actual_row[width_idx] == WIDTH
    assert actual_row[height_idx] == HEIGHT


def test_upsert_records_inserts_two_records_to_image_table(
    postgres_with_load_and_image_table, tmpdir, load_table, image_table, identifier
):
    postgres_conn_id = POSTGRES_CONN_ID

    FID_A = "a"
    FID_B = "b"
    LAND_URL_A = "https://images.com/a"
    LAND_URL_B = "https://images.com/b"
    IMG_URL_A = "images.com/a/img.jpg"
    IMG_URL_B = "images.com/b/img.jpg"
    LICENSE = "cc0"
    VERSION = "1.0"
    PROVIDER = "images"

    test_rows = [
        (FID_A, LAND_URL_A, IMG_URL_A, LICENSE, VERSION, PROVIDER),
        (FID_B, LAND_URL_B, IMG_URL_B, LICENSE, VERSION, PROVIDER),
    ]

    for r in test_rows:
        load_data_query = f"""INSERT INTO {load_table} (
            foreign_identifier, foreign_landing_url, url,
             license, license_version, provider, source
            ) VALUES (
            '{r[0]}', '{r[1]}', '{r[2]}',
            '{r[3]}', '{r[4]}', '{r[5]}', '{r[5]}'
            );"""
        postgres_with_load_and_image_table.cursor.execute(load_data_query)
        postgres_with_load_and_image_table.connection.commit()
    sql.upsert_records_to_db_table(postgres_conn_id, identifier, db_table=image_table)
    postgres_with_load_and_image_table.cursor.execute(f"SELECT * FROM {image_table};")
    actual_rows = postgres_with_load_and_image_table.cursor.fetchall()
    assert actual_rows[0][fid_idx] == FID_A
    assert actual_rows[1][fid_idx] == FID_B


def test_upsert_records_replaces_updated_on_and_last_synced_with_source(
    postgres_with_load_and_image_table, tmpdir, load_table, image_table, identifier
):
    postgres_conn_id = POSTGRES_CONN_ID

    FID = "a"
    LAND_URL = "https://images.com/a"
    IMG_URL = "images.com/a/img.jpg"
    LICENSE = "cc0"
    VERSION = "1.0"
    PROVIDER = "images"

    load_data_query = f"""INSERT INTO {load_table} (
        foreign_identifier, foreign_landing_url, url,
         license, license_version, provider, source
        ) VALUES (
        '{FID}','{LAND_URL}','{IMG_URL}','{LICENSE}','{VERSION}',
        '{PROVIDER}','{PROVIDER}'
        );"""
    postgres_with_load_and_image_table.cursor.execute(load_data_query)
    postgres_with_load_and_image_table.connection.commit()

    sql.upsert_records_to_db_table(postgres_conn_id, identifier, db_table=image_table)
    postgres_with_load_and_image_table.cursor.execute(f"SELECT * FROM {image_table};")
    original_row = postgres_with_load_and_image_table.cursor.fetchall()
    logging.info(f"\n{len(original_row)}\nOriginal row: {original_row}\n")
    original_row = original_row[0]
    original_updated_on = original_row[updated_idx]
    original_last_synced = original_row[synced_idx]
    logging.info(
        f"\nLast updated: {original_updated_on}\nSynced: {original_last_synced}"
    )

    time.sleep(1)
    sql.upsert_records_to_db_table(postgres_conn_id, identifier, db_table=image_table)
    postgres_with_load_and_image_table.cursor.execute(f"SELECT * FROM {image_table};")
    updated_result = postgres_with_load_and_image_table.cursor.fetchall()
    logging.info(
        f"\n{len(updated_result)}\nLast updated: {original_updated_on}\nSynced: {original_last_synced}"
    )
    updated_row = updated_result[0]
    updated_updated_on = updated_row[updated_idx]
    updated_last_synced = updated_row[synced_idx]

    assert len(updated_result) == 1
    assert updated_updated_on > original_updated_on
    assert updated_last_synced > original_last_synced


def test_upsert_records_replaces_data(
    postgres_with_load_and_image_table, tmpdir, load_table, image_table, identifier
):
    postgres_conn_id = POSTGRES_CONN_ID

    FID = "a"
    PROVIDER = "images_provider"
    SOURCE = "images_source"
    WATERMARKED = "f"
    FILESIZE = 2000
    TAGS = '["fun", "great"]'

    IMG_URL_A = "https://images.com/a/img.jpg"
    LAND_URL_A = "https://images.com/a"
    THM_URL_A = "https://images.com/a/img_small.jpg"
    WIDTH_A = 1000
    HEIGHT_A = 500
    LICENSE_A = "by"
    VERSION_A = "4.0"
    CREATOR_A = "Alice"
    CREATOR_URL_A = "https://alice.com"
    TITLE_A = "My Great Pic"
    META_DATA_A = '{"description": "what a cool picture"}'
    INGESTION_TYPE = "provider_api"

    IMG_URL_B = "https://images.com/b/img.jpg"
    LAND_URL_B = "https://images.com/b"
    THM_URL_B = "https://images.com/b/img_small.jpg"
    WIDTH_B = 2000
    HEIGHT_B = 1000
    LICENSE_B = "cc0"
    VERSION_B = "1.0"
    CREATOR_B = "Bob"
    CREATOR_URL_B = "https://bob.com"
    TITLE_B = "Bobs Great Pic"
    META_DATA_B = '{"description": "Bobs cool picture"}'

    query_values = create_query_values(
        {
            col.FOREIGN_ID.db_name: FID,
            col.LANDING_URL.db_name: LAND_URL_A,
            col.DIRECT_URL.db_name: IMG_URL_A,
            col.THUMBNAIL.db_name: THM_URL_A,
            col.FILESIZE.db_name: FILESIZE,
            col.LICENSE.db_name: LICENSE_A,
            col.LICENSE_VERSION.db_name: VERSION_A,
            col.CREATOR.db_name: CREATOR_A,
            col.CREATOR_URL.db_name: CREATOR_URL_A,
            col.TITLE.db_name: TITLE_A,
            col.META_DATA.db_name: META_DATA_A,
            col.TAGS.db_name: TAGS,
            col.WATERMARKED.db_name: WATERMARKED,
            col.PROVIDER.db_name: PROVIDER,
            col.SOURCE.db_name: SOURCE,
            col.INGESTION_TYPE.db_name: INGESTION_TYPE,
            col.WIDTH.db_name: WIDTH_A,
            col.HEIGHT.db_name: HEIGHT_A,
        }
    )
    load_data_query_a = f"""INSERT INTO {load_table} VALUES(
       {query_values}
       );"""
    postgres_with_load_and_image_table.cursor.execute(load_data_query_a)
    postgres_with_load_and_image_table.connection.commit()
    sql.upsert_records_to_db_table(postgres_conn_id, identifier, db_table=image_table)
    postgres_with_load_and_image_table.connection.commit()

    query_values = create_query_values(
        {
            col.FOREIGN_ID.db_name: FID,
            col.LANDING_URL.db_name: LAND_URL_B,
            col.DIRECT_URL.db_name: IMG_URL_B,
            col.THUMBNAIL.db_name: THM_URL_B,
            col.FILESIZE.db_name: FILESIZE,
            col.LICENSE.db_name: LICENSE_B,
            col.LICENSE_VERSION.db_name: VERSION_B,
            col.CREATOR.db_name: CREATOR_B,
            col.CREATOR_URL.db_name: CREATOR_URL_B,
            col.TITLE.db_name: TITLE_B,
            col.META_DATA.db_name: META_DATA_B,
            col.TAGS.db_name: TAGS,
            col.WATERMARKED.db_name: WATERMARKED,
            col.PROVIDER.db_name: PROVIDER,
            col.SOURCE.db_name: SOURCE,
            col.INGESTION_TYPE.db_name: INGESTION_TYPE,
            col.WIDTH.db_name: WIDTH_B,
            col.HEIGHT.db_name: HEIGHT_B,
        }
    )
    load_data_query_b = f"""INSERT INTO {load_table} VALUES(
        {query_values}
        );"""
    postgres_with_load_and_image_table.cursor.execute(f"DELETE FROM {load_table};")
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(load_data_query_b)
    postgres_with_load_and_image_table.connection.commit()
    sql.upsert_records_to_db_table(postgres_conn_id, identifier, db_table=image_table)
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(f"SELECT * FROM {image_table};")
    actual_rows = postgres_with_load_and_image_table.cursor.fetchall()
    actual_row = actual_rows[0]
    assert len(actual_rows) == 1
    assert actual_row[land_url_idx] == LAND_URL_B
    assert actual_row[url_idx] == IMG_URL_B
    assert actual_row[thm_idx] == THM_URL_B
    assert actual_row[license_idx] == LICENSE_B
    assert actual_row[version_idx] == VERSION_B
    assert actual_row[creator_idx] == CREATOR_B
    assert actual_row[creator_url_idx] == CREATOR_URL_B
    assert actual_row[title_idx] == TITLE_B
    assert actual_row[metadata_idx] == json.loads(META_DATA_B)
    assert actual_row[tags_idx] == json.loads(TAGS)
    assert actual_row[width_idx] == WIDTH_B


def test_upsert_records_does_not_replace_with_nulls(
    postgres_with_load_and_image_table, tmpdir, load_table, image_table, identifier
):
    postgres_conn_id = POSTGRES_CONN_ID

    FID = "a"
    PROVIDER = "images_provider"
    SOURCE = "images_source"
    WATERMARKED = "f"
    IMG_URL = "https://images.com/a/img.jpg"
    FILESIZE = 2000
    TAGS = '["fun", "great"]'
    INGESTION_TYPE = "provider_api"

    LAND_URL_A = "https://images.com/a"
    THM_URL_A = "https://images.com/a/img_small.jpg"
    WIDTH_A = 1000
    HEIGHT_A = 500
    LICENSE_A = "by"
    VERSION_A = "4.0"
    CREATOR_A = "Alice"
    CREATOR_URL_A = "https://alice.com"
    TITLE_A = "My Great Pic"
    META_DATA_A = '{"description": "what a cool picture"}'

    LAND_URL_B = "https://images.com/b"
    LICENSE_B = "cc0"
    VERSION_B = "1.0"

    query_values_a = create_query_values(
        {
            col.FOREIGN_ID.db_name: FID,
            col.LANDING_URL.db_name: LAND_URL_A,
            col.DIRECT_URL.db_name: IMG_URL,
            col.THUMBNAIL.db_name: THM_URL_A,
            col.FILESIZE.db_name: FILESIZE,
            col.LICENSE.db_name: LICENSE_A,
            col.LICENSE_VERSION.db_name: VERSION_A,
            col.CREATOR.db_name: CREATOR_A,
            col.CREATOR_URL.db_name: CREATOR_URL_A,
            col.TITLE.db_name: TITLE_A,
            col.META_DATA.db_name: META_DATA_A,
            col.TAGS.db_name: TAGS,
            col.WATERMARKED.db_name: WATERMARKED,
            col.PROVIDER.db_name: PROVIDER,
            col.SOURCE.db_name: SOURCE,
            col.INGESTION_TYPE.db_name: INGESTION_TYPE,
            col.WIDTH.db_name: WIDTH_A,
            col.HEIGHT.db_name: HEIGHT_A,
        }
    )
    load_data_query_a = f"""INSERT INTO {load_table} VALUES(
        {query_values_a}
        );"""
    postgres_with_load_and_image_table.cursor.execute(load_data_query_a)
    postgres_with_load_and_image_table.connection.commit()
    sql.upsert_records_to_db_table(postgres_conn_id, identifier, db_table=image_table)
    postgres_with_load_and_image_table.connection.commit()

    query_values_b = create_query_values(
        {
            col.FOREIGN_ID.db_name: FID,
            col.LANDING_URL.db_name: LAND_URL_B,
            col.DIRECT_URL.db_name: IMG_URL,
            col.LICENSE.db_name: LICENSE_B,
            col.LICENSE_VERSION.db_name: VERSION_B,
            col.TAGS.db_name: TAGS,
            col.PROVIDER.db_name: PROVIDER,
            col.SOURCE.db_name: SOURCE,
        }
    )
    load_data_query_b = f"""INSERT INTO {load_table} VALUES(
        {query_values_b}
        );"""
    postgres_with_load_and_image_table.cursor.execute(f"DELETE FROM {load_table};")
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(load_data_query_b)
    postgres_with_load_and_image_table.connection.commit()
    sql.upsert_records_to_db_table(postgres_conn_id, identifier, db_table=image_table)
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(f"SELECT * FROM {image_table};")
    actual_rows = postgres_with_load_and_image_table.cursor.fetchall()
    actual_row = actual_rows[0]
    assert len(actual_rows) == 1
    assert actual_row[land_url_idx] == LAND_URL_B
    assert actual_row[thm_idx] == THM_URL_A
    assert actual_row[filesize_idx] == FILESIZE
    assert actual_row[license_idx] == LICENSE_B
    assert actual_row[version_idx] == VERSION_B
    assert actual_row[creator_idx] == CREATOR_A
    assert actual_row[creator_url_idx] == CREATOR_URL_A
    assert actual_row[title_idx] == TITLE_A
    assert actual_row[metadata_idx] == json.loads(META_DATA_A)
    assert actual_row[tags_idx] == json.loads(TAGS)
    assert actual_row[width_idx] == WIDTH_A
    assert actual_row[height_idx] == HEIGHT_A


def test_upsert_records_merges_meta_data(
    postgres_with_load_and_image_table, tmpdir, load_table, image_table, identifier
):
    postgres_conn_id = POSTGRES_CONN_ID

    FID = "a"
    PROVIDER = "images_provider"
    IMG_URL = "https://images.com/a/img.jpg"
    LICENSE = "by"

    META_DATA_A = '{"description": "a cool picture", "test": "should stay"}'
    META_DATA_B = '{"description": "I updated my description"}'

    query_values_a = create_query_values(
        {
            col.FOREIGN_ID.db_name: FID,
            col.DIRECT_URL.db_name: IMG_URL,
            col.LICENSE.db_name: LICENSE,
            col.META_DATA.db_name: META_DATA_A,
            col.PROVIDER.db_name: PROVIDER,
        }
    )
    load_data_query_a = f"""INSERT INTO {load_table} VALUES(
        {query_values_a}
    );"""

    query_values_b = create_query_values(
        {
            col.FOREIGN_ID.db_name: FID,
            col.DIRECT_URL.db_name: IMG_URL,
            col.LICENSE.db_name: LICENSE,
            col.META_DATA.db_name: META_DATA_B,
            col.PROVIDER.db_name: PROVIDER,
        }
    )
    load_data_query_b = f"""INSERT INTO {load_table} VALUES(
        {query_values_b}
        );"""
    postgres_with_load_and_image_table.cursor.execute(load_data_query_a)
    postgres_with_load_and_image_table.connection.commit()
    sql.upsert_records_to_db_table(postgres_conn_id, identifier, db_table=image_table)
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(f"DELETE FROM {load_table};")
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(load_data_query_b)
    postgres_with_load_and_image_table.connection.commit()
    sql.upsert_records_to_db_table(postgres_conn_id, identifier, db_table=image_table)
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(f"SELECT * FROM {image_table};")
    actual_rows = postgres_with_load_and_image_table.cursor.fetchall()
    actual_row = actual_rows[0]
    assert len(actual_rows) == 1
    expected_meta_data = json.loads(META_DATA_A)
    expected_meta_data.update(json.loads(META_DATA_B))
    assert actual_row[metadata_idx] == expected_meta_data


def test_upsert_records_does_not_replace_with_null_values_in_meta_data(
    postgres_with_load_and_image_table, tmpdir, load_table, image_table, identifier
):
    postgres_conn_id = POSTGRES_CONN_ID

    FID = "a"
    PROVIDER = "images_provider"
    IMG_URL = "https://images.com/a/img.jpg"
    LICENSE = "by"

    META_DATA_A = '{"description": "a cool picture", "test": "should stay"}'
    META_DATA_B = '{"description": "I updated my description", "test": null}'

    query_values_a = create_query_values(
        {
            col.FOREIGN_ID.db_name: FID,
            col.DIRECT_URL.db_name: IMG_URL,
            col.LICENSE.db_name: LICENSE,
            col.META_DATA.db_name: META_DATA_A,
            col.PROVIDER.db_name: PROVIDER,
        }
    )
    load_data_query_a = f"""INSERT INTO {load_table} VALUES(
        {query_values_a}
        );"""

    query_values_b = create_query_values(
        {
            col.FOREIGN_ID.db_name: FID,
            col.DIRECT_URL.db_name: IMG_URL,
            col.LICENSE.db_name: LICENSE,
            col.META_DATA.db_name: META_DATA_B,
            col.PROVIDER.db_name: PROVIDER,
        }
    )
    load_data_query_b = f"""INSERT INTO {load_table} VALUES(
        {query_values_b}
        );"""
    postgres_with_load_and_image_table.cursor.execute(load_data_query_a)
    postgres_with_load_and_image_table.connection.commit()
    sql.upsert_records_to_db_table(postgres_conn_id, identifier, db_table=image_table)
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(f"DELETE FROM {load_table};")
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(load_data_query_b)
    postgres_with_load_and_image_table.connection.commit()
    sql.upsert_records_to_db_table(postgres_conn_id, identifier, db_table=image_table)
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(f"SELECT * FROM {image_table};")
    actual_rows = postgres_with_load_and_image_table.cursor.fetchall()
    actual_row = actual_rows[0]
    assert len(actual_rows) == 1
    expected_meta_data = {
        "description": json.loads(META_DATA_B)["description"],
        "test": json.loads(META_DATA_A)["test"],
    }
    assert actual_row[metadata_idx] == expected_meta_data


def test_upsert_records_merges_tags(
    postgres_with_load_and_image_table, tmpdir, load_table, image_table, identifier
):
    postgres_conn_id = POSTGRES_CONN_ID

    FID = "a"
    PROVIDER = "images_provider"
    IMG_URL = "https://images.com/a/img.jpg"
    LICENSE = "by"

    TAGS_A = json.dumps(
        [{"name": "tagone", "provider": "test"}, {"name": "tagtwo", "provider": "test"}]
    )
    TAGS_B = json.dumps(
        [
            {"name": "tagone", "provider": "test"},
            {"name": "tagthree", "provider": "test"},
        ]
    )

    query_values_a = create_query_values(
        {
            col.FOREIGN_ID.db_name: FID,
            col.DIRECT_URL.db_name: IMG_URL,
            col.LICENSE.db_name: LICENSE,
            col.TAGS.db_name: TAGS_A,
            col.PROVIDER.db_name: PROVIDER,
        }
    )
    load_data_query_a = f"""INSERT INTO {load_table} VALUES(
        {query_values_a}
        );"""

    query_values_b = create_query_values(
        {
            col.FOREIGN_ID.db_name: FID,
            col.DIRECT_URL.db_name: IMG_URL,
            col.LICENSE.db_name: LICENSE,
            col.TAGS.db_name: TAGS_B,
            col.PROVIDER.db_name: PROVIDER,
        }
    )
    load_data_query_b = f"""INSERT INTO {load_table} VALUES(
        {query_values_b}
        );"""
    postgres_with_load_and_image_table.cursor.execute(load_data_query_a)
    postgres_with_load_and_image_table.connection.commit()
    sql.upsert_records_to_db_table(postgres_conn_id, identifier, db_table=image_table)
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(f"DELETE FROM {load_table};")
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(load_data_query_b)
    postgres_with_load_and_image_table.connection.commit()
    sql.upsert_records_to_db_table(postgres_conn_id, identifier, db_table=image_table)
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(f"SELECT * FROM {image_table};")
    actual_rows = postgres_with_load_and_image_table.cursor.fetchall()
    actual_row = actual_rows[0]
    assert len(actual_rows) == 1
    expect_tags = [
        {"name": "tagone", "provider": "test"},
        {"name": "tagtwo", "provider": "test"},
        {"name": "tagthree", "provider": "test"},
    ]
    actual_tags = actual_row[tags_idx]
    assert len(actual_tags) == 3
    assert all([t in expect_tags for t in actual_tags])
    assert all([t in actual_tags for t in expect_tags])


def test_upsert_records_does_not_replace_tags_with_null(
    postgres_with_load_and_image_table, tmpdir, load_table, image_table, identifier
):
    postgres_conn_id = POSTGRES_CONN_ID

    FID = "a"
    PROVIDER = "images_provider"
    IMG_URL = "https://images.com/a/img.jpg"
    LICENSE = "by"

    TAGS = [
        {"name": "tagone", "provider": "test"},
        {"name": "tagtwo", "provider": "test"},
    ]

    query_values_a = create_query_values(
        {
            col.FOREIGN_ID.db_name: FID,
            col.DIRECT_URL.db_name: IMG_URL,
            col.LICENSE.db_name: LICENSE,
            col.TAGS.db_name: json.dumps(TAGS),
            col.PROVIDER.db_name: PROVIDER,
        }
    )
    load_data_query_a = f"""INSERT INTO {load_table} VALUES(
        {query_values_a}
        );"""

    query_values_b = create_query_values(
        {
            col.FOREIGN_ID.db_name: FID,
            col.DIRECT_URL.db_name: IMG_URL,
            col.LICENSE.db_name: LICENSE,
            col.PROVIDER.db_name: PROVIDER,
        }
    )
    load_data_query_b = f"""INSERT INTO {load_table} VALUES(
        {query_values_b}
        );"""
    postgres_with_load_and_image_table.cursor.execute(load_data_query_a)
    postgres_with_load_and_image_table.connection.commit()
    sql.upsert_records_to_db_table(postgres_conn_id, identifier, db_table=image_table)
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(f"DELETE FROM {load_table};")
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(load_data_query_b)
    postgres_with_load_and_image_table.connection.commit()
    sql.upsert_records_to_db_table(postgres_conn_id, identifier, db_table=image_table)
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(f"SELECT * FROM {image_table};")
    actual_rows = postgres_with_load_and_image_table.cursor.fetchall()
    actual_row = actual_rows[0]
    assert len(actual_rows) == 1
    expect_tags = [
        {"name": "tagone", "provider": "test"},
        {"name": "tagtwo", "provider": "test"},
    ]
    actual_tags = actual_row[tags_idx]
    assert len(actual_tags) == 2
    assert all([t in expect_tags for t in actual_tags])
    assert all([t in actual_tags for t in expect_tags])


def test_upsert_records_replaces_null_tags(
    postgres_with_load_and_image_table, tmpdir, load_table, image_table, identifier
):
    postgres_conn_id = POSTGRES_CONN_ID

    FID = "a"
    PROVIDER = "images_provider"
    IMG_URL = "https://images.com/a/img.jpg"
    LICENSE = "by"
    TAGS = [
        {"name": "tagone", "provider": "test"},
        {"name": "tagtwo", "provider": "test"},
    ]
    query_values_a = create_query_values(
        {
            col.FOREIGN_ID.db_name: FID,
            col.DIRECT_URL.db_name: IMG_URL,
            col.LICENSE.db_name: LICENSE,
            col.PROVIDER.db_name: PROVIDER,
        }
    )
    logging.info(f"Query values a: {query_values_a}")
    load_data_query_a = f"""INSERT INTO {load_table} VALUES(
        {query_values_a}
        );"""
    query_values_b = create_query_values(
        {
            col.FOREIGN_ID.db_name: FID,
            col.DIRECT_URL.db_name: IMG_URL,
            col.LICENSE.db_name: LICENSE,
            col.TAGS.db_name: json.dumps(TAGS),
            col.PROVIDER.db_name: PROVIDER,
        }
    )
    load_data_query_b = f"""INSERT INTO {load_table} VALUES(
        {query_values_b}
        );"""

    postgres_with_load_and_image_table.cursor.execute(load_data_query_a)
    postgres_with_load_and_image_table.connection.commit()
    sql.upsert_records_to_db_table(postgres_conn_id, identifier, db_table=image_table)
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(f"DELETE FROM {load_table};")
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(load_data_query_b)
    postgres_with_load_and_image_table.connection.commit()
    sql.upsert_records_to_db_table(postgres_conn_id, identifier, db_table=image_table)
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(f"SELECT * FROM {image_table};")
    actual_rows = postgres_with_load_and_image_table.cursor.fetchall()
    actual_row = actual_rows[0]
    logging.info(f"Actual row: {actual_row}")
    assert len(actual_rows) == 1
    expect_tags = [
        {"name": "tagone", "provider": "test"},
        {"name": "tagtwo", "provider": "test"},
    ]
    actual_tags = actual_row[tags_idx]
    assert len(actual_tags) == 2
    assert all([t in expect_tags for t in actual_tags])
    assert all([t in actual_tags for t in expect_tags])


def test_drop_load_table_drops_table(postgres_with_load_table, load_table, identifier):
    postgres_conn_id = POSTGRES_CONN_ID
    sql.drop_load_table(postgres_conn_id, identifier)
    check_query = (
        f"SELECT EXISTS (" f"SELECT FROM pg_tables WHERE tablename='{load_table}');"
    )
    postgres_with_load_table.cursor.execute(check_query)
    check_result = postgres_with_load_table.cursor.fetchone()[0]
    assert not check_result


def test_image_expiration(
    postgres_with_load_and_image_table, load_table, image_table, identifier
):
    postgres_conn_id = POSTGRES_CONN_ID

    FID_A = "a"
    FID_B = "b"
    IMG_URL_A = "https://images.com/a/img.jpg"
    IMG_URL_B = "https://images.com/b/img.jpg"
    PROVIDER_A = "smithsonian"
    PROVIDER_B = "flickr"
    LICENSE = "by-nc-nd"

    query_values = [
        create_query_values(
            {
                col.FOREIGN_ID.db_name: FID_A,
                col.DIRECT_URL.db_name: IMG_URL_A,
                col.LICENSE.db_name: LICENSE,
                col.PROVIDER.db_name: PROVIDER_A,
                col.SOURCE.db_name: PROVIDER_A,
            }
        ),
        create_query_values(
            {
                col.FOREIGN_ID.db_name: FID_B,
                col.DIRECT_URL.db_name: IMG_URL_B,
                col.LICENSE.db_name: LICENSE,
                col.PROVIDER.db_name: PROVIDER_B,
                col.SOURCE.db_name: PROVIDER_B,
            }
        ),
    ]
    insert_data_query = f"""INSERT INTO {load_table} VALUES
        ({query_values[0]}),
        ({query_values[1]}
        );"""

    postgres_with_load_and_image_table.cursor.execute(insert_data_query)
    postgres_with_load_and_image_table.connection.commit()
    sql.upsert_records_to_db_table(postgres_conn_id, identifier, db_table=image_table)
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(f"DELETE FROM {load_table};")
    postgres_with_load_and_image_table.connection.commit()

    postgres_with_load_and_image_table.cursor.execute(
        f"UPDATE {image_table} SET updated_on = NOW() - INTERVAL '1 year' "
        f"WHERE provider = 'flickr';"
    )

    postgres_with_load_and_image_table.connection.commit()

    sql.expire_old_images(postgres_conn_id, PROVIDER_A, image_table=image_table)

    sql.expire_old_images(postgres_conn_id, PROVIDER_B, image_table=image_table)

    postgres_with_load_and_image_table.connection.commit()

    postgres_with_load_and_image_table.cursor.execute(f"SELECT * FROM {image_table};")
    actual_rows = postgres_with_load_and_image_table.cursor.fetchall()
    assert len(actual_rows) == 2

    for actual_row in actual_rows:
        if actual_row[fid_idx] == "a":
            assert not actual_row[removed_idx]
        else:
            assert actual_row[fid_idx] == "b" and actual_row[removed_idx]

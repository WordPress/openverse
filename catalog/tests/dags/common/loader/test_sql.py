import json
import logging
import os
import time
from textwrap import dedent
from unittest import mock

import psycopg2
import pytest
from flaky import flaky
from psycopg2.errors import InvalidTextRepresentation

from catalog.tests.dags.common.conftest import POSTGRES_TEST_CONN_ID as POSTGRES_CONN_ID
from catalog.tests.dags.popularity.test_sql import _set_up_std_popularity_func
from catalog.tests.test_utils import sql as utils
from common.loader import sql
from common.storage import columns as col


RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)), "test_resources")


@pytest.fixture
def load_table(identifier):
    # Parallelized tests need to use distinct database tables
    return f"load_image_{identifier}"


@pytest.fixture
def postgres(load_table) -> utils.PostgresRef:
    conn = psycopg2.connect(utils.POSTGRES_TEST_URI)
    cur = conn.cursor()
    drop_command = f"DROP TABLE IF EXISTS {load_table}"
    cur.execute(drop_command)
    conn.commit()

    yield utils.PostgresRef(cursor=cur, connection=conn)

    cur.execute(drop_command)
    cur.close()
    conn.commit()
    conn.close()


@pytest.fixture
def postgres_with_load_table(
    postgres: utils.PostgresRef, load_table
) -> utils.PostgresRef:
    create_command = utils.CREATE_LOAD_TABLE_QUERY.format(load_table)
    postgres.cursor.execute(create_command)
    postgres.connection.commit()

    yield postgres


@pytest.fixture
def postgres_with_load_and_image_table(load_table, sql_info, mock_pg_hook_task):
    conn = psycopg2.connect(utils.POSTGRES_TEST_URI)
    cur = conn.cursor()
    drop_test_relations_query = f"""
    DROP TABLE IF EXISTS {load_table} CASCADE;
    DROP TABLE IF EXISTS {sql_info.media_table} CASCADE;
    DROP INDEX IF EXISTS {sql_info.media_table}_provider_fid_idx;
    DROP TABLE IF EXISTS {sql_info.metrics_table} CASCADE;
    DROP FUNCTION IF EXISTS {sql_info.standardized_popularity_fn} CASCADE;
    DROP FUNCTION IF EXISTS {sql_info.popularity_percentile_fn} CASCADE;
    """

    cur.execute(drop_test_relations_query)

    cur.execute(utils.CREATE_LOAD_TABLE_QUERY.format(load_table))
    cur.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;')
    cur.execute(utils.CREATE_IMAGE_TABLE_QUERY.format(sql_info.media_table))
    cur.execute(utils.UNIQUE_CONDITION_QUERY.format(table=sql_info.media_table))

    conn.commit()

    yield utils.PostgresRef(cursor=cur, connection=conn)

    cur.execute(drop_test_relations_query)
    cur.close()
    conn.commit()
    conn.close()


def _load_local_tsv(tmpdir, bucket, tsv_file_name, identifier, mock_pg_hook_task):
    """
    Wrap ``sql.load_local_data_to_intermediate_table`` so we can test it under
    various conditions.
    """
    tsv_file_path = os.path.join(RESOURCES, tsv_file_name)
    with open(tsv_file_path) as f:
        f_data = f.read()

    test_tsv = "test.tsv"
    path = tmpdir.join(test_tsv)
    path.write(f_data)

    sql.load_local_data_to_intermediate_table(
        postgres_conn_id=POSTGRES_CONN_ID,
        tsv_file_name=str(path),
        identifier=identifier,
        task=mock_pg_hook_task,
    )


def _load_s3_tsv(tmpdir, bucket, tsv_file_name, identifier, mock_pg_hook_task):
    tsv_file_path = os.path.join(RESOURCES, tsv_file_name)
    key = f"path/to/object/{tsv_file_name}"
    bucket.upload_file(tsv_file_path, key)
    sql.load_s3_data_to_intermediate_table(
        postgres_conn_id=POSTGRES_CONN_ID,
        bucket=bucket.name,
        s3_key=key,
        identifier=identifier,
        task=mock_pg_hook_task,
    )


def test_create_loading_table_creates_table(
    postgres, load_table, identifier, mock_pg_hook_task
):
    postgres_conn_id = POSTGRES_CONN_ID
    sql.create_loading_table(postgres_conn_id, identifier, media_type="image")

    check_query = (
        f"SELECT EXISTS (SELECT FROM pg_tables WHERE tablename='{load_table}');"
    )
    postgres.cursor.execute(check_query)
    check_result = postgres.cursor.fetchone()[0]
    assert check_result


def test_create_loading_table_errors_if_run_twice_with_same_id(postgres, identifier):
    postgres_conn_id = POSTGRES_CONN_ID
    sql.create_loading_table(postgres_conn_id, identifier, media_type="image")
    with pytest.raises(Exception):
        sql.create_loading_table(postgres_conn_id, identifier, media_type="image")


@flaky
@pytest.mark.parametrize("load_function", [_load_local_tsv, _load_s3_tsv])
def test_loaders_load_good_tsv(
    postgres_with_load_table,
    tmpdir,
    empty_s3_bucket,
    load_function,
    load_table,
    identifier,
    mock_pg_hook_task,
):
    load_function(
        tmpdir, empty_s3_bucket, "none_missing.tsv", identifier, mock_pg_hook_task
    )
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
    mock_pg_hook_task,
):
    load_function(
        tmpdir,
        empty_s3_bucket,
        "malformed_less_than_max_rows.tsv",
        identifier,
        mock_pg_hook_task,
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
    mock_pg_hook_task,
):
    load_function(
        tmpdir, empty_s3_bucket, "malformed_max_rows.tsv", identifier, mock_pg_hook_task
    )
    check_query = f"SELECT COUNT (*) FROM {load_table};"
    postgres_with_load_table.cursor.execute(check_query)
    num_rows = postgres_with_load_table.cursor.fetchone()[0]
    assert num_rows == 3


@pytest.mark.parametrize("load_function", [_load_local_tsv])
def test_delete_more_than_max_malformed_rows(
    postgres_with_load_table,
    tmpdir,
    empty_s3_bucket,
    load_function,
    identifier,
    mock_pg_hook_task,
):
    with pytest.raises(InvalidTextRepresentation):
        load_function(
            tmpdir,
            empty_s3_bucket,
            "malformed_more_than_max_rows.tsv",
            identifier,
            mock_pg_hook_task,
        )


@flaky
@pytest.mark.parametrize("load_function", [_load_local_tsv, _load_s3_tsv])
def test_loaders_deletes_null_url_rows(
    postgres_with_load_table,
    tmpdir,
    empty_s3_bucket,
    load_function,
    load_table,
    identifier,
    mock_pg_hook_task,
):
    # Load test data with some null urls into the intermediate table
    load_function(
        tmpdir, empty_s3_bucket, "url_missing.tsv", identifier, mock_pg_hook_task
    )
    # Clean data
    sql.clean_intermediate_table_data(
        POSTGRES_CONN_ID, identifier, task=mock_pg_hook_task
    )

    # Check that rows with null urls were deleted
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
    mock_pg_hook_task,
):
    # Load test data with some null licenses into the intermediate table
    load_function(
        tmpdir, empty_s3_bucket, "license_missing.tsv", identifier, mock_pg_hook_task
    )
    # Clean data
    sql.clean_intermediate_table_data(
        POSTGRES_CONN_ID, identifier, task=mock_pg_hook_task
    )

    # Check that rows with null licenses were deleted
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
    mock_pg_hook_task,
):
    # Load test data with null foreign landings url into the intermediate table
    load_function(
        tmpdir,
        empty_s3_bucket,
        "foreign_landing_url_missing.tsv",
        identifier,
        mock_pg_hook_task,
    )
    # Clean data
    sql.clean_intermediate_table_data(
        POSTGRES_CONN_ID, identifier, task=mock_pg_hook_task
    )

    # Check that rows with null foreign landing urls were deleted
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
    mock_pg_hook_task,
):
    # Load test data with null foreign identifiers into the intermediate table
    load_function(
        tmpdir,
        empty_s3_bucket,
        "foreign_identifier_missing.tsv",
        identifier,
        mock_pg_hook_task,
    )
    # Clean data
    sql.clean_intermediate_table_data(
        POSTGRES_CONN_ID, identifier, task=mock_pg_hook_task
    )

    # Check that rows with null foreign identifiers were deleted
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
    mock_pg_hook_task,
):
    # Load test data with duplicate foreign identifiers into the intermediate table
    load_function(
        tmpdir,
        empty_s3_bucket,
        "foreign_identifier_duplicate.tsv",
        identifier,
        mock_pg_hook_task,
    )
    # Clean data
    sql.clean_intermediate_table_data(
        POSTGRES_CONN_ID, identifier, task=mock_pg_hook_task
    )

    # Check that rows with duplicate foreign ids were deleted
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
    postgres_with_load_and_image_table,
    tmpdir,
    load_table,
    image_table,
    sql_info,
    identifier,
    mock_pg_hook_task,
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

    query_values = utils.create_query_values(
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
    load_data_query = utils.make_insert_query(load_table, query_values)

    _set_up_std_popularity_func(
        postgres_with_load_and_image_table,
        load_data_query,
        {},
        sql_info,
        mock_pg_hook_task,
    )

    sql.upsert_records_to_db_table(
        postgres_conn_id,
        identifier,
        media_type="image",
        sql_info=sql_info,
        task=mock_pg_hook_task,
    )
    postgres_with_load_and_image_table.cursor.execute(f"SELECT * FROM {image_table};")
    actual_rows = postgres_with_load_and_image_table.cursor.fetchall()
    actual_row = actual_rows[0]
    assert len(actual_rows) == 1
    assert actual_row[utils.ingestion_idx] == INGESTION_TYPE
    assert actual_row[utils.provider_idx] == PROVIDER
    assert actual_row[utils.source_idx] == SOURCE
    assert actual_row[utils.fid_idx] == FID
    assert actual_row[utils.land_url_idx] == LAND_URL
    assert actual_row[utils.url_idx] == IMG_URL
    assert actual_row[utils.thm_idx] == THM_URL
    assert actual_row[utils.filesize_idx] == FILESIZE
    assert actual_row[utils.license_idx] == LICENSE
    assert actual_row[utils.version_idx] == VERSION
    assert actual_row[utils.creator_idx] == CREATOR
    assert actual_row[utils.creator_url_idx] == CREATOR_URL
    assert actual_row[utils.title_idx] == TITLE
    assert actual_row[utils.metadata_idx] == json.loads(META_DATA)
    assert actual_row[utils.tags_idx] == json.loads(TAGS)
    assert actual_row[utils.watermarked_idx] is False
    assert actual_row[utils.width_idx] == WIDTH
    assert actual_row[utils.height_idx] == HEIGHT


def test_upsert_records_inserts_two_records_to_image_table(
    postgres_with_load_and_image_table,
    tmpdir,
    load_table,
    image_table,
    sql_info,
    identifier,
    mock_pg_hook_task,
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

    _set_up_std_popularity_func(
        postgres_with_load_and_image_table,
        None,
        {},
        sql_info,
        mock_pg_hook_task,
    )

    sql.upsert_records_to_db_table(
        postgres_conn_id,
        identifier,
        media_type="image",
        sql_info=sql_info,
        task=mock_pg_hook_task,
    )
    postgres_with_load_and_image_table.cursor.execute(f"SELECT * FROM {image_table};")
    actual_rows = postgres_with_load_and_image_table.cursor.fetchall()
    assert actual_rows[0][utils.fid_idx] == FID_A
    assert actual_rows[1][utils.fid_idx] == FID_B


def test_upsert_records_replaces_updated_on_and_last_synced_with_source(
    postgres_with_load_and_image_table,
    tmpdir,
    load_table,
    image_table,
    sql_info,
    identifier,
    mock_pg_hook_task,
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

    _set_up_std_popularity_func(
        postgres_with_load_and_image_table,
        load_data_query,
        {},
        sql_info,
        mock_pg_hook_task,
    )

    sql.upsert_records_to_db_table(
        postgres_conn_id,
        identifier,
        media_type="image",
        sql_info=sql_info,
        task=mock_pg_hook_task,
    )
    postgres_with_load_and_image_table.cursor.execute(f"SELECT * FROM {image_table};")
    original_row = postgres_with_load_and_image_table.cursor.fetchall()
    logging.info(f"\n{len(original_row)}\nOriginal row: {original_row}\n")
    original_row = original_row[0]
    original_updated_on = original_row[utils.updated_idx]
    original_last_synced = original_row[utils.synced_idx]
    logging.info(
        f"\nLast updated: {original_updated_on}\nSynced: {original_last_synced}"
    )

    time.sleep(0.5)
    sql.upsert_records_to_db_table(
        postgres_conn_id,
        identifier,
        media_type="image",
        sql_info=sql_info,
        task=mock_pg_hook_task,
    )
    postgres_with_load_and_image_table.cursor.execute(f"SELECT * FROM {image_table};")
    updated_result = postgres_with_load_and_image_table.cursor.fetchall()
    logging.info(
        f"\n{len(updated_result)}\nLast updated: {original_updated_on}\nSynced: {original_last_synced}"
    )
    updated_row = updated_result[0]
    updated_updated_on = updated_row[utils.updated_idx]
    updated_last_synced = updated_row[utils.synced_idx]

    assert len(updated_result) == 1
    assert updated_updated_on > original_updated_on
    assert updated_last_synced > original_last_synced


def test_upsert_records_replaces_data(
    postgres_with_load_and_image_table,
    tmpdir,
    load_table,
    image_table,
    sql_info,
    identifier,
    mock_pg_hook_task,
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

    query_values = utils.create_query_values(
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
    _set_up_std_popularity_func(
        postgres_with_load_and_image_table,
        load_data_query_a,
        {},
        sql_info,
        mock_pg_hook_task,
    )

    sql.upsert_records_to_db_table(
        postgres_conn_id,
        identifier,
        media_type="image",
        sql_info=sql_info,
        task=mock_pg_hook_task,
    )
    postgres_with_load_and_image_table.connection.commit()

    query_values = utils.create_query_values(
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
    sql.upsert_records_to_db_table(
        postgres_conn_id,
        identifier,
        media_type="image",
        sql_info=sql_info,
        task=mock_pg_hook_task,
    )
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(f"SELECT * FROM {image_table};")
    actual_rows = postgres_with_load_and_image_table.cursor.fetchall()
    actual_row = actual_rows[0]
    assert len(actual_rows) == 1
    assert actual_row[utils.land_url_idx] == LAND_URL_B
    assert actual_row[utils.url_idx] == IMG_URL_B
    assert actual_row[utils.thm_idx] == THM_URL_B
    assert actual_row[utils.license_idx] == LICENSE_B
    assert actual_row[utils.version_idx] == VERSION_B
    assert actual_row[utils.creator_idx] == CREATOR_B
    assert actual_row[utils.creator_url_idx] == CREATOR_URL_B
    assert actual_row[utils.title_idx] == TITLE_B
    assert actual_row[utils.metadata_idx] == json.loads(META_DATA_B)
    assert actual_row[utils.tags_idx] == json.loads(TAGS)
    assert actual_row[utils.width_idx] == WIDTH_B


def test_upsert_records_does_not_replace_with_nulls(
    postgres_with_load_and_image_table,
    tmpdir,
    load_table,
    image_table,
    sql_info,
    identifier,
    mock_pg_hook_task,
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

    query_values_a = utils.create_query_values(
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
    _set_up_std_popularity_func(
        postgres_with_load_and_image_table,
        load_data_query_a,
        {},
        sql_info,
        mock_pg_hook_task,
    )

    sql.upsert_records_to_db_table(
        postgres_conn_id,
        identifier,
        media_type="image",
        sql_info=sql_info,
        task=mock_pg_hook_task,
    )
    postgres_with_load_and_image_table.connection.commit()

    query_values_b = utils.create_query_values(
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
    sql.upsert_records_to_db_table(
        postgres_conn_id,
        identifier,
        media_type="image",
        sql_info=sql_info,
        task=mock_pg_hook_task,
    )
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(f"SELECT * FROM {image_table};")
    actual_rows = postgres_with_load_and_image_table.cursor.fetchall()
    actual_row = actual_rows[0]
    assert len(actual_rows) == 1
    assert actual_row[utils.land_url_idx] == LAND_URL_B
    assert actual_row[utils.thm_idx] == THM_URL_A
    assert actual_row[utils.filesize_idx] == FILESIZE
    assert actual_row[utils.license_idx] == LICENSE_B
    assert actual_row[utils.version_idx] == VERSION_B
    assert actual_row[utils.creator_idx] == CREATOR_A
    assert actual_row[utils.creator_url_idx] == CREATOR_URL_A
    assert actual_row[utils.title_idx] == TITLE_A
    assert actual_row[utils.metadata_idx] == json.loads(META_DATA_A)
    assert actual_row[utils.tags_idx] == json.loads(TAGS)
    assert actual_row[utils.width_idx] == WIDTH_A
    assert actual_row[utils.height_idx] == HEIGHT_A


def test_upsert_records_merges_meta_data(
    postgres_with_load_and_image_table,
    tmpdir,
    load_table,
    image_table,
    sql_info,
    identifier,
    mock_pg_hook_task,
):
    postgres_conn_id = POSTGRES_CONN_ID

    FID = "a"
    PROVIDER = "images_provider"
    IMG_URL = "https://images.com/a/img.jpg"
    LICENSE = "by"

    META_DATA_A = '{"description": "a cool picture", "test": "should stay"}'
    META_DATA_B = '{"description": "I updated my description"}'

    query_values_a = utils.create_query_values(
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

    query_values_b = utils.create_query_values(
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
    _set_up_std_popularity_func(
        postgres_with_load_and_image_table,
        load_data_query_a,
        {},
        sql_info,
        mock_pg_hook_task,
    )

    sql.upsert_records_to_db_table(
        postgres_conn_id,
        identifier,
        media_type="image",
        sql_info=sql_info,
        task=mock_pg_hook_task,
    )
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(f"DELETE FROM {load_table};")
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(load_data_query_b)
    postgres_with_load_and_image_table.connection.commit()
    sql.upsert_records_to_db_table(
        postgres_conn_id,
        identifier,
        media_type="image",
        sql_info=sql_info,
        task=mock_pg_hook_task,
    )
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(f"SELECT * FROM {image_table};")
    actual_rows = postgres_with_load_and_image_table.cursor.fetchall()
    actual_row = actual_rows[0]
    assert len(actual_rows) == 1
    expected_meta_data = json.loads(META_DATA_A)
    expected_meta_data.update(json.loads(META_DATA_B))
    assert actual_row[utils.metadata_idx] == expected_meta_data


def test_upsert_records_does_not_replace_with_null_values_in_meta_data(
    postgres_with_load_and_image_table,
    tmpdir,
    load_table,
    image_table,
    sql_info,
    identifier,
    mock_pg_hook_task,
):
    postgres_conn_id = POSTGRES_CONN_ID

    FID = "a"
    PROVIDER = "images_provider"
    IMG_URL = "https://images.com/a/img.jpg"
    LICENSE = "by"

    META_DATA_A = '{"description": "a cool picture", "test": "should stay"}'
    META_DATA_B = '{"description": "I updated my description", "test": null}'

    query_values_a = utils.create_query_values(
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

    query_values_b = utils.create_query_values(
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
    _set_up_std_popularity_func(
        postgres_with_load_and_image_table,
        load_data_query_a,
        {},
        sql_info,
        mock_pg_hook_task,
    )

    sql.upsert_records_to_db_table(
        postgres_conn_id,
        identifier,
        media_type="image",
        sql_info=sql_info,
        task=mock_pg_hook_task,
    )
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(f"DELETE FROM {load_table};")
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(load_data_query_b)
    postgres_with_load_and_image_table.connection.commit()
    sql.upsert_records_to_db_table(
        postgres_conn_id,
        identifier,
        media_type="image",
        sql_info=sql_info,
        task=mock_pg_hook_task,
    )
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(f"SELECT * FROM {image_table};")
    actual_rows = postgres_with_load_and_image_table.cursor.fetchall()
    actual_row = actual_rows[0]
    assert len(actual_rows) == 1
    expected_meta_data = {
        "description": json.loads(META_DATA_B)["description"],
        "test": json.loads(META_DATA_A)["test"],
    }
    assert actual_row[utils.metadata_idx] == expected_meta_data


def test_upsert_records_merges_tags(
    postgres_with_load_and_image_table,
    tmpdir,
    load_table,
    image_table,
    sql_info,
    identifier,
    mock_pg_hook_task,
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

    query_values_a = utils.create_query_values(
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

    query_values_b = utils.create_query_values(
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
    _set_up_std_popularity_func(
        postgres_with_load_and_image_table,
        load_data_query_a,
        {},
        sql_info,
        mock_pg_hook_task,
    )
    sql.upsert_records_to_db_table(
        postgres_conn_id,
        identifier,
        media_type="image",
        sql_info=sql_info,
        task=mock_pg_hook_task,
    )
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(f"DELETE FROM {load_table};")
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(load_data_query_b)
    postgres_with_load_and_image_table.connection.commit()
    sql.upsert_records_to_db_table(
        postgres_conn_id,
        identifier,
        media_type="image",
        sql_info=sql_info,
        task=mock_pg_hook_task,
    )
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
    actual_tags = actual_row[utils.tags_idx]
    assert len(actual_tags) == 3
    assert all([t in expect_tags for t in actual_tags])
    assert all([t in actual_tags for t in expect_tags])


def test_upsert_records_does_not_replace_tags_with_null(
    postgres_with_load_and_image_table,
    tmpdir,
    load_table,
    image_table,
    sql_info,
    identifier,
    mock_pg_hook_task,
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

    query_values_a = utils.create_query_values(
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

    query_values_b = utils.create_query_values(
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
    _set_up_std_popularity_func(
        postgres_with_load_and_image_table,
        load_data_query_a,
        {},
        sql_info,
        mock_pg_hook_task,
    )
    sql.upsert_records_to_db_table(
        postgres_conn_id,
        identifier,
        media_type="image",
        sql_info=sql_info,
        task=mock_pg_hook_task,
    )
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(f"DELETE FROM {load_table};")
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(load_data_query_b)
    postgres_with_load_and_image_table.connection.commit()
    sql.upsert_records_to_db_table(
        postgres_conn_id,
        identifier,
        media_type="image",
        sql_info=sql_info,
        task=mock_pg_hook_task,
    )
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(f"SELECT * FROM {image_table};")
    actual_rows = postgres_with_load_and_image_table.cursor.fetchall()
    actual_row = actual_rows[0]
    assert len(actual_rows) == 1
    expect_tags = [
        {"name": "tagone", "provider": "test"},
        {"name": "tagtwo", "provider": "test"},
    ]
    actual_tags = actual_row[utils.tags_idx]
    assert len(actual_tags) == 2
    assert all([t in expect_tags for t in actual_tags])
    assert all([t in actual_tags for t in expect_tags])


def test_upsert_records_replaces_null_tags(
    postgres_with_load_and_image_table,
    tmpdir,
    load_table,
    image_table,
    sql_info,
    identifier,
    mock_pg_hook_task,
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
    query_values_a = utils.create_query_values(
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
    query_values_b = utils.create_query_values(
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

    _set_up_std_popularity_func(
        postgres_with_load_and_image_table,
        load_data_query_a,
        {},
        sql_info,
        mock_pg_hook_task,
    )
    sql.upsert_records_to_db_table(
        postgres_conn_id,
        identifier,
        media_type="image",
        sql_info=sql_info,
        task=mock_pg_hook_task,
    )
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(f"DELETE FROM {load_table};")
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(load_data_query_b)
    postgres_with_load_and_image_table.connection.commit()
    sql.upsert_records_to_db_table(
        postgres_conn_id,
        identifier,
        media_type="image",
        sql_info=sql_info,
        task=mock_pg_hook_task,
    )
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
    actual_tags = actual_row[utils.tags_idx]
    assert len(actual_tags) == 2
    assert all([t in expect_tags for t in actual_tags])
    assert all([t in actual_tags for t in expect_tags])


def test_upsert_records_handles_duplicate_url_and_does_not_merge(
    postgres_with_load_and_image_table,
    tmpdir,
    load_table,
    image_table,
    sql_info,
    identifier,
    mock_pg_hook_task,
):
    postgres_conn_id = POSTGRES_CONN_ID

    PROVIDER = "images_provider"
    IMG_URL = "https://images.com/a/img.jpg"
    LICENSE = "by"

    FID_A = "a"
    META_DATA_A = '{"description": "a cool picture", "test": "should stay"}'

    FID_B = "b"
    META_DATA_B = '{"description": "the same cool picture"}'

    # A and B have different foreign identifiers, but the same url
    query_values_a = utils.create_query_values(
        {
            col.FOREIGN_ID.db_name: FID_A,
            col.DIRECT_URL.db_name: IMG_URL,
            col.LICENSE.db_name: LICENSE,
            col.META_DATA.db_name: META_DATA_A,
            col.PROVIDER.db_name: PROVIDER,
        }
    )
    load_data_query_a = f"""INSERT INTO {load_table} VALUES(
        {query_values_a}
    );"""

    query_values_b = utils.create_query_values(
        {
            col.FOREIGN_ID.db_name: FID_B,
            col.DIRECT_URL.db_name: IMG_URL,
            col.LICENSE.db_name: LICENSE,
            col.META_DATA.db_name: META_DATA_B,
            col.PROVIDER.db_name: PROVIDER,
        }
    )
    load_data_query_b = f"""INSERT INTO {load_table} VALUES(
        {query_values_b}
        );"""

    # Simulate a DAG run where A is ingested into the loading table, upserted into
    # the image table, and finally the loading table is cleared for the next DAG run.
    _set_up_std_popularity_func(
        postgres_with_load_and_image_table,
        load_data_query_a,
        {},
        sql_info,
        mock_pg_hook_task,
    )
    sql.upsert_records_to_db_table(
        postgres_conn_id,
        identifier,
        media_type="image",
        sql_info=sql_info,
        task=mock_pg_hook_task,
    )
    postgres_with_load_and_image_table.connection.commit()
    postgres_with_load_and_image_table.cursor.execute(f"DELETE FROM {load_table};")
    postgres_with_load_and_image_table.connection.commit()

    # Simulate a second DAG run where B is ingested into the loading table, and we
    # attempt to upsert it into the image table which already contains A.
    postgres_with_load_and_image_table.cursor.execute(load_data_query_b)
    postgres_with_load_and_image_table.connection.commit()
    sql.upsert_records_to_db_table(
        postgres_conn_id,
        identifier,
        media_type="image",
        sql_info=sql_info,
        task=mock_pg_hook_task,
    )
    postgres_with_load_and_image_table.connection.commit()

    # Now check the final state of the image table. If we get here, the duplicate key
    # violation was successfully caught.
    postgres_with_load_and_image_table.cursor.execute(f"SELECT * FROM {image_table};")
    actual_rows = postgres_with_load_and_image_table.cursor.fetchall()
    actual_row = actual_rows[0]
    # There should only be one row (B should not have been inserted)
    assert len(actual_rows) == 1
    # No data in A should have been updated or merged
    expected_meta_data = json.loads(META_DATA_A)
    assert actual_row[utils.metadata_idx] == expected_meta_data
    assert actual_row[utils.fid_idx] == "a"


def test_upsert_records_handles_duplicate_urls_in_a_single_batch_and_does_not_merge(
    postgres_with_load_and_image_table,
    tmpdir,
    load_table,
    image_table,
    sql_info,
    identifier,
    mock_pg_hook_task,
):
    postgres_conn_id = POSTGRES_CONN_ID

    PROVIDER = "images_provider"
    IMG_URL = "https://images.com/a/img.jpg"
    LICENSE = "by"

    FID_A = "a"
    META_DATA_A = '{"description": "a cool picture", "test": "should stay"}'
    FID_B = "b"
    META_DATA_B = '{"description": "the same cool picture"}'
    FID_C = "c"
    META_DATA_C = '{"description": "Definitely not a duplicate!"}'
    IMG_URL_C = "https://images.com/c/img.jpg"

    # A and B have different foreign identifiers, but the same url
    query_values_a = utils.create_query_values(
        {
            col.FOREIGN_ID.db_name: FID_A,
            col.DIRECT_URL.db_name: IMG_URL,
            col.LICENSE.db_name: LICENSE,
            col.META_DATA.db_name: META_DATA_A,
            col.PROVIDER.db_name: PROVIDER,
        }
    )
    load_data_query_a = f"""INSERT INTO {load_table} VALUES(
        {query_values_a}
    );"""

    query_values_b = utils.create_query_values(
        {
            col.FOREIGN_ID.db_name: FID_B,
            col.DIRECT_URL.db_name: IMG_URL,
            col.LICENSE.db_name: LICENSE,
            col.META_DATA.db_name: META_DATA_B,
            col.PROVIDER.db_name: PROVIDER,
        }
    )
    load_data_query_b = f"""INSERT INTO {load_table} VALUES(
        {query_values_b}
        );"""

    # C is not a duplicate of anything, just a normal image
    query_values_c = utils.create_query_values(
        {
            col.FOREIGN_ID.db_name: FID_C,
            col.DIRECT_URL.db_name: IMG_URL_C,
            col.LICENSE.db_name: LICENSE,
            col.META_DATA.db_name: META_DATA_C,
            col.PROVIDER.db_name: PROVIDER,
        }
    )
    load_data_query_c = f"""INSERT INTO {load_table} VALUES(
        {query_values_c}
        );"""

    # Simulate a DAG run where duplicates (A and B) and a non-duplicate (C) are all
    # ingested in a single batch from the provider script, and we attempt to upsert
    # all into the image table.
    postgres_with_load_and_image_table.cursor.execute(load_data_query_c)
    postgres_with_load_and_image_table.cursor.execute(load_data_query_a)
    postgres_with_load_and_image_table.cursor.execute(load_data_query_b)
    postgres_with_load_and_image_table.connection.commit()

    # Confirm that all three made it to the loading table.
    postgres_with_load_and_image_table.cursor.execute(f"SELECT * FROM {load_table};")
    rows = postgres_with_load_and_image_table.cursor.fetchall()
    assert len(rows) == 3

    _set_up_std_popularity_func(
        postgres_with_load_and_image_table,
        None,
        {},
        sql_info,
        mock_pg_hook_task,
    )
    # Now try upserting the records from the loading table to the final image table.
    sql.upsert_records_to_db_table(
        postgres_conn_id,
        identifier,
        media_type="image",
        sql_info=sql_info,
        task=mock_pg_hook_task,
    )
    postgres_with_load_and_image_table.connection.commit()

    # Now check the final state of the image table. If we get here, the duplicate key
    # violation was successfully caught.
    postgres_with_load_and_image_table.cursor.execute(f"SELECT * FROM {image_table};")
    actual_rows = postgres_with_load_and_image_table.cursor.fetchall()
    # There should be two rows (only the first duplicate and the normal row should be inserted)
    assert len(actual_rows) == 2
    # No data in A should have been updated or merged
    expected_meta_data = json.loads(META_DATA_A)
    assert actual_rows[0][utils.metadata_idx] == expected_meta_data
    assert actual_rows[0][utils.fid_idx] == "a"
    assert actual_rows[1][utils.fid_idx] == "c"


def test_upsert_records_calculates_standardized_popularity(
    postgres_with_load_and_image_table,
    tmpdir,
    load_table,
    image_table,
    identifier,
    sql_info,
    mock_pg_hook_task,
):
    postgres_conn_id = POSTGRES_CONN_ID

    PROVIDER = "images_provider"
    FID_A = "fid_a"
    FID_B = "fid_b"
    FID_C = "fid_c"

    # To test standardized popularity calculation, we want to have existing popularity
    # data. This query will be used to insert a few rows into the image table.
    data_query = dedent(
        f"""
        INSERT INTO {image_table} (
          created_on, updated_on, provider, foreign_identifier, url,
          meta_data, license, removed_from_source
        )
        VALUES
          (
            NOW(), NOW(), '{PROVIDER}', '{FID_A}', 'https://test.com/a.jpg',
            '{{"views": 0, "description": "cats"}}', 'cc0', false
          ),
          (
            NOW(), NOW(), '{PROVIDER}', '{FID_B}', 'https://test.com/b.jpg',
            '{{"views": 50, "description": "cats"}}', 'cc0', false
          )
        ;
        """
    )

    # Sample data to insert into the `image_popularity_metrics` table, so that popularity
    # constants will be calculated for our fake provider.
    metrics = {
        PROVIDER: {"metric": "views", "percentile": 0.8},
    }

    # Now we re-set up the popularity constants tables, views, and functions after running
    # the `data_query` to insert our test rows, which will initially have `null` standardized
    # popularity (because no popularity constants exist). Then it will insert `metrics` into
    # the `image_popularity_metrics` table, and calculate a value for the popularity constant
    # for PROVIDER using those initial records.
    # Then it sets up the standardized popularity function itself.
    _set_up_std_popularity_func(
        postgres_with_load_and_image_table,
        data_query,
        metrics,
        sql_info,
        mock_pg_hook_task,
    )

    # Now we want to try to upsert some records into the db. We want to update one of the existing
    # records, and also insert a new one.

    # A record matching one of our existing records into the load table.
    query_values_update_old_record = utils.create_query_values(
        {
            col.FOREIGN_ID.db_name: FID_A,  # Matching a record that was already inserted
            col.DIRECT_URL.db_name: "https://test.com/a.jpg",
            col.LICENSE.db_name: "cc0",
            col.META_DATA.db_name: '{"views": 10, "description": "cats"}',  # Update the number of views
            col.PROVIDER.db_name: PROVIDER,
        }
    )

    # A brand new record into the load table.
    query_values_update_new_record = utils.create_query_values(
        {
            col.FOREIGN_ID.db_name: FID_C,
            col.DIRECT_URL.db_name: "https://test.com/z.jpg",
            col.LICENSE.db_name: "cc0",
            col.META_DATA.db_name: '{"views": 20, "description": "dogs"}',
            col.PROVIDER.db_name: PROVIDER,
        }
    )

    # Queries to insert the two records into the load table.
    load_data_query_old_record = f"""INSERT INTO {load_table} VALUES(
        {query_values_update_old_record}
    );"""

    load_data_query_new_record = f"""INSERT INTO {load_table} VALUES(
        {query_values_update_new_record}
    );"""

    # Now actually insert the records into the load table. This simulates a DagRun which ingests both
    # records.
    postgres_with_load_and_image_table.cursor.execute(load_data_query_old_record)
    postgres_with_load_and_image_table.cursor.execute(load_data_query_new_record)
    postgres_with_load_and_image_table.connection.commit()

    # Confirm that both made it to the loading table.
    postgres_with_load_and_image_table.cursor.execute(f"SELECT * FROM {load_table};")
    rows = postgres_with_load_and_image_table.cursor.fetchall()
    assert len(rows) == 2

    # Now try upserting the records from the loading table to the final image table. Standardized popularity
    # should be calculated for both records.
    sql.upsert_records_to_db_table(
        postgres_conn_id,
        identifier,
        media_type="image",
        sql_info=sql_info,
        task=mock_pg_hook_task,
    )
    postgres_with_load_and_image_table.connection.commit()

    # Now check the final state of the image table. We expect there to be three rows total.
    postgres_with_load_and_image_table.cursor.execute(f"SELECT * FROM {image_table};")
    actual_rows = postgres_with_load_and_image_table.cursor.fetchall()
    assert len(actual_rows) == 3

    # This record was present on the image table but was not updated, so it still has null popularity.
    assert actual_rows[0][utils.fid_idx] == FID_B
    assert actual_rows[0][utils.standardized_popularity_idx] is None

    # This is the row that was updated; it should have standardized popularity calculated based on its
    # updated raw popularity score, rather than the initial raw score.
    assert actual_rows[1][utils.fid_idx] == FID_A
    assert actual_rows[1][utils.standardized_popularity_idx] == 0.44444444444444453

    # This is the new record
    assert actual_rows[2][utils.fid_idx] == FID_C
    assert actual_rows[2][utils.standardized_popularity_idx] == 0.6153846153846154


def test_drop_load_table_drops_table(postgres_with_load_table, load_table, identifier):
    postgres_conn_id = POSTGRES_CONN_ID
    sql.drop_load_table(postgres_conn_id, identifier)
    check_query = (
        f"SELECT EXISTS (" f"SELECT FROM pg_tables WHERE tablename='{load_table}');"
    )
    postgres_with_load_table.cursor.execute(check_query)
    check_result = postgres_with_load_table.cursor.fetchone()[0]
    assert not check_result


@pytest.mark.parametrize(
    "value, expected",
    [
        (123, 123),
        ("500 rows imported into relation '...' from file ... of ... bytes", 500),
    ],
)
def test_handle_s3_load_result(value, expected):
    cursor_mock = mock.Mock()
    cursor_mock.fetchone.return_value = (value,)
    actual = sql._handle_s3_load_result(cursor_mock)
    assert actual == expected

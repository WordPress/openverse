import logging

import psycopg2
import pytest

from catalog.tests.test_utils import sql
from common.storage import columns as col
from common.storage.db_columns import DELETED_IMAGE_TABLE_COLUMNS, IMAGE_TABLE_COLUMNS
from database.delete_records.delete_records import (
    create_deleted_records,
    delete_records_from_media_table,
    notify_slack,
)


logger = logging.getLogger(__name__)


FID_A = "a"
FID_B = "b"
FID_C = "c"
MATCHING_PROVIDER = "foo"
NOT_MATCHING_PROVIDER = "bar"
TITLE = "test title"
LICENSE = "by"


@pytest.fixture
def identifier(request):
    return f"{hash(request.node.name)}".replace("-", "_")


@pytest.fixture
def image_table(identifier):
    # Parallelized tests need to use distinct database tables
    return f"image_{identifier}"


@pytest.fixture
def deleted_image_table(identifier):
    return f"deleted_image_{identifier}"


@pytest.fixture
def postgres_with_image_and_deleted_image_table(image_table, deleted_image_table):
    conn = psycopg2.connect(sql.POSTGRES_TEST_URI)
    cur = conn.cursor()
    drop_table_query = f"""
    DROP TABLE IF EXISTS {image_table} CASCADE;
    DROP TABLE IF EXISTS {deleted_image_table} CASCADE;
    """
    cur.execute(drop_table_query)
    cur.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;')
    cur.execute(sql.CREATE_IMAGE_TABLE_QUERY.format(image_table))
    cur.execute(sql.CREATE_DELETED_IMAGE_TABLE_QUERY.format(deleted_image_table))

    conn.commit()

    yield sql.PostgresRef(cursor=cur, connection=conn)

    cur.execute(drop_table_query)

    cur.close()
    conn.commit()
    conn.close()


def _load_sample_data_into_image_table(image_table, postgres):
    DEFAULT_COLS = {
        col.LICENSE.db_name: LICENSE,
        col.UPDATED_ON.db_name: "NOW()",
        col.CREATED_ON.db_name: "NOW()",
        col.TITLE.db_name: TITLE,
    }

    # Load sample data into the image table
    sample_records = [
        {
            col.FOREIGN_ID.db_name: FID_A,
            col.DIRECT_URL.db_name: f"https://images.com/{FID_A}/img.jpg",
            col.PROVIDER.db_name: MATCHING_PROVIDER,
        },
        {
            col.FOREIGN_ID.db_name: FID_B,
            col.DIRECT_URL.db_name: f"https://images.com/{FID_B}/img.jpg",
            col.PROVIDER.db_name: MATCHING_PROVIDER,
        },
        {
            col.FOREIGN_ID.db_name: FID_C,
            col.DIRECT_URL.db_name: f"https://images.com/{FID_C}/img.jpg",
            col.PROVIDER.db_name: NOT_MATCHING_PROVIDER,
        },
    ]

    sql.load_sample_data_into_image_table(
        image_table, postgres, [{**record, **DEFAULT_COLS} for record in sample_records]
    )


def test_create_deleted_records(
    postgres_with_image_and_deleted_image_table,
    image_table,
    deleted_image_table,
    identifier,
):
    # Load sample data into the image table
    _load_sample_data_into_image_table(
        image_table,
        postgres_with_image_and_deleted_image_table,
    )

    # Delete records matching the MATCHING_PROVIDER
    select_query = f"WHERE provider='{MATCHING_PROVIDER}'"
    deleted_reason = "FOO"
    deleted_count = create_deleted_records.function(
        media_type=image_table,
        select_query=select_query,
        deleted_reason=deleted_reason,
        db_columns=IMAGE_TABLE_COLUMNS,
        deleted_db_columns=DELETED_IMAGE_TABLE_COLUMNS,
        postgres_conn_id=sql.POSTGRES_CONN_ID,
    )

    # Both records A and B should have been added to the deleted image table
    assert deleted_count == 2

    postgres_with_image_and_deleted_image_table.cursor.execute(
        f"SELECT * FROM {deleted_image_table};"
    )
    actual_rows = postgres_with_image_and_deleted_image_table.cursor.fetchall()

    assert len(actual_rows) == 2

    # They should both retain the fields of the original record, and have
    # the deleted_reason set appropriately.
    assert actual_rows[0][sql.fid_idx] == FID_A
    assert actual_rows[0][sql.title_idx] == TITLE
    assert actual_rows[0][sql.license_idx] == LICENSE
    assert actual_rows[0][sql.deleted_reason_idx] == deleted_reason

    assert actual_rows[1][sql.fid_idx] == FID_B
    assert actual_rows[1][sql.title_idx] == TITLE
    assert actual_rows[1][sql.license_idx] == LICENSE
    assert actual_rows[1][sql.deleted_reason_idx] == deleted_reason


def test_create_deleted_records_with_query_matching_no_rows(
    postgres_with_image_and_deleted_image_table,
    image_table,
    deleted_image_table,
    identifier,
):
    # Load sample data into the image table
    _load_sample_data_into_image_table(
        image_table,
        postgres_with_image_and_deleted_image_table,
    )

    # Try to delete records matching a condition that does not exist
    select_query = "WHERE provider='NONEXISTENT_PROVIDER'"
    deleted_reason = "FOO"
    deleted_count = create_deleted_records.function(
        media_type=image_table,
        select_query=select_query,
        deleted_reason=deleted_reason,
        db_columns=IMAGE_TABLE_COLUMNS,
        deleted_db_columns=DELETED_IMAGE_TABLE_COLUMNS,
        postgres_conn_id=sql.POSTGRES_CONN_ID,
    )

    # No records should have been added to the deleted image table
    assert deleted_count == 0

    postgres_with_image_and_deleted_image_table.cursor.execute(
        f"SELECT * FROM {deleted_image_table};"
    )
    actual_rows = postgres_with_image_and_deleted_image_table.cursor.fetchall()

    assert len(actual_rows) == 0


def test_delete_records_from_media_table(
    postgres_with_image_and_deleted_image_table,
    image_table,
    deleted_image_table,
    identifier,
):
    # Load sample data into the image table
    _load_sample_data_into_image_table(
        image_table,
        postgres_with_image_and_deleted_image_table,
    )

    # Delete records matching the MATCHING_PROVIDER
    select_query = f"WHERE provider='{MATCHING_PROVIDER}'"
    deleted_count = delete_records_from_media_table.function(
        table=image_table,
        select_query=select_query,
        postgres_conn_id=sql.POSTGRES_CONN_ID,
    )

    # Both records A and B should have been deleted
    assert deleted_count == 2

    postgres_with_image_and_deleted_image_table.cursor.execute(
        f"SELECT * FROM {image_table};"
    )
    actual_rows = postgres_with_image_and_deleted_image_table.cursor.fetchall()

    # There is only one record left in the image table
    assert len(actual_rows) == 1

    # They should both retain the fields of the original record, and have
    # the deleted_reason set appropriately.
    assert actual_rows[0][sql.fid_idx] == FID_C
    assert actual_rows[0][sql.title_idx] == TITLE
    assert actual_rows[0][sql.license_idx] == LICENSE


def test_delete_no_records_from_media_table(
    postgres_with_image_and_deleted_image_table,
    image_table,
    deleted_image_table,
    identifier,
):
    # Load sample data into the image table
    _load_sample_data_into_image_table(
        image_table,
        postgres_with_image_and_deleted_image_table,
    )

    # Try to delete records using a query that matches nothing
    select_query = "WHERE provider='NONEXISTENT_PROVIDER'"
    deleted_count = delete_records_from_media_table.function(
        table=image_table,
        select_query=select_query,
        postgres_conn_id=sql.POSTGRES_CONN_ID,
    )

    # No records should have been deleted
    assert deleted_count == 0

    postgres_with_image_and_deleted_image_table.cursor.execute(
        f"SELECT * FROM {image_table};"
    )
    actual_rows = postgres_with_image_and_deleted_image_table.cursor.fetchall()

    # All three records are left in the image table
    assert len(actual_rows) == 3


def test_notify_slack():
    message = notify_slack.function(123456789, "audio", "WHERE provider='foo';")
    assert message == (
        "Deleted 123,456,789 records from the `audio` table matching query: "
        "`WHERE provider='foo';`"
    )

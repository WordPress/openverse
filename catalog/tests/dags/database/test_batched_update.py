import logging

import psycopg2
import pytest
from airflow.models import Variable

from common.storage import columns as col
from database.batched_update import constants
from database.batched_update.batched_update import (
    get_expected_update_count,
    notify_slack,
    update_batches,
)
from tests.test_utils import sql


logger = logging.getLogger(__name__)


FID_A = "a"
FID_B = "b"
FID_C = "c"
MATCHING_PROVIDER = "foo"
NOT_MATCHING_PROVIDER = "bar"
OLD_TITLE = "old title"
NEW_TITLE = "new title"
LICENSE = "by"


@pytest.fixture
def identifier(request):
    return f"{hash(request.node.name)}".replace("-", "_")


@pytest.fixture
def batch_start_var(identifier):
    return f"test_{identifier}_batch_start"


@pytest.fixture
def image_table(identifier):
    # Parallelized tests need to use distinct database tables
    return f"image_{identifier}"


@pytest.fixture
def temp_table(identifier):
    return f"test_{identifier}_rows_to_update"


@pytest.fixture
def postgres_with_image_and_temp_table(batch_start_var, image_table, temp_table):
    conn = psycopg2.connect(sql.POSTGRES_TEST_URI)
    cur = conn.cursor()
    drop_table_query = f"""
    DROP TABLE IF EXISTS {image_table} CASCADE;
    DROP TABLE IF EXISTS {temp_table} CASCADE;
    """
    cur.execute(drop_table_query)
    cur.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;')
    # The temp table is created as part of tests.
    cur.execute(sql.CREATE_IMAGE_TABLE_QUERY.format(image_table))

    conn.commit()

    yield sql.PostgresRef(cursor=cur, connection=conn)

    cur.execute(drop_table_query)
    # Drop the test airflow variable
    Variable.delete(batch_start_var)

    cur.close()
    conn.commit()
    conn.close()


def _load_sample_data_into_image_table(image_table, postgres):
    DEFAULT_COLS = {
        col.LICENSE.db_name: LICENSE,
        col.UPDATED_ON.db_name: "NOW()",
        col.CREATED_ON.db_name: "NOW()",
        col.TITLE.db_name: OLD_TITLE,
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


@pytest.mark.parametrize(
    "total_row_count",
    (
        # Simulate a 'normal' flow, where the total count is passed into
        # the task via XCOM after creating the table
        3,
        # Simulate a DagRun that is using `resume_update` to skip creating a
        # new table, so None is passed in from XCOM and we need to run a
        # `SELECT COUNT(*)` on the temp table
        None,
    ),
)
def test_get_expected_update_count(
    postgres_with_image_and_temp_table,
    image_table,
    temp_table,
    identifier,
    total_row_count,
):
    # Load sample data into the image table
    _load_sample_data_into_image_table(
        image_table,
        postgres_with_image_and_temp_table,
    )

    # Create the temp table with a query that will select all records
    select_query = f"WHERE title='{OLD_TITLE}'"
    create_temp_table_query = constants.CREATE_TEMP_TABLE_QUERY.format(
        temp_table_name=temp_table, table_name=image_table, select_query=select_query
    )
    postgres_with_image_and_temp_table.cursor.execute(create_temp_table_query)
    postgres_with_image_and_temp_table.connection.commit()

    total_count = get_expected_update_count.function(
        query_id=f"test_{identifier}", total_row_count=total_row_count, dry_run=False
    )

    assert total_count == 3


def test_update_batches(
    postgres_with_image_and_temp_table,
    image_table,
    temp_table,
    identifier,
    batch_start_var,
):
    # Load sample data into the image table
    _load_sample_data_into_image_table(
        image_table,
        postgres_with_image_and_temp_table,
    )

    # Create the temp table with a query that will select records A and B
    select_query = f"WHERE provider='{MATCHING_PROVIDER}'"
    create_temp_table_query = constants.CREATE_TEMP_TABLE_QUERY.format(
        temp_table_name=temp_table, table_name=image_table, select_query=select_query
    )
    postgres_with_image_and_temp_table.cursor.execute(create_temp_table_query)
    postgres_with_image_and_temp_table.connection.commit()

    # Test update query
    update_query = f"SET title='{NEW_TITLE}'"
    updated_count = update_batches.function(
        dry_run=False,
        query_id=f"test_{identifier}",
        table_name=image_table,
        total_row_count=2,
        batch_size=1,
        update_query=update_query,
        update_timeout=3600,
        batch_start_var=batch_start_var,
        postgres_conn_id=sql.POSTGRES_CONN_ID,
    )

    # Both records A and C should be updated
    assert updated_count == 2

    postgres_with_image_and_temp_table.cursor.execute(f"SELECT * FROM {image_table};")
    actual_rows = postgres_with_image_and_temp_table.cursor.fetchall()

    assert len(actual_rows) == 3
    # This is the row that did not match the initial select_query, and will
    # therefore not be updated regardless of whether it is a dry run
    assert actual_rows[0][sql.fid_idx] == FID_C
    assert actual_rows[0][sql.title_idx] == OLD_TITLE

    # These are the updated rows
    assert actual_rows[1][sql.fid_idx] == FID_A
    assert actual_rows[1][sql.title_idx] == NEW_TITLE
    assert actual_rows[2][sql.fid_idx] == FID_B
    assert actual_rows[2][sql.title_idx] == NEW_TITLE


def test_update_batches_dry_run(
    postgres_with_image_and_temp_table,
    image_table,
    temp_table,
    identifier,
    batch_start_var,
):
    # Load sample data into the image table
    _load_sample_data_into_image_table(
        image_table,
        postgres_with_image_and_temp_table,
    )

    # Create the temp table with a query that will select records A and B
    select_query = f"WHERE provider='{MATCHING_PROVIDER}'"
    create_temp_table_query = constants.CREATE_TEMP_TABLE_QUERY.format(
        temp_table_name=temp_table, table_name=image_table, select_query=select_query
    )
    postgres_with_image_and_temp_table.cursor.execute(create_temp_table_query)
    postgres_with_image_and_temp_table.connection.commit()

    # Test update query
    update_query = f"SET title='{NEW_TITLE}'"
    updated_count = update_batches.function(
        dry_run=True,
        query_id=f"test_{identifier}",
        table_name=image_table,
        total_row_count=2,
        batch_size=1,
        update_query=update_query,
        update_timeout=3600,
        batch_start_var=batch_start_var,
        postgres_conn_id=sql.POSTGRES_CONN_ID,
    )

    # No records should be updated
    assert updated_count == 0

    postgres_with_image_and_temp_table.cursor.execute(f"SELECT * FROM {image_table};")
    actual_rows = postgres_with_image_and_temp_table.cursor.fetchall()

    assert len(actual_rows) == 3
    for row in actual_rows:
        assert row[sql.title_idx] == OLD_TITLE


def test_update_batches_resuming_from_batch_start(
    postgres_with_image_and_temp_table,
    image_table,
    temp_table,
    identifier,
    batch_start_var,
):
    # Load sample data into the image table
    _load_sample_data_into_image_table(
        image_table,
        postgres_with_image_and_temp_table,
    )

    # Create the temp table with a query that will select all three records
    select_query = f"WHERE title='{OLD_TITLE}'"
    create_temp_table_query = constants.CREATE_TEMP_TABLE_QUERY.format(
        temp_table_name=temp_table, table_name=image_table, select_query=select_query
    )
    postgres_with_image_and_temp_table.cursor.execute(create_temp_table_query)
    postgres_with_image_and_temp_table.connection.commit()

    # Set the batch_start Airflow variable to 1, to skip the first
    # record
    Variable.set(batch_start_var, 1)

    update_query = f"SET title='{NEW_TITLE}'"
    updated_count = update_batches.function(
        dry_run=False,
        query_id=f"test_{identifier}",
        table_name=image_table,
        total_row_count=3,
        batch_size=1,
        update_query=update_query,
        update_timeout=3600,
        batch_start_var=batch_start_var,
        postgres_conn_id=sql.POSTGRES_CONN_ID,
    )

    # Only records B and C should have been updated
    assert updated_count == 2

    postgres_with_image_and_temp_table.cursor.execute(f"SELECT * FROM {image_table};")
    actual_rows = postgres_with_image_and_temp_table.cursor.fetchall()

    assert len(actual_rows) == 3
    # This is the first row, that was skipped by setting the batch_start to 1
    assert actual_rows[0][sql.fid_idx] == FID_A
    assert actual_rows[0][sql.title_idx] == OLD_TITLE

    # These are the updated rows
    assert actual_rows[1][sql.fid_idx] == FID_B
    assert actual_rows[1][sql.title_idx] == NEW_TITLE
    assert actual_rows[2][sql.fid_idx] == FID_C
    assert actual_rows[2][sql.title_idx] == NEW_TITLE


@pytest.mark.parametrize(
    "text, count, expected_message",
    [
        ("Updated {count} records", 1000000, "Updated 1,000,000 records"),
        (
            "Updated {count} records",
            2,
            "Updated 2 records",
        ),
        (
            "A message without a count",
            None,
            "A message without a count",
        ),
    ],
)
def test_notify_slack(text, count, expected_message):
    actual_message = notify_slack.function(text, True, count)
    assert actual_message == expected_message

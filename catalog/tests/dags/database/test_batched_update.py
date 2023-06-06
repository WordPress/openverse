import logging
import uuid

import psycopg2
import pytest

from catalog.tests.test_utils import sql
from common.storage import columns as col
from common.storage.db_columns import IMAGE_TABLE_COLUMNS
from database.batched_update import constants
from database.batched_update.batched_update import update_batches


logger = logging.getLogger(__name__)


@pytest.fixture
def identifier(request):
    return f"{hash(request.node.name)}".replace("-", "_")


@pytest.fixture
def image_table(identifier):
    # Parallelized tests need to use distinct database tables
    return f"image_{identifier}"


@pytest.fixture
def temp_table(identifier):
    return f"test_{identifier}_rows_to_update"


@pytest.fixture
def postgres_with_image_and_temp_table(image_table, temp_table):
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
    cur.close()
    conn.commit()
    conn.close()


def _get_insert_query(image_table, values: dict):
    # Append the required identifier
    values[col.IDENTIFIER.db_name] = uuid.uuid4()

    query_values = sql.create_query_values(values, columns=IMAGE_TABLE_COLUMNS)

    return f"INSERT INTO {image_table} VALUES({query_values});"


@pytest.mark.parametrize("dry_run, should_run", [(True, False), (False, True)])
def test_update_batches(
    postgres_with_image_and_temp_table,
    image_table,
    temp_table,
    identifier,
    dry_run,
    should_run,
):
    MATCHING_PROVIDER = "foo"
    NOT_MATCHING_PROVIDER = "bar"
    LICENSE = "by"

    OLD_TITLE = "old title"
    NEW_TITLE = "new title"

    FID_A = "a"
    FID_B = "b"
    FID_C = "c"

    DEFAULT_COLS = {
        col.LICENSE.db_name: LICENSE,
        col.TITLE.db_name: OLD_TITLE,
        col.UPDATED_ON.db_name: "NOW()",
        col.CREATED_ON.db_name: "NOW()",
    }
    # Create some records in the image table
    # A and B are records that will match our SELECT, C will not.
    load_data_query_a = _get_insert_query(
        image_table,
        {
            col.FOREIGN_ID.db_name: FID_A,
            col.DIRECT_URL.db_name: f"https://images.com/{FID_A}/img.jpg",
            col.PROVIDER.db_name: MATCHING_PROVIDER,
            **DEFAULT_COLS,
        },
    )

    load_data_query_b = _get_insert_query(
        image_table,
        {
            col.FOREIGN_ID.db_name: FID_B,
            col.DIRECT_URL.db_name: f"https://images.com/{FID_B}/img.jpg",
            col.PROVIDER.db_name: MATCHING_PROVIDER,
            **DEFAULT_COLS,
        },
    )

    # C is not a duplicate of anything, just a normal image
    load_data_query_c = _get_insert_query(
        image_table,
        {
            col.FOREIGN_ID.db_name: FID_C,
            col.DIRECT_URL.db_name: f"https://images.com/{FID_C}/img.jpg",
            col.PROVIDER.db_name: NOT_MATCHING_PROVIDER,
            **DEFAULT_COLS,
        },
    )

    # Load the records into the image table
    postgres_with_image_and_temp_table.cursor.execute(load_data_query_c)
    postgres_with_image_and_temp_table.cursor.execute(load_data_query_a)
    postgres_with_image_and_temp_table.cursor.execute(load_data_query_b)
    postgres_with_image_and_temp_table.connection.commit()

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
        dry_run=dry_run,
        query_id=f"test_{identifier}",
        table_name=image_table,
        expected_row_count=2,
        batch_size=1,
        update_query=update_query,
        update_timeout=3600,
        postgres_conn_id=sql.POSTGRES_CONN_ID,
    )

    # Both records A and C should be updated if this is not a dry_run;
    # otherwise, neither should be updated
    expected_updated_count = 2 if should_run else 0
    expected_title = NEW_TITLE if should_run else OLD_TITLE

    assert updated_count == expected_updated_count

    postgres_with_image_and_temp_table.cursor.execute(f"SELECT * FROM {image_table};")
    actual_rows = postgres_with_image_and_temp_table.cursor.fetchall()

    assert len(actual_rows) == 3
    # This is the row that did not match the initial select_query, and will
    # therefore not be updated regardless of whether it is a dry run
    assert actual_rows[0][sql.fid_idx] == FID_C
    assert actual_rows[0][sql.title_idx] == OLD_TITLE

    # These are the updated rows
    assert actual_rows[1][sql.fid_idx] == FID_A
    assert actual_rows[1][sql.title_idx] == expected_title
    assert actual_rows[2][sql.fid_idx] == FID_B
    assert actual_rows[2][sql.title_idx] == expected_title

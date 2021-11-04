import os
from collections import namedtuple
from textwrap import dedent

import psycopg2
import pytest
from common.popularity import sql


TEST_ID = "testing"
POSTGRES_CONN_ID = os.getenv("TEST_CONN_ID")
POSTGRES_TEST_URI = os.getenv("AIRFLOW_CONN_POSTGRES_OPENLEDGER_TESTING")
TEST_IMAGE_VIEW = f"image_view_{TEST_ID}"
TEST_CONSTANTS = f"image_popularity_constants_{TEST_ID}"
TEST_METRICS = f"image_popularity_metrics_{TEST_ID}"
TEST_IMAGE_TABLE = f"image_{TEST_ID}"
TEST_STANDARDIZED_POPULARITY = f"standardized_popularity_{TEST_ID}"
TEST_POPULARITY_PERCENTILE = f"popularity_percentile_{TEST_ID}"
TEST_POPULARITY_CONSTANTS_IDX = "test_popularity_constants_idx"
TEST_IMAGE_VIEW_ID_IDX = "test_view_id_idx"
TEST_IMAGE_VIEW_PROVIDER_FID_IDX = "test_view_provider_fid_idx"

UUID_FUNCTION_QUERY = 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;'

DROP_IMAGE_TABLE_QUERY = f"DROP TABLE IF EXISTS {TEST_IMAGE_TABLE} CASCADE;"

CREATE_IMAGE_TABLE_QUERY = (
    f"CREATE TABLE public.{TEST_IMAGE_TABLE} ("
    "identifier uuid PRIMARY KEY DEFAULT public.uuid_generate_v4(),"
    "created_on timestamp with time zone NOT NULL,"
    "updated_on timestamp with time zone NOT NULL,"
    "ingestion_type character varying(80),"
    "provider character varying(80),"
    "source character varying(80),"
    "foreign_identifier character varying(3000),"
    "foreign_landing_url character varying(1000),"
    "url character varying(3000) NOT NULL,"
    "thumbnail character varying(3000),"
    "width integer,"
    "height integer,"
    "filesize integer,"
    "license character varying(50) NOT NULL,"
    "license_version character varying(25),"
    "creator character varying(2000),"
    "creator_url character varying(2000),"
    "title character varying(5000),"
    "meta_data jsonb,"
    "tags jsonb,"
    "watermarked boolean,"
    "last_synced_with_source timestamp with time zone,"
    "removed_from_source boolean NOT NULL"
    ");"
)

UNIQUE_CONDITION_QUERY = (
    f"CREATE UNIQUE INDEX {TEST_IMAGE_TABLE}_provider_fid_idx"
    f" ON public.{TEST_IMAGE_TABLE}"
    " USING btree (provider, md5(foreign_identifier));"
)

DROP_TEST_RELATIONS_QUERY = f"""
    DROP MATERIALIZED VIEW IF EXISTS {TEST_IMAGE_VIEW} CASCADE;
    DROP MATERIALIZED VIEW IF EXISTS {TEST_CONSTANTS} CASCADE;
    DROP TABLE IF EXISTS {TEST_METRICS} CASCADE;
    DROP TABLE IF EXISTS {TEST_IMAGE_TABLE} CASCADE;
    DROP FUNCTION IF EXISTS {TEST_STANDARDIZED_POPULARITY} CASCADE;
    DROP FUNCTION IF EXISTS {TEST_POPULARITY_PERCENTILE} CASCADE;
    """


@pytest.fixture
def postgres_with_image_table():
    Postgres = namedtuple("Postgres", ["cursor", "connection"])
    conn = psycopg2.connect(POSTGRES_TEST_URI)
    cur = conn.cursor()

    cur.execute(DROP_TEST_RELATIONS_QUERY)
    cur.execute(UUID_FUNCTION_QUERY)
    cur.execute(CREATE_IMAGE_TABLE_QUERY)
    cur.execute(UNIQUE_CONDITION_QUERY)

    conn.commit()

    yield Postgres(cursor=cur, connection=conn)

    cur.execute(DROP_TEST_RELATIONS_QUERY)
    cur.close()
    conn.commit()
    conn.close()


def _set_up_image_view(pg, data_query, metrics_dict):
    conn_id = POSTGRES_CONN_ID
    _set_up_std_popularity_func(pg, data_query, metrics_dict)
    sql.create_media_view(
        conn_id,
        standardized_popularity_func=TEST_STANDARDIZED_POPULARITY,
        table_name=TEST_IMAGE_TABLE,
        db_view_name=TEST_IMAGE_VIEW,
        db_view_id_idx=TEST_IMAGE_VIEW_ID_IDX,
        db_view_provider_fid_idx=TEST_IMAGE_VIEW_PROVIDER_FID_IDX,
    )


def _set_up_std_popularity_func(pg, data_query, metrics_dict):
    conn_id = POSTGRES_CONN_ID
    _set_up_popularity_constants(pg, data_query, metrics_dict)
    sql.create_standardized_media_popularity_function(
        conn_id,
        function_name=TEST_STANDARDIZED_POPULARITY,
        popularity_constants=TEST_CONSTANTS,
    )


def _set_up_popularity_constants(pg, data_query, metrics_dict):
    conn_id = POSTGRES_CONN_ID
    _set_up_popularity_percentile_function()
    _set_up_popularity_metrics(metrics_dict)
    pg.cursor.execute(data_query)
    pg.connection.commit()
    sql.create_media_popularity_constants_view(
        conn_id,
        popularity_constants=TEST_CONSTANTS,
        popularity_constants_idx=TEST_POPULARITY_CONSTANTS_IDX,
        popularity_metrics=TEST_METRICS,
        popularity_percentile=TEST_POPULARITY_PERCENTILE,
    )


def _set_up_popularity_percentile_function():
    conn_id = POSTGRES_CONN_ID
    sql.create_media_popularity_percentile_function(
        conn_id,
        popularity_percentile=TEST_POPULARITY_PERCENTILE,
        media_table=TEST_IMAGE_TABLE,
    )


def _set_up_popularity_metrics(metrics_dict):
    conn_id = POSTGRES_CONN_ID
    sql.create_media_popularity_metrics(
        conn_id,
        popularity_metrics_table=TEST_METRICS,
    )
    sql.update_media_popularity_metrics(
        conn_id,
        popularity_metrics=metrics_dict,
        popularity_metrics_table=TEST_METRICS,
    )


def test_popularity_percentile_function_calculates(postgres_with_image_table):
    image_table = TEST_IMAGE_TABLE
    data_query = dedent(
        f"""
        INSERT INTO {image_table} (
          created_on, updated_on, provider, foreign_identifier, url,
          meta_data, license, removed_from_source
        )
        VALUES
          (
            NOW(), NOW(), 'my_provider', 'fid_a', 'https://test.com/a.jpg',
            '{{"views": 0, "description": "cats"}}', 'cc0', false
          ),
          (
            NOW(), NOW(), 'my_provider', 'fid_b', 'https://test.com/b.jpg',
            '{{"views": 50, "description": "cats"}}', 'cc0', false
          ),
          (
            NOW(), NOW(), 'my_provider', 'fid_c', 'https://test.com/c.jpg',
            '{{"views": 75, "description": "cats"}}', 'cc0', false
          ),
          (
            NOW(), NOW(), 'my_provider', 'fid_d', 'https://test.com/d.jpg',
            '{{"views": 150, "description": "cats"}}', 'cc0', false
          ),
          (
            NOW(), NOW(), 'diff_provider', 'fid_a', 'https://test.com/a.jpg',
            '{{"comments": 0, "description": "cats"}}', 'cc0', false
          ),
          (
            NOW(), NOW(), 'diff_provider', 'fid_b', 'https://test.com/b.jpg',
            '{{"comments": 50, "description": "cats"}}', 'cc0', false
          )
        ;
        """
    )
    postgres_with_image_table.cursor.execute(data_query)
    postgres_with_image_table.connection.commit()
    _set_up_popularity_percentile_function()
    mp_perc_1 = dedent(
        f"""
        SELECT {TEST_POPULARITY_PERCENTILE}('my_provider', 'views', 0.5);
        """
    )
    postgres_with_image_table.cursor.execute(mp_perc_1)
    expect_percentile_val = 50.0
    actual_percentile_val = postgres_with_image_table.cursor.fetchone()[0]
    assert actual_percentile_val == expect_percentile_val
    mp_perc_2 = dedent(
        f"""
        SELECT {TEST_POPULARITY_PERCENTILE}('diff_provider', 'comments', 0.3);
        """
    )
    postgres_with_image_table.cursor.execute(mp_perc_2)
    expect_percentile_val = 0.0
    actual_percentile_val = postgres_with_image_table.cursor.fetchone()[0]
    assert actual_percentile_val == expect_percentile_val


def test_popularity_percentile_function_nones_when_missing_type(
    postgres_with_image_table,
):
    image_table = TEST_IMAGE_TABLE
    data_query = dedent(
        f"""
        INSERT INTO {image_table} (
          created_on, updated_on, provider, foreign_identifier, url,
          meta_data, license, removed_from_source
        )
        VALUES
          (
            NOW(), NOW(), 'diff_provider', 'fid_a', 'https://test.com/a.jpg',
            '{{"comments": 0, "description": "cats"}}', 'cc0', false
          ),
          (
            NOW(), NOW(), 'diff_provider', 'fid_b', 'https://test.com/b.jpg',
            '{{"comments": 50, "description": "cats"}}', 'cc0', false
          )
        ;
        """
    )
    postgres_with_image_table.cursor.execute(data_query)
    postgres_with_image_table.connection.commit()
    _set_up_popularity_percentile_function()
    mp_perc_3 = dedent(
        f"""
        SELECT {TEST_POPULARITY_PERCENTILE}('diff_provider', 'views', 0.3);
        """
    )
    postgres_with_image_table.cursor.execute(mp_perc_3)
    actual_percentile_val = postgres_with_image_table.cursor.fetchone()[0]
    assert actual_percentile_val is None


def test_constants_view_adds_values_and_constants(postgres_with_image_table):
    image_table = TEST_IMAGE_TABLE
    data_query = dedent(
        f"""
        INSERT INTO {image_table} (
          created_on, updated_on, provider, foreign_identifier, url,
          meta_data, license, removed_from_source
        )
        VALUES
          (
            NOW(), NOW(), 'my_provider', 'fid_a', 'https://test.com/a.jpg',
            '{{"views": 0, "description": "cats"}}', 'cc0', false
          ),
          (
            NOW(), NOW(), 'my_provider', 'fid_b', 'https://test.com/b.jpg',
            '{{"views": 50, "description": "cats"}}', 'cc0', false
          ),
          (
            NOW(), NOW(), 'my_provider', 'fid_c', 'https://test.com/c.jpg',
            '{{"views": 75, "description": "cats"}}', 'cc0', false
          ),
          (
            NOW(), NOW(), 'my_provider', 'fid_d', 'https://test.com/d.jpg',
            '{{"views": 150, "description": "cats"}}', 'cc0', false
          ),
          (
            NOW(), NOW(), 'diff_provider', 'fid_a', 'https://test.com/a.jpg',
            '{{"comments": 10, "description": "cats"}}', 'cc0', false
          ),
          (
            NOW(), NOW(), 'diff_provider', 'fid_b', 'https://test.com/b.jpg',
            '{{"comments": 50, "description": "cats"}}', 'cc0', false
          )
        ;
        """
    )
    metrics = {
        "my_provider": {"metric": "views", "percentile": 0.5},
        "diff_provider": {"metric": "comments", "percentile": 0.8},
    }
    _set_up_popularity_constants(postgres_with_image_table, data_query, metrics)

    check_query = f"SELECT * FROM {TEST_CONSTANTS};"
    postgres_with_image_table.cursor.execute(check_query)
    expect_rows = [
        ("diff_provider", "comments", 0.8, 50.0, 50.0, 12.5),
        ("my_provider", "views", 0.5, 50.0, 50.0, 50.0),
    ]
    sorted_rows = sorted(list(postgres_with_image_table.cursor), key=lambda x: x[0])
    for (expect_row, sorted_row) in zip(expect_rows, sorted_rows):
        assert expect_row == pytest.approx(sorted_row)


def test_constants_view_handles_zeros_and_missing(postgres_with_image_table):
    image_table = TEST_IMAGE_TABLE
    data_query = dedent(
        f"""
        INSERT INTO {image_table} (
          created_on, updated_on, provider, foreign_identifier, url,
          meta_data, license, removed_from_source
        )
        VALUES
          (
            NOW(), NOW(), 'my_provider', 'fid_a', 'https://test.com/a.jpg',
            '{{"views": 0, "description": "cats"}}', 'cc0', false
          ),
          (
            NOW(), NOW(), 'my_provider', 'fid_b', 'https://test.com/b.jpg',
            '{{"views": 0, "description": "cats"}}', 'cc0', false
          ),
          (
            NOW(), NOW(), 'my_provider', 'fid_c', 'https://test.com/c.jpg',
            '{{"views": 0, "description": "cats"}}', 'cc0', false
          ),
          (
            NOW(), NOW(), 'my_provider', 'fid_d', 'https://test.com/d.jpg',
            '{{"views": 0, "description": "cats"}}', 'cc0', false
          ),
          (
            NOW(), NOW(), 'my_provider', 'fid_e', 'https://test.com/e.jpg',
            '{{"views": 10, "description": "cats"}}', 'cc0', false
          ),
          (
            NOW(), NOW(), 'diff_provider', 'fid_b', 'https://test.com/b.jpg',
            '{{"views": 50, "description": "cats"}}', 'cc0', false
          )
        ;
        """
    )
    metrics = {
        "my_provider": {"metric": "views", "percentile": 0.8},
        "diff_provider": {"metric": "comments", "percentile": 0.8},
    }
    _set_up_popularity_constants(postgres_with_image_table, data_query, metrics)

    check_query = f"SELECT * FROM {TEST_CONSTANTS};"
    postgres_with_image_table.cursor.execute(check_query)
    expect_rows = [
        ("diff_provider", "comments", 0.8, None, None, None),
        ("my_provider", "views", 0.8, 0.0, 1.0, 0.25),
    ]
    sorted_rows = sorted(list(postgres_with_image_table.cursor), key=lambda x: x[0])
    for (expect_row, sorted_row) in zip(expect_rows, sorted_rows):
        assert expect_row == pytest.approx(sorted_row)


def test_standardized_popularity_function_calculates(postgres_with_image_table):
    image_table = TEST_IMAGE_TABLE
    data_query = dedent(
        f"""
        INSERT INTO {image_table} (
          created_on, updated_on, provider, foreign_identifier, url,
          meta_data, license, removed_from_source
        )
        VALUES
          (
            NOW(), NOW(), 'my_provider', 'fid_a', 'https://test.com/a.jpg',
            '{{"views": 150, "description": "cats"}}', 'cc0', false
          ),
          (
            NOW(), NOW(), 'diff_provider', 'fid_b', 'https://test.com/b.jpg',
            '{{"comments": 50, "description": "cats"}}', 'cc0', false
          ),
          (
            NOW(), NOW(), 'other_provider', 'fid_c', 'https://test.com/c.jpg',
            '{{"likes": 0, "description": "cats"}}', 'cc0', false
          )
        ;
        """
    )
    metrics = {
        "my_provider": {"metric": "views", "percentile": 0.8},
        "diff_provider": {"metric": "comments", "percentile": 0.5},
        "other_provider": {"metric": "likes", "percentile": 0.5},
    }
    _set_up_std_popularity_func(postgres_with_image_table, data_query, metrics)
    check_query = f"SELECT * FROM {TEST_CONSTANTS};"
    postgres_with_image_table.cursor.execute(check_query)
    print(list(postgres_with_image_table.cursor))
    arg_list = [
        ("my_provider", '{"views": 150, "description": "cats"}', 0.8),
        ("my_provider", '{"views": 0, "description": "cats"}', 0.0),
        ("my_provider", '{"comments": 100, "description": "cats"}', None),
        ("diff_provider", '{"comments": 50, "description": "cats"}', 0.5),
        ("diff_provider", '{"comments": 0, "description": "cats"}', 0.0),
        ("diff_provider", '{"comments": 150, "description": "cats"}', 0.75),
        ("diff_provider", '{"comments": 450, "description": "cats"}', 0.9),
        ("diff_provider", '{"views": 150, "description": "cats"}', None),
        ("other_provider", '{"likes": 3, "description": "cats"}', 0.75),
        ("other_provider", '{"likes": 1, "description": "cats"}', 0.5),
    ]
    for i in range(len(arg_list)):
        print(arg_list[i])
        std_pop_query = dedent(
            f"""
            SELECT {TEST_STANDARDIZED_POPULARITY}(
              '{arg_list[i][0]}',
              '{arg_list[i][1]}'::jsonb
            );
            """
        )
        postgres_with_image_table.cursor.execute(std_pop_query)
        actual_std_pop_val = postgres_with_image_table.cursor.fetchone()[0]
        expect_std_pop_val = arg_list[i][2]
        assert actual_std_pop_val == expect_std_pop_val


def test_image_view_calculates_std_pop(postgres_with_image_table):
    image_table = TEST_IMAGE_TABLE
    image_view = TEST_IMAGE_VIEW
    data_query = dedent(
        f"""
        INSERT INTO {image_table} (
          created_on, updated_on, provider, foreign_identifier, url,
          meta_data, license, removed_from_source
        )
        VALUES
          (
            NOW(), NOW(), 'my_provider', 'fid_a', 'https://test.com/a.jpg',
            '{{"views": 0, "description": "cats"}}', 'cc0', false
          ),
          (
            NOW(), NOW(), 'my_provider', 'fid_b', 'https://test.com/b.jpg',
            '{{"views": 50, "description": "cats"}}', 'cc0', false
          ),
          (
            NOW(), NOW(), 'my_provider', 'fid_c', 'https://test.com/c.jpg',
            '{{"views": 75, "description": "cats"}}', 'cc0', false
          ),
          (
            NOW(), NOW(), 'my_provider', 'fid_d', 'https://test.com/d.jpg',
            '{{"views": 150, "description": "cats"}}', 'cc0', false
          )
        """
    )
    metrics = {"my_provider": {"metric": "views", "percentile": 0.5}}
    _set_up_image_view(postgres_with_image_table, data_query, metrics)
    check_query = dedent(
        f"""
        SELECT foreign_identifier, standardized_popularity
        FROM {image_view};
        """
    )
    postgres_with_image_table.cursor.execute(check_query)
    rd = dict(postgres_with_image_table.cursor)
    assert all(
        [
            rd["fid_a"] == 0.0,
            rd["fid_b"] == 0.5,
            rd["fid_c"] == 0.6,
            rd["fid_d"] == 0.75,
        ]
    )

import os
from collections import namedtuple
from datetime import datetime, timedelta
from textwrap import dedent

import psycopg2
import pytest
from popularity import sql
from popularity.popularity_refresh_types import PopularityRefresh

from common.constants import SQLInfo
from common.loader.sql import create_column_definitions
from common.storage.db_columns import IMAGE_TABLE_COLUMNS
from tests.dags.common.conftest import POSTGRES_TEST_CONN_ID as POSTGRES_CONN_ID


POSTGRES_TEST_URI = os.getenv("AIRFLOW_CONN_POSTGRES_OPENLEDGER_TESTING")


@pytest.fixture
def sql_info(
    image_table,
    identifier,
) -> SQLInfo:
    return SQLInfo(
        media_table=image_table,
        metrics_table=f"image_popularity_metrics_{identifier}",
        standardized_popularity_fn=f"standardized_image_popularity_{identifier}",
        popularity_percentile_fn=f"image_popularity_percentile_{identifier}",
    )


@pytest.fixture
def postgres_with_image_table(sql_info):
    Postgres = namedtuple("Postgres", ["cursor", "connection"])
    conn = psycopg2.connect(POSTGRES_TEST_URI)
    cur = conn.cursor()

    drop_test_relations_query = f"""
    DROP TABLE IF EXISTS {sql_info.metrics_table} CASCADE;
    DROP TABLE IF EXISTS {sql_info.media_table} CASCADE;
    DROP FUNCTION IF EXISTS {sql_info.standardized_popularity_fn} CASCADE;
    DROP FUNCTION IF EXISTS {sql_info.popularity_percentile_fn} CASCADE;
    """

    cur.execute(drop_test_relations_query)
    cur.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;')

    image_columns = create_column_definitions(IMAGE_TABLE_COLUMNS)
    cur.execute(f"CREATE TABLE public.{sql_info.media_table} ({image_columns});")

    cur.execute(
        f"""
CREATE UNIQUE INDEX {sql_info.media_table}_provider_fid_idx
ON public.{sql_info.media_table}
USING btree (provider, md5(foreign_identifier));
"""
    )

    conn.commit()

    yield Postgres(cursor=cur, connection=conn)

    cur.execute(drop_test_relations_query)
    cur.close()
    conn.commit()
    conn.close()


def _set_up_popularity_metrics(metrics_dict, sql_info, mock_pg_hook_task):
    conn_id = POSTGRES_CONN_ID
    # Create metrics table
    sql.create_media_popularity_metrics.function(
        postgres_conn_id=conn_id, media_type="image", sql_info=sql_info
    )
    # Insert values from metrics_dict into metrics table
    if metrics_dict:
        sql.update_media_popularity_metrics.function(
            postgres_conn_id=conn_id,
            media_type="image",
            popularity_metrics=metrics_dict,
            sql_info=sql_info,
            task=mock_pg_hook_task,
        )

    # For each provider in metrics_dict, calculate the percentile and then
    # update the percentile and popularity constant
    for provider in metrics_dict.keys():
        percentile_val = sql.calculate_media_popularity_percentile_value.function(
            postgres_conn_id=conn_id,
            provider=provider,
            media_type="image",
            task=mock_pg_hook_task,
            sql_info=sql_info,
        )
        sql.update_percentile_and_constants_values_for_provider.function(
            postgres_conn_id=conn_id,
            provider=provider,
            raw_percentile_value=percentile_val,
            media_type="image",
            popularity_metrics=metrics_dict,
            sql_info=sql_info,
        )


def _set_up_popularity_percentile_function(sql_info):
    conn_id = POSTGRES_CONN_ID
    sql.create_media_popularity_percentile_function.function(
        conn_id, media_type="image", sql_info=sql_info
    )


def _set_up_popularity_metrics_and_constants(
    pg,
    data_query,
    metrics_dict,
    sql_info,
    mock_pg_hook_task,
):
    # Execute the data query first (typically, loads sample data into the media table)
    if data_query:
        pg.cursor.execute(data_query)
        pg.connection.commit()

    # Then set up functions, metrics, and constants
    _set_up_popularity_percentile_function(sql_info)
    _set_up_popularity_metrics(metrics_dict, sql_info, mock_pg_hook_task)


def _set_up_std_popularity_func(
    pg,
    data_query,
    metrics_dict,
    sql_info,
    mock_pg_hook_task,
):
    conn_id = POSTGRES_CONN_ID
    _set_up_popularity_metrics_and_constants(
        pg,
        data_query,
        metrics_dict,
        sql_info,
        mock_pg_hook_task,
    )
    sql.create_standardized_media_popularity_function.function(
        conn_id, media_type="image", sql_info=sql_info
    )


def test_popularity_percentile_function_calculates(postgres_with_image_table, sql_info):
    data_query = dedent(
        f"""
        INSERT INTO {sql_info.media_table} (
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
    _set_up_popularity_percentile_function(sql_info)
    mp_perc_1 = dedent(
        f"""
        SELECT {sql_info.popularity_percentile_fn}('my_provider', 'views', 0.5);
        """
    )
    postgres_with_image_table.cursor.execute(mp_perc_1)
    expect_percentile_val = 50.0
    actual_percentile_val = postgres_with_image_table.cursor.fetchone()[0]
    assert actual_percentile_val == expect_percentile_val
    mp_perc_2 = dedent(
        f"""
        SELECT {sql_info.popularity_percentile_fn}('diff_provider', 'comments', 0.3);
        """
    )
    postgres_with_image_table.cursor.execute(mp_perc_2)
    expect_percentile_val = 0.0
    actual_percentile_val = postgres_with_image_table.cursor.fetchone()[0]
    assert actual_percentile_val == expect_percentile_val


def test_popularity_percentile_function_nones_when_missing_type(
    postgres_with_image_table, sql_info
):
    data_query = dedent(
        f"""
        INSERT INTO {sql_info.media_table} (
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
    _set_up_popularity_percentile_function(sql_info)
    mp_perc_3 = dedent(
        f"""
        SELECT {sql_info.popularity_percentile_fn}('diff_provider', 'views', 0.3);
        """
    )
    postgres_with_image_table.cursor.execute(mp_perc_3)
    actual_percentile_val = postgres_with_image_table.cursor.fetchone()[0]
    assert actual_percentile_val is None


def test_metrics_table_adds_values_and_constants(
    postgres_with_image_table, sql_info, mock_pg_hook_task
):
    data_query = dedent(
        f"""
        INSERT INTO {sql_info.media_table} (
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
    _set_up_popularity_metrics_and_constants(
        postgres_with_image_table, data_query, metrics, sql_info, mock_pg_hook_task
    )

    check_query = f"SELECT * FROM {sql_info.metrics_table};"
    postgres_with_image_table.cursor.execute(check_query)
    expect_rows = [
        ("diff_provider", "comments", 0.8, 50.0, 12.5),
        ("my_provider", "views", 0.5, 50.0, 50.0),
    ]
    sorted_rows = sorted(list(postgres_with_image_table.cursor), key=lambda x: x[0])
    for expect_row, sorted_row in zip(expect_rows, sorted_rows):
        assert expect_row == pytest.approx(sorted_row)


def test_metrics_table_handles_zeros_and_missing_in_constants(
    postgres_with_image_table, sql_info, mock_pg_hook_task
):
    data_query = dedent(
        f"""
        INSERT INTO {sql_info.media_table} (
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
        # Provider that has some records with popularity data
        "my_provider": {"metric": "views", "percentile": 0.8},
        # Provider that has a metric configured, but no records with data for that metric
        "diff_provider": {"metric": "comments", "percentile": 0.8},
    }
    _set_up_popularity_metrics_and_constants(
        postgres_with_image_table, data_query, metrics, sql_info, mock_pg_hook_task
    )

    check_query = f"SELECT * FROM {sql_info.metrics_table};"
    postgres_with_image_table.cursor.execute(check_query)
    expect_rows = [
        ("diff_provider", "comments", 0.8, None, None),
        ("my_provider", "views", 0.8, 1.0, 0.25),
    ]
    sorted_rows = sorted(list(postgres_with_image_table.cursor), key=lambda x: x[0])
    for expect_row, sorted_row in zip(expect_rows, sorted_rows):
        assert expect_row == pytest.approx(sorted_row)


def test_standardized_popularity_function_calculates(
    postgres_with_image_table, sql_info, mock_pg_hook_task
):
    data_query = dedent(
        f"""
        INSERT INTO {sql_info.media_table} (
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
    _set_up_std_popularity_func(
        postgres_with_image_table, data_query, metrics, sql_info, mock_pg_hook_task
    )
    check_query = f"SELECT * FROM {sql_info.metrics_table};"
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
            SELECT {sql_info.standardized_popularity_fn}(
              '{arg_list[i][0]}',
              '{arg_list[i][1]}'::jsonb
            );
            """
        )
        postgres_with_image_table.cursor.execute(std_pop_query)
        actual_std_pop_val = postgres_with_image_table.cursor.fetchone()[0]
        expect_std_pop_val = arg_list[i][2]
        assert actual_std_pop_val == expect_std_pop_val


@pytest.mark.parametrize(
    "providers, media_type, expected_confs",
    [
        # No providers for this media type
        ([], "image", []),
        (
            ["foo_provider"],
            "image",
            [
                {
                    "query_id": "foo_provider_popularity_refresh_20230101",
                    "table_name": "image",
                    "select_query": "WHERE provider='foo_provider' AND updated_on < '2023-01-01 00:00:00'",
                    "update_query": "SET updated_on = NOW(), standardized_popularity = standardized_image_popularity(image.provider, image.meta_data)",
                    "batch_size": 10000,
                    "update_timeout": 3600.0,
                    "dry_run": False,
                    "resume_update": False,
                },
            ],
        ),
        (
            ["my_provider", "your_provider"],
            "audio",
            [
                {
                    "query_id": "my_provider_popularity_refresh_20230101",
                    "table_name": "audio",
                    "select_query": "WHERE provider='my_provider' AND updated_on < '2023-01-01 00:00:00'",
                    "update_query": "SET updated_on = NOW(), standardized_popularity = standardized_audio_popularity(audio.provider, audio.meta_data)",
                    "batch_size": 10000,
                    "update_timeout": 3600.0,
                    "dry_run": False,
                    "resume_update": False,
                },
                {
                    "query_id": "your_provider_popularity_refresh_20230101",
                    "table_name": "audio",
                    "select_query": "WHERE provider='your_provider' AND updated_on < '2023-01-01 00:00:00'",
                    "update_query": "SET updated_on = NOW(), standardized_popularity = standardized_audio_popularity(audio.provider, audio.meta_data)",
                    "batch_size": 10000,
                    "update_timeout": 3600.0,
                    "dry_run": False,
                    "resume_update": False,
                },
            ],
        ),
    ],
)
def test_get_providers_update_confs(providers, media_type, expected_confs):
    TEST_DAY = datetime(2023, 1, 1)
    config = PopularityRefresh(
        media_type=media_type,
        refresh_popularity_batch_timeout=timedelta(hours=1),
        popularity_metrics={provider: {"metric": "views"} for provider in providers},
    )

    actual_confs = sql.get_providers_update_confs.function(
        POSTGRES_CONN_ID,
        config,
        TEST_DAY,
    )

    assert actual_confs == expected_confs

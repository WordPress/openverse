import os
import re
from collections import namedtuple
from pathlib import Path
from textwrap import dedent
from typing import NamedTuple

import psycopg2
import pytest

from catalog.tests.dags.common.conftest import POSTGRES_TEST_CONN_ID as POSTGRES_CONN_ID
from common.loader.sql import create_column_definitions
from common.popularity import sql
from common.storage.db_columns import IMAGE_TABLE_COLUMNS


DDL_DEFINITIONS_PATH = Path(__file__).parents[5] / "docker" / "upstream_db"
POSTGRES_TEST_URI = os.getenv("AIRFLOW_CONN_POSTGRES_OPENLEDGER_TESTING")


class TableInfo(NamedTuple):
    image: str
    image_view: str
    metrics: str
    standardized_popularity: str
    popularity_percentile: str
    image_view_idx: str
    provider_fid_idx: str


@pytest.fixture
def table_info(
    image_table,
    identifier,
) -> TableInfo:
    return TableInfo(
        image=image_table,
        image_view=f"image_view_{identifier}",
        metrics=f"image_popularity_metrics_{identifier}",
        standardized_popularity=f"standardized_popularity_{identifier}",
        popularity_percentile=f"popularity_percentile_{identifier}",
        image_view_idx=f"test_view_id_{identifier}_idx",
        provider_fid_idx=f"test_view_provider_fid_{identifier}_idx",
    )


@pytest.fixture
def postgres_with_image_table(table_info):
    Postgres = namedtuple("Postgres", ["cursor", "connection"])
    conn = psycopg2.connect(POSTGRES_TEST_URI)
    cur = conn.cursor()

    drop_test_relations_query = f"""
    DROP MATERIALIZED VIEW IF EXISTS {table_info.image_view} CASCADE;
    DROP TABLE IF EXISTS {table_info.metrics} CASCADE;
    DROP TABLE IF EXISTS {table_info.image} CASCADE;
    DROP FUNCTION IF EXISTS {table_info.standardized_popularity} CASCADE;
    DROP FUNCTION IF EXISTS {table_info.popularity_percentile} CASCADE;
    """

    cur.execute(drop_test_relations_query)
    cur.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;')

    image_columns = create_column_definitions(IMAGE_TABLE_COLUMNS)
    cur.execute(f"CREATE TABLE public.{table_info.image} ({image_columns});")

    cur.execute(
        f"""
CREATE UNIQUE INDEX {table_info.image}_provider_fid_idx
ON public.{table_info.image}
USING btree (provider, md5(foreign_identifier));
"""
    )

    conn.commit()

    yield Postgres(cursor=cur, connection=conn)

    cur.execute(drop_test_relations_query)
    cur.close()
    conn.commit()
    conn.close()


def _set_up_popularity_metrics(metrics_dict, table_info, mock_pg_hook_task):
    conn_id = POSTGRES_CONN_ID
    # Create metrics table
    sql.create_media_popularity_metrics(
        postgres_conn_id=conn_id,
        popularity_metrics_table=table_info.metrics,
    )
    # Insert values from metrics_dict into metrics table
    sql.update_media_popularity_metrics.function(
        postgres_conn_id=conn_id,
        popularity_metrics=metrics_dict,
        popularity_metrics_table=table_info.metrics,
        task=mock_pg_hook_task,
    )

    # For each provider in metrics_dict, calculate the percentile and then
    # update the percentile and popularity constant
    for provider in metrics_dict.keys():
        percentile_val = sql.calculate_media_popularity_percentile_value.function(
            postgres_conn_id=conn_id,
            provider=provider,
            task=mock_pg_hook_task,
            popularity_metrics_table=table_info.metrics,
            popularity_percentile=table_info.popularity_percentile,
        )
        sql.update_percentile_and_constants_values_for_provider.function(
            postgres_conn_id=conn_id,
            provider=provider,
            raw_percentile_value=percentile_val,
            popularity_metrics_table=table_info.metrics,
            popularity_metrics=metrics_dict,
        )


def _set_up_popularity_percentile_function(table_info):
    conn_id = POSTGRES_CONN_ID
    sql.create_media_popularity_percentile_function(
        conn_id,
        popularity_percentile=table_info.popularity_percentile,
        media_table=table_info.image,
    )


def _set_up_popularity_constants(
    pg,
    data_query,
    metrics_dict,
    table_info,
    mock_pg_hook_task,
):
    # Execute the data query first (typically, loads sample data into the media table)
    pg.cursor.execute(data_query)
    pg.connection.commit()

    # Then set up functions, metrics, and constants
    _set_up_popularity_percentile_function(table_info)
    _set_up_popularity_metrics(metrics_dict, table_info, mock_pg_hook_task)


def _set_up_std_popularity_func(
    pg,
    data_query,
    metrics_dict,
    table_info,
    mock_pg_hook_task,
):
    conn_id = POSTGRES_CONN_ID
    _set_up_popularity_constants(
        pg,
        data_query,
        metrics_dict,
        table_info,
        mock_pg_hook_task,
    )
    sql.create_standardized_media_popularity_function(
        conn_id,
        mock_pg_hook_task,
        function_name=table_info.standardized_popularity,
        popularity_metrics=table_info.metrics,
    )


def _set_up_image_view(
    pg,
    data_query,
    metrics_dict,
    table_info,
    mock_pg_hook_task,
):
    conn_id = POSTGRES_CONN_ID
    _set_up_std_popularity_func(
        pg, data_query, metrics_dict, table_info, mock_pg_hook_task
    )
    sql.create_media_view(
        conn_id,
        standardized_popularity_func=table_info.standardized_popularity,
        table_name=table_info.image,
        db_view_name=table_info.image_view,
        db_view_id_idx=table_info.image_view_idx,
        db_view_provider_fid_idx=table_info.provider_fid_idx,
        task=mock_pg_hook_task,
    )


def test_popularity_percentile_function_calculates(
    postgres_with_image_table, table_info
):
    data_query = dedent(
        f"""
        INSERT INTO {table_info.image} (
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
    _set_up_popularity_percentile_function(table_info)
    mp_perc_1 = dedent(
        f"""
        SELECT {table_info.popularity_percentile}('my_provider', 'views', 0.5);
        """
    )
    postgres_with_image_table.cursor.execute(mp_perc_1)
    expect_percentile_val = 50.0
    actual_percentile_val = postgres_with_image_table.cursor.fetchone()[0]
    assert actual_percentile_val == expect_percentile_val
    mp_perc_2 = dedent(
        f"""
        SELECT {table_info.popularity_percentile}('diff_provider', 'comments', 0.3);
        """
    )
    postgres_with_image_table.cursor.execute(mp_perc_2)
    expect_percentile_val = 0.0
    actual_percentile_val = postgres_with_image_table.cursor.fetchone()[0]
    assert actual_percentile_val == expect_percentile_val


def test_popularity_percentile_function_nones_when_missing_type(
    postgres_with_image_table, table_info
):
    data_query = dedent(
        f"""
        INSERT INTO {table_info.image} (
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
    _set_up_popularity_percentile_function(table_info)
    mp_perc_3 = dedent(
        f"""
        SELECT {table_info.popularity_percentile}('diff_provider', 'views', 0.3);
        """
    )
    postgres_with_image_table.cursor.execute(mp_perc_3)
    actual_percentile_val = postgres_with_image_table.cursor.fetchone()[0]
    assert actual_percentile_val is None


def test_metrics_table_adds_values_and_constants(
    postgres_with_image_table, table_info, mock_pg_hook_task
):
    data_query = dedent(
        f"""
        INSERT INTO {table_info.image} (
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
    _set_up_popularity_constants(
        postgres_with_image_table, data_query, metrics, table_info, mock_pg_hook_task
    )

    check_query = f"SELECT * FROM {table_info.metrics};"
    postgres_with_image_table.cursor.execute(check_query)
    expect_rows = [
        ("diff_provider", "comments", 0.8, 50.0, 12.5),
        ("my_provider", "views", 0.5, 50.0, 50.0),
    ]
    sorted_rows = sorted(list(postgres_with_image_table.cursor), key=lambda x: x[0])
    for expect_row, sorted_row in zip(expect_rows, sorted_rows):
        assert expect_row == pytest.approx(sorted_row)


def test_metrics_table_handles_zeros_and_missing_in_constants(
    postgres_with_image_table, table_info, mock_pg_hook_task
):
    data_query = dedent(
        f"""
        INSERT INTO {table_info.image} (
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
    _set_up_popularity_constants(
        postgres_with_image_table, data_query, metrics, table_info, mock_pg_hook_task
    )

    check_query = f"SELECT * FROM {table_info.metrics};"
    postgres_with_image_table.cursor.execute(check_query)
    expect_rows = [
        ("diff_provider", "comments", 0.8, None, None),
        ("my_provider", "views", 0.8, 1.0, 0.25),
    ]
    sorted_rows = sorted(list(postgres_with_image_table.cursor), key=lambda x: x[0])
    for expect_row, sorted_row in zip(expect_rows, sorted_rows):
        assert expect_row == pytest.approx(sorted_row)


def test_get_providers_with_popularity_data_for_media_type(
    postgres_with_image_table, table_info, mock_pg_hook_task
):
    data_query = dedent(
        f"""
        INSERT INTO {table_info.image} (
          created_on, updated_on, provider, foreign_identifier, url,
          meta_data, license, removed_from_source
        )
        VALUES
          (
            NOW(), NOW(), 'my_provider', 'fid_a', 'https://test.com/a.jpg',
            '{{"views": 0, "description": "cats"}}', 'cc0', false
          ),
          (
            NOW(), NOW(), 'diff_provider', 'fid_b', 'https://test.com/b.jpg',
            '{{"views": 50, "description": "cats"}}', 'cc0', false
          ),
          (
            NOW(), NOW(), 'provider_without_popularity', 'fid_b', 'https://test.com/b.jpg',
            '{{"views": 50, "description": "cats"}}', 'cc0', false
          )
        ;
        """
    )
    metrics = {
        "my_provider": {"metric": "views", "percentile": 0.8},
        "diff_provider": {"metric": "comments", "percentile": 0.8},
    }
    _set_up_popularity_constants(
        postgres_with_image_table, data_query, metrics, table_info, mock_pg_hook_task
    )

    expected_providers = ["diff_provider", "my_provider"]
    actual_providers = sql.get_providers_with_popularity_data_for_media_type(
        POSTGRES_CONN_ID, media_type="image", popularity_metrics=table_info.metrics
    )

    assert actual_providers == expected_providers


def test_standardized_popularity_function_calculates(
    postgres_with_image_table, table_info, mock_pg_hook_task
):
    data_query = dedent(
        f"""
        INSERT INTO {table_info.image} (
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
        postgres_with_image_table, data_query, metrics, table_info, mock_pg_hook_task
    )
    check_query = f"SELECT * FROM {table_info.metrics};"
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
            SELECT {table_info.standardized_popularity}(
              '{arg_list[i][0]}',
              '{arg_list[i][1]}'::jsonb
            );
            """
        )
        postgres_with_image_table.cursor.execute(std_pop_query)
        actual_std_pop_val = postgres_with_image_table.cursor.fetchone()[0]
        expect_std_pop_val = arg_list[i][2]
        assert actual_std_pop_val == expect_std_pop_val


def test_image_view_calculates_std_pop(
    postgres_with_image_table, table_info, mock_pg_hook_task
):
    data_query = dedent(
        f"""
        INSERT INTO {table_info.image} (
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
    _set_up_image_view(
        postgres_with_image_table, data_query, metrics, table_info, mock_pg_hook_task
    )
    check_query = dedent(
        f"""
        SELECT foreign_identifier, standardized_popularity
        FROM {table_info.image_view};
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


@pytest.mark.parametrize(
    "ddl_filename, metrics",
    [
        ("0004_openledger_image_view.sql", sql.IMAGE_POPULARITY_METRICS),
        ("0007_openledger_audio_view.sql", sql.AUDIO_POPULARITY_METRICS),
    ],
)
def test_ddl_matches_definitions(ddl_filename, metrics):
    ddl = (DDL_DEFINITIONS_PATH / ddl_filename).read_text()
    if not (
        match := re.search(
            r"INSERT INTO public.\w+_popularity_metrics.*?;",
            ddl,
            re.MULTILINE | re.DOTALL,
        )
    ):
        raise ValueError(f"Could not find insert statement in ddl file {ddl_filename}")

    for provider in metrics:
        assert provider in match.group(0)

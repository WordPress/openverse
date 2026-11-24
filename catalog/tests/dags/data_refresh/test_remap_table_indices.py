from unittest.mock import call, patch

import pytest

from data_refresh.promote_table import get_go_live_query
from data_refresh.remap_table_indices import (
    TableIndex,
    create_table_indices,
    transform_index_defs,
)
from tests.conftest import xcom_round_trip


@pytest.mark.parametrize(
    "existing_index_defs, expected_index_defs",
    [
        # Empty
        ([], []),
        # Transform all indices, including pk
        (
            [
                "CREATE INDEX image_provider_7d11f847 ON public.image USING btree (provider)",
                # Unique index
                "CREATE UNIQUE INDEX image_identifier_key ON public.image USING btree (identifier)",
                # Pk is ignored
                "CREATE UNIQUE INDEX image_pkey ON public.image USING btree (id)",
            ],
            [
                TableIndex(
                    index_name="image_provider_7d11f847",
                    temp_index_name="temp_import_image_provider_7d11f847",
                    index_def="CREATE INDEX temp_import_image_provider_7d11f847 ON"
                    " public.temp_import_image USING btree (provider)",
                ),
                TableIndex(
                    index_name="image_identifier_key",
                    temp_index_name="temp_import_image_identifier_key",
                    index_def="CREATE UNIQUE INDEX temp_import_image_identifier_key ON"
                    " public.temp_import_image USING btree (identifier)",
                ),
                TableIndex(
                    index_name="image_pkey",
                    temp_index_name="temp_import_image_pkey",
                    index_def="CREATE UNIQUE INDEX temp_import_image_pkey ON"
                    " public.temp_import_image USING btree (id)",
                ),
            ],
        ),
    ],
)
def test_transform_index_defs(existing_index_defs, expected_index_defs):
    actual = transform_index_defs.function(
        existing_index_defs=existing_index_defs,
        temp_table_name="temp_import_image",
        table_name="image",
    )

    assert actual == expected_index_defs


@pytest.mark.parametrize(
    "index_configs, expected_sql",
    [
        # Empty
        ([], []),
        # run_sql never called if there is only a pk index
        (
            [
                TableIndex(
                    index_name="image_pkey",
                    temp_index_name="temp_import_image_pkey",
                    index_def="CREATE UNIQUE INDEX temp_import_image_pk ON"
                    " public.temp_import_image USING btree (id)",
                ),
            ],
            [],
        ),
        # Single index that should be remapped
        (
            [
                TableIndex(
                    index_name="image_provider_7d11f847",
                    temp_index_name="temp_import_image_provider_7d11f847",
                    index_def="CREATE INDEX temp_import_image_provider_7d11f847 ON"
                    " public.temp_import_image USING btree (provider)",
                ),
            ],
            [
                "CREATE INDEX IF NOT EXISTS temp_import_image_provider_7d11f847"
                " ON public.temp_import_image USING btree (provider)",
            ],
        ),
        # If there are multiple indices, run_sql is called for all except the pk
        (
            [
                TableIndex(
                    index_name="image_provider_7d11f847",
                    temp_index_name="temp_import_image_provider_7d11f847",
                    index_def="CREATE INDEX temp_import_image_provider_7d11f847 ON"
                    " public.temp_import_image USING btree (provider)",
                ),
                TableIndex(
                    index_name="image_identifier_key",
                    temp_index_name="temp_import_image_identifier_key",
                    index_def="CREATE UNIQUE INDEX temp_import_image_identifier_key ON"
                    " public.temp_import_image USING btree (identifier)",
                ),
                TableIndex(
                    index_name="image_pkey",
                    temp_index_name="temp_import_image_pkey",
                    index_def="CREATE UNIQUE INDEX temp_import_image_pk ON"
                    " public.temp_import_image USING btree (id)",
                ),
            ],
            [
                "CREATE INDEX IF NOT EXISTS temp_import_image_provider_7d11f847"
                " ON public.temp_import_image USING btree (provider)",
                "CREATE UNIQUE INDEX IF NOT EXISTS temp_import_image_identifier_key"
                " ON public.temp_import_image USING btree (identifier)",
            ],
        ),
    ],
)
def test_create_table_indices(index_configs, expected_sql):
    with patch("common.sql.run_sql.function") as run_sql_mock:
        create_table_indices.function(
            postgres_conn_id="test_id",
            index_configs=index_configs,
            table_name="image",
            statement_timeout=7200.0,
        )

        expected_calls = [
            call(postgres_conn_id="test_id", sql_template=sql, timeout=7200.0)
            for sql in expected_sql
        ]

        assert run_sql_mock.call_args_list == expected_calls


def test_index_configs_survive_xcom():
    index_configs = xcom_round_trip(
        transform_index_defs.function(
            existing_index_defs=[
                "CREATE INDEX image_provider_7d11f847 ON public.image USING btree (provider)",
                "CREATE UNIQUE INDEX image_pkey ON public.image USING btree (id)",
            ],
            temp_table_name="temp_import_image",
            table_name="image",
        )
    )

    with patch("common.sql.run_sql.function") as run_sql_mock:
        returned = create_table_indices.function(
            postgres_conn_id="test_id", index_configs=index_configs, table_name="image"
        )
    run_sql_mock.assert_called_once_with(
        postgres_conn_id="test_id",
        sql_template="CREATE INDEX IF NOT EXISTS temp_import_image_provider_7d11f847"
        " ON public.temp_import_image USING btree (provider)",
        timeout=None,
    )

    go_live_query = get_go_live_query.function(
        table_name="image",
        temp_table_name="temp_import_image",
        index_mapping=xcom_round_trip(returned),
    )
    assert (
        "ALTER INDEX temp_import_image_provider_7d11f847"
        " RENAME TO image_provider_7d11f847;" in go_live_query
    )
    assert "ALTER INDEX temp_import_image_pkey RENAME TO image_pkey;" in go_live_query

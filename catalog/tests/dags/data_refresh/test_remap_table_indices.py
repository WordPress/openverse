from unittest.mock import call, patch

import pytest

from data_refresh.remap_table_indices import (
    TableIndex,
    create_table_indices,
    transform_index_defs,
)


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
                    "image_provider_7d11f847",
                    "temp_import_image_provider_7d11f847",
                    "CREATE INDEX temp_import_image_provider_7d11f847 ON"
                    " public.temp_import_image USING btree (provider)",
                ),
                TableIndex(
                    "image_identifier_key",
                    "temp_import_image_identifier_key",
                    "CREATE UNIQUE INDEX temp_import_image_identifier_key ON"
                    " public.temp_import_image USING btree (identifier)",
                ),
                TableIndex(
                    "image_pkey",
                    "temp_import_image_pkey",
                    "CREATE UNIQUE INDEX temp_import_image_pkey ON"
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
                    "image_pkey",
                    "temp_import_image_pkey",
                    "CREATE UNIQUE INDEX temp_import_image_pk ON"
                    " public.temp_import_image USING btree (id)",
                ),
            ],
            [],
        ),
        # Single index that should be remapped
        (
            [
                TableIndex(
                    "image_provider_7d11f847",
                    "temp_import_image_provider_7d11f847",
                    "CREATE INDEX temp_import_image_provider_7d11f847 ON"
                    " public.temp_import_image USING btree (provider)",
                ),
            ],
            [
                "CREATE INDEX temp_import_image_provider_7d11f847 ON"
                " public.temp_import_image USING btree (provider)",
            ],
        ),
        # If there are multiple indices, run_sql is called for all except the pk
        (
            [
                TableIndex(
                    "image_provider_7d11f847",
                    "temp_import_image_provider_7d11f847",
                    "CREATE INDEX temp_import_image_provider_7d11f847 ON"
                    " public.temp_import_image USING btree (provider)",
                ),
                TableIndex(
                    "image_identifier_key",
                    "temp_import_image_identifier_key",
                    "CREATE UNIQUE INDEX temp_import_image_identifier_key ON"
                    " public.temp_import_image USING btree (identifier)",
                ),
                TableIndex(
                    "image_pkey",
                    "temp_import_image_pkey",
                    "CREATE UNIQUE INDEX temp_import_image_pk ON"
                    " public.temp_import_image USING btree (id)",
                ),
            ],
            [
                "CREATE INDEX temp_import_image_provider_7d11f847 ON"
                " public.temp_import_image USING btree (provider)",
                "CREATE UNIQUE INDEX temp_import_image_identifier_key ON"
                " public.temp_import_image USING btree (identifier)",
            ],
        ),
    ],
)
def test_create_table_indices(index_configs, expected_sql):
    with patch("common.sql.run_sql.function") as run_sql_mock:
        create_table_indices.function(
            postgres_conn_id="test_id", index_configs=index_configs, table_name="image"
        )

        expected_calls = [
            call(postgres_conn_id="test_id", sql_template=sql) for sql in expected_sql
        ]

        run_sql_mock.assert_has_calls(expected_calls)

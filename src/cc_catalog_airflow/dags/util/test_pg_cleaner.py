import os
from unittest.mock import patch, call

from airflow.hooks.postgres_hook import PostgresHook
import pytest

from util.loader import test_sql
from util import pg_cleaner

RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "test_resources"
)

TEST_IMAGE_TABLE = test_sql.TEST_IMAGE_TABLE
DROP_IMAGE_TABLE_QUERY = test_sql.DROP_IMAGE_TABLE_QUERY
DROP_IMAGE_INDEX_QUERY = test_sql.DROP_IMAGE_INDEX_QUERY
UUID_FUNCTION_QUERY = test_sql.UUID_FUNCTION_QUERY
CREATE_IMAGE_TABLE_QUERY = test_sql.CREATE_IMAGE_TABLE_QUERY
UNIQUE_CONDITION_QUERY = test_sql.UNIQUE_CONDITION_QUERY


POSTGRES_CONN_ID = os.getenv("TEST_CONN_ID")
POSTGRES_TEST_URI = os.getenv("AIRFLOW_CONN_POSTGRES_OPENLEDGER_TESTING")


@pytest.fixture
def postgres_with_image_table():
    postgres = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    postgres.run(DROP_IMAGE_TABLE_QUERY)
    postgres.run(DROP_IMAGE_INDEX_QUERY)
    postgres.run(UUID_FUNCTION_QUERY)
    postgres.run(CREATE_IMAGE_TABLE_QUERY)
    postgres.run(UNIQUE_CONDITION_QUERY)

    yield postgres

    postgres.run(DROP_IMAGE_TABLE_QUERY)
    postgres.run(DROP_IMAGE_INDEX_QUERY)


@pytest.fixture
def mock_breakers(monkeypatch):
    def mock_get_license_info(
            license_url=None, license_=None, license_version=None
    ):
        assert 0 == 1

    monkeypatch.setattr(
        pg_cleaner.image.licenses,
        "get_license_info",
        mock_get_license_info,
    )

    def mock_validate_url_string(url_string):
        assert 0 == 1

    monkeypatch.setattr(
        pg_cleaner.image.columns.urls,
        "validate_url_string",
        mock_validate_url_string,
    )


def _load_tsv(postgres, tmpdir, tsv_file_name):
    tsv_file_path = os.path.join(RESOURCES, tsv_file_name)
    with open(tsv_file_path) as f:
        f_data = f.read()

    test_tsv = "test.tsv"
    path = tmpdir.join(test_tsv)
    path.write(f_data)
    postgres.bulk_load(TEST_IMAGE_TABLE, str(path))


def test_clean_rows_calls_add_item(tmpdir, postgres_with_image_table):
    tsv_name = os.path.join(RESOURCES, "image_table_sample.tsv")
    _load_tsv(postgres_with_image_table, tmpdir, tsv_name)
    expected_calls = [
        call(
            provider="smithsonian",
            output_file="cleaned_000000.tsv",
            output_dir="/tmp/workflow_output/overwrite/"
        ),
        call().add_item(
            foreign_landing_url="https://n2t.net/ark:/65665/3f07eb37b-d022-4d44-90de-179a4aaf1c82",
            image_url="https://ids.si.edu/ids/deliveryService/id/ark:/65665/m3272d5bfa5716461fbf173e083887621c",
            thumbnail_url="https://ids.si.edu/ids/deliveryService/id/ark:/65665/m3272d5bfa5716461fbf173e083887621c/90",
            license_url="https://creativecommons.org/publicdomain/zero/1.0/",
            license_="cc0",
            license_version="1.0",
            foreign_identifier="ark:/65665/m3272d5bfa5716461fbf173e083887621c",
            width=None,
            height=None,
            creator="Susan Gabriella Stokes",
            creator_url=None,
            title="Eriogonum latifolium Sm.",
            meta_data={
                "unit_code": "NMNHBOTANY",
                "data_source": "NMNH - Botany Dept.",
                "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
                "raw_license_url": "https://creativecommons.org/publicdomain/zero/1.0/"
            },
            raw_tags=[
                {"name": "1930s", "provider": "smithsonian"},
                {"name": "Dicotyledonae", "provider": "smithsonian"},
                {"name": "United States", "provider": "smithsonian"},
                {"name": "California", "provider": "smithsonian"},
                {"name": "North America", "provider": "smithsonian"}
            ],
            watermarked=False,
            source="smithsonian_national_museum_of_natural_history",
        ),
        call().commit(),
    ]
    with patch.object(
            pg_cleaner.image,
            "ImageStore",
            autospec=True,
    ) as mock_add_item:
        with pytest.raises(AssertionError):
            pg_cleaner.clean_rows(
                POSTGRES_CONN_ID, "000000", image_table=TEST_IMAGE_TABLE
            )

    mock_add_item.assert_has_calls(expected_calls)

import datetime
import os
import psycopg2
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


def _load_tsv(postgres, tmpdir, tsv_file_name):
    tsv_file_path = os.path.join(RESOURCES, tsv_file_name)
    with open(tsv_file_path) as f:
        f_data = f.read()

    test_tsv = "test.tsv"
    path = tmpdir.join(test_tsv)
    path.write(f_data)
    postgres.bulk_load(TEST_IMAGE_TABLE, str(path))


def test_clean_prefix_loop_raises_with_long_prefix(monkeypatch):
    with patch.object(pg_cleaner.time, "sleep") as mock_sleep:
        with patch.object(
            pg_cleaner,
            "clean_rows",
            side_effect=Exception("Super fail!"),
        ) as mock_cleaner:
            with pytest.raises(pg_cleaner.CleaningException):
                pg_cleaner.clean_prefix_loop(
                    "abc", "3f23", desired_prefix_length=3, delay_minutes=1
                )
    mock_cleaner.assert_called_once_with("abc", "3f23")
    mock_sleep.assert_not_called()


def test_clean_prefix_loop_handles_long_prefix(monkeypatch):
    with patch.object(pg_cleaner.time, "sleep") as mock_sleep:
        with patch.object(pg_cleaner, "clean_rows") as mock_cleaner:
            pg_cleaner.clean_prefix_loop(
                "abc", "3f23", desired_prefix_length=3, delay_minutes=1
            )
    mock_cleaner.assert_called_once_with("abc", "3f23")
    mock_sleep.assert_not_called()


def test_clean_prefix_loop_raises_after_looping(monkeypatch):
    expected_calls = [
        call("abc", "3fc0"),
        call("abc", "3fc1"),
        call("abc", "3fc2"),
        call("abc", "3fc3"),
        call("abc", "3fc4"),
        call("abc", "3fc5"),
        call("abc", "3fc6"),
        call("abc", "3fc7"),
        call("abc", "3fc8"),
        call("abc", "3fc9"),
        call("abc", "3fca"),
        call("abc", "3fcb"),
        call("abc", "3fcc"),
        call("abc", "3fcd"),
        call("abc", "3fce"),
        call("abc", "3fcf"),
    ]
    monkeypatch.setattr(pg_cleaner.time, "sleep", lambda x: None)
    with patch.object(
        pg_cleaner,
        "clean_rows",
        side_effect=Exception("Super fail!"),
    ) as mock_cleaner:
        with pytest.raises(pg_cleaner.CleaningException):
            pg_cleaner.clean_prefix_loop(
                "abc", "3fc", desired_prefix_length=4, delay_minutes=1
            )
    mock_cleaner.assert_has_calls(expected_calls)


def test_clean_prefix_loop_delays(monkeypatch):
    monkeypatch.setattr(pg_cleaner, "clean_rows", lambda x, y: None)
    with patch.object(pg_cleaner.time, "sleep") as mock_sleep:
        pg_cleaner.clean_prefix_loop(
            "abc", "3f", desired_prefix_length=3, delay_minutes=1
        )

    assert all([c[1][0] < 60 and c[1][0] > 55 for c in mock_sleep.mock_calls])


def test_clean_prefix_loop_loops(monkeypatch):
    monkeypatch.setattr(pg_cleaner.time, "sleep", lambda x: None)
    expected_calls = [
        call("abc", "3f0"),
        call("abc", "3f1"),
        call("abc", "3f2"),
        call("abc", "3f3"),
        call("abc", "3f4"),
        call("abc", "3f5"),
        call("abc", "3f6"),
        call("abc", "3f7"),
        call("abc", "3f8"),
        call("abc", "3f9"),
        call("abc", "3fa"),
        call("abc", "3fb"),
        call("abc", "3fc"),
        call("abc", "3fd"),
        call("abc", "3fe"),
        call("abc", "3ff"),
    ]
    with patch.object(
        pg_cleaner,
        "clean_rows",
    ) as mock_cleaner:
        pg_cleaner.clean_prefix_loop("abc", "3f", desired_prefix_length=3)

    mock_cleaner.assert_has_calls(expected_calls)


def test_clean_rows_continues_when_single_row_fails(monkeypatch):
    row_list = ["a", "b"]
    monkeypatch.setattr(pg_cleaner, "_select_records", lambda x, y: row_list)
    monkeypatch.setattr(pg_cleaner, "_log_and_check_totals", lambda x, y: None)

    with patch.object(
        pg_cleaner,
        "_clean_single_row",
        side_effect=Exception("cleaning fail!"),
    ) as mock_cleaner:
        pg_cleaner.clean_rows("abc", "def")

    assert len(mock_cleaner.mock_calls) == 2


def test_clean_rows_logs_defective_row_when_single_row_fails(monkeypatch):
    row_list = [
        ("my_row_number_one", "nextfield"),
        ("my_row_number_2", "anotherfield"),
    ]
    monkeypatch.setattr(pg_cleaner, "_select_records", lambda x, y: row_list)
    monkeypatch.setattr(pg_cleaner, "_log_and_check_totals", lambda x, y: None)

    def make_a_problem(a, b, c):
        assert 3 == 4

    monkeypatch.setattr(pg_cleaner, "_clean_single_row", make_a_problem)

    with patch.object(pg_cleaner.logger, "warning") as mock_warner:
        pg_cleaner.clean_rows("abc", "def")

    log_concat = " ".join([str(c) for c in mock_warner.mock_calls])
    assert all([str(r) in log_concat for r in row_list])


def test_clean_rows_raises_when_log_and_check_fails(monkeypatch):
    row_list = [
        ("my_row_number_one", "nextfield"),
        ("my_row_number_2", "anotherfield"),
    ]
    expect_exception_message = "test exception!"
    monkeypatch.setattr(pg_cleaner, "_select_records", lambda x, y: row_list)

    def make_a_problem(a, b):
        raise Exception(expect_exception_message)

    monkeypatch.setattr(pg_cleaner, "_log_and_check_totals", make_a_problem)
    monkeypatch.setattr(pg_cleaner, "_clean_single_row", lambda x, y, z: None)

    with pytest.raises(Exception) as e:
        pg_cleaner.clean_rows("abc", "def")

    assert expect_exception_message == str(e.value)


def test_select_records_gets_one_record(tmpdir, postgres_with_image_table):
    tsv_name = os.path.join(RESOURCES, "image_table_sample.tsv")
    _load_tsv(postgres_with_image_table, tmpdir, tsv_name)
    expect_records = [
        (
            "000000ea-9a81-47dd-a83c-a2093ea4741b",
            datetime.datetime(
                2020,
                10,
                12,
                18,
                11,
                57,
                791507,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
            ),
            datetime.datetime(
                2020,
                10,
                15,
                8,
                10,
                42,
                421899,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
            ),
            "provider_api",
            "smithsonian",
            "smithsonian_national_museum_of_natural_history",
            "ark:/65665/m3272d5bfa5716461fbf173e083887621c",
            "https://n2t.net/ark:/65665/3f07eb37b-d022-4d44-90de-179a4aaf1c82",
            "https://ids.si.edu/ids/deliveryService/id/ark:/65665/m3272d5bfa5716461fbf173e083887621c",
            "https://ids.si.edu/ids/deliveryService/id/ark:/65665/m3272d5bfa5716461fbf173e083887621c/90",
            None,
            None,
            None,
            "cc0",
            "1.0",
            "Susan Gabriella Stokes",
            None,
            "Eriogonum latifolium Sm.",
            {
                "unit_code": "NMNHBOTANY",
                "data_source": "NMNH - Botany Dept.",
                "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
                "raw_license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
            },
            [
                {"name": "1930s", "provider": "smithsonian"},
                {"name": "Dicotyledonae", "provider": "smithsonian"},
                {"name": "United States", "provider": "smithsonian"},
                {"name": "California", "provider": "smithsonian"},
                {"name": "North America", "provider": "smithsonian"},
            ],
            False,
            datetime.datetime(
                2020,
                10,
                15,
                8,
                10,
                42,
                421899,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
            ),
            False,
        )
    ]
    actual_records = pg_cleaner._select_records(
        POSTGRES_CONN_ID, "000000", image_table=TEST_IMAGE_TABLE
    )
    assert actual_records == expect_records


def test_select_records_gets_multiple_records(
    tmpdir, postgres_with_image_table
):
    tsv_name = os.path.join(RESOURCES, "image_table_sample.tsv")
    _load_tsv(postgres_with_image_table, tmpdir, tsv_name)
    expect_records = [
        (
            "000000ea-9a81-47dd-a83c-a2093ea4741b",
            datetime.datetime(
                2020,
                10,
                12,
                18,
                11,
                57,
                791507,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
            ),
            datetime.datetime(
                2020,
                10,
                15,
                8,
                10,
                42,
                421899,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
            ),
            "provider_api",
            "smithsonian",
            "smithsonian_national_museum_of_natural_history",
            "ark:/65665/m3272d5bfa5716461fbf173e083887621c",
            "https://n2t.net/ark:/65665/3f07eb37b-d022-4d44-90de-179a4aaf1c82",
            "https://ids.si.edu/ids/deliveryService/id/ark:/65665/m3272d5bfa5716461fbf173e083887621c",
            "https://ids.si.edu/ids/deliveryService/id/ark:/65665/m3272d5bfa5716461fbf173e083887621c/90",
            None,
            None,
            None,
            "cc0",
            "1.0",
            "Susan Gabriella Stokes",
            None,
            "Eriogonum latifolium Sm.",
            {
                "unit_code": "NMNHBOTANY",
                "data_source": "NMNH - Botany Dept.",
                "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
                "raw_license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
            },
            [
                {"name": "1930s", "provider": "smithsonian"},
                {"name": "Dicotyledonae", "provider": "smithsonian"},
                {"name": "United States", "provider": "smithsonian"},
                {"name": "California", "provider": "smithsonian"},
                {"name": "North America", "provider": "smithsonian"},
            ],
            False,
            datetime.datetime(
                2020,
                10,
                15,
                8,
                10,
                42,
                421899,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
            ),
            False,
        ),
        (
            "000008ce-9150-4e9d-99d4-a26882220081",
            datetime.datetime(
                2020,
                10,
                12,
                18,
                11,
                57,
                791507,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
            ),
            datetime.datetime(
                2020,
                10,
                15,
                8,
                10,
                42,
                421899,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
            ),
            "provider_api",
            "smithsonian",
            "smithsonian_national_museum_of_natural_history",
            "ark:/65665/m33f5237895c464e6bb6f133e8133891f6",
            "https://n2t.net/ark:/65665/334a650c2-9c2a-4394-898c-9f809808ef83",
            "https://ids.si.edu/ids/deliveryService/id/ark:/65665/m33f5237895c464e6bb6f133e8133891f6",
            "https://ids.si.edu/ids/deliveryService/id/ark:/65665/m33f5237895c464e6bb6f133e8133891f6/90",
            None,
            None,
            None,
            "cc0",
            "1.0",
            "John O. Snyder",
            None,
            "Hesperoleucus mitrulus",
            {
                "unit_code": "NMNHFISHES",
                "data_source": "NMNH - Vertebrate Zoology - Fishes Division",
                "description": "Type status confirmed by c. r. gilbert, 1985.",
                "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
                "raw_license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
            },
            [
                {"name": "1900s", "provider": "smithsonian"},
                {"name": "Actinopterygii", "provider": "smithsonian"},
                {"name": "Fishes", "provider": "smithsonian"},
                {"name": "Oregon", "provider": "smithsonian"},
                {"name": "Lake County", "provider": "smithsonian"},
                {"name": "United States", "provider": "smithsonian"},
                {"name": "North America", "provider": "smithsonian"},
            ],
            False,
            datetime.datetime(
                2020,
                10,
                15,
                8,
                10,
                42,
                421899,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
            ),
            False,
        ),
        (
            "00000924-dbe5-438f-a271-8b866b9e6d78",
            datetime.datetime(
                2020,
                10,
                12,
                18,
                11,
                57,
                791507,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
            ),
            datetime.datetime(
                2020,
                10,
                15,
                8,
                10,
                42,
                421899,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
            ),
            "provider_api",
            "smithsonian",
            "smithsonian_national_museum_of_natural_history",
            "ark:/65665/m346a7ed5bbf9b4377896d687507c07a09",
            "https://n2t.net/ark:/65665/30e935ee9-5949-464e-8d79-3b2c22b1f2a0",
            "https://ids.si.edu/ids/deliveryService/id/ark:/65665/m346a7ed5bbf9b4377896d687507c07a09",
            "https://ids.si.edu/ids/deliveryService/id/ark:/65665/m346a7ed5bbf9b4377896d687507c07a09/90",
            None,
            None,
            None,
            "cc0",
            "1.0",
            "Manuel López Figueiras",
            None,
            "Espeletia schultzii var. mucurubana Cuatrec.",
            {
                "unit_code": "NMNHBOTANY",
                "data_source": "NMNH - Botany Dept.",
                "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
                "raw_license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
            },
            [
                {"name": "1980s", "provider": "smithsonian"},
                {"name": "Dicotyledonae", "provider": "smithsonian"},
                {"name": "Mu00e9rida", "provider": "smithsonian"},
                {
                    "name": "South America - Neotropics",
                    "provider": "smithsonian",
                },
                {"name": "Venezuela", "provider": "smithsonian"},
            ],
            False,
            datetime.datetime(
                2020,
                10,
                15,
                8,
                10,
                42,
                421899,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
            ),
            False,
        ),
    ]

    actual_records = pg_cleaner._select_records(
        POSTGRES_CONN_ID, "00000", image_table=TEST_IMAGE_TABLE
    )
    print(actual_records)
    assert actual_records == expect_records


def test_clean_single_row_inits_image_store_and_adds_row():
    row = (
        "000000ea-9a81-47dd-a83c-a2093ea4741b",
        datetime.datetime(
            2020,
            10,
            12,
            18,
            11,
            57,
            791507,
            tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
        ),
        datetime.datetime(
            2020,
            10,
            15,
            8,
            10,
            42,
            421899,
            tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
        ),
        "provider_api",
        "smithsonian",
        "smithsonian_national_museum_of_natural_history",
        "ark:/65665/m3272d5bfa5716461fbf173e083887621c",
        "https://n2t.net/ark:/65665/3f07eb37b-d022-4d44-90de-179a4aaf1c82",
        "https://ids.si.edu/ids/deliveryService/id/ark:/65665/m3272d5bfa5716461fbf173e083887621c",
        "https://ids.si.edu/ids/deliveryService/id/ark:/65665/m3272d5bfa5716461fbf173e083887621c/90",
        None,
        None,
        None,
        "cc0",
        "1.0",
        "Susan Gabriella Stokes",
        None,
        "Eriogonum latifolium Sm.",
        {
            "unit_code": "NMNHBOTANY",
            "data_source": "NMNH - Botany Dept.",
            "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
            "raw_license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
        },
        [
            {"name": "1930s", "provider": "smithsonian"},
            {"name": "Dicotyledonae", "provider": "smithsonian"},
            {"name": "United States", "provider": "smithsonian"},
            {"name": "California", "provider": "smithsonian"},
            {"name": "North America", "provider": "smithsonian"},
        ],
        False,
        datetime.datetime(
            2020,
            10,
            15,
            8,
            10,
            42,
            421899,
            tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
        ),
        False,
    )
    image_store_dict = pg_cleaner.ImageStoreDict()
    expected_calls = [
        call(
            provider="smithsonian",
            output_file="cleaned_000000.tsv",
            output_dir=os.path.join(
                pg_cleaner.OUTPUT_DIR_PATH, pg_cleaner.OVERWRITE_DIR,
            ),
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
                "raw_license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
            },
            raw_tags=[
                {"name": "1930s", "provider": "smithsonian"},
                {"name": "Dicotyledonae", "provider": "smithsonian"},
                {"name": "United States", "provider": "smithsonian"},
                {"name": "California", "provider": "smithsonian"},
                {"name": "North America", "provider": "smithsonian"},
            ],
            watermarked=False,
            source="smithsonian_national_museum_of_natural_history",
        ),
    ]
    with patch.object(pg_cleaner.image, "ImageStore") as mock_image_store:
        pg_cleaner._clean_single_row(row, image_store_dict, "000000")

    mock_image_store.assert_has_calls(expected_calls)


def test_clean_single_row_reuses_image_store_and_adds_row():
    row = (
        "000000ea-9a81-47dd-a83c-a2093ea4741b",
        datetime.datetime(
            2020,
            10,
            12,
            18,
            11,
            57,
            791507,
            tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
        ),
        datetime.datetime(
            2020,
            10,
            15,
            8,
            10,
            42,
            421899,
            tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
        ),
        "provider_api",
        "smithsonian",
        "smithsonian_national_museum_of_natural_history",
        "ark:/65665/m3272d5bfa5716461fbf173e083887621c",
        "https://n2t.net/ark:/65665/3f07eb37b-d022-4d44-90de-179a4aaf1c82",
        "https://ids.si.edu/ids/deliveryService/id/ark:/65665/m3272d5bfa5716461fbf173e083887621c",
        "https://ids.si.edu/ids/deliveryService/id/ark:/65665/m3272d5bfa5716461fbf173e083887621c/90",
        None,
        None,
        None,
        "cc0",
        "1.0",
        "Susan Gabriella Stokes",
        None,
        "Eriogonum latifolium Sm.",
        {
            "unit_code": "NMNHBOTANY",
            "data_source": "NMNH - Botany Dept.",
            "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
            "raw_license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
        },
        [
            {"name": "1930s", "provider": "smithsonian"},
            {"name": "Dicotyledonae", "provider": "smithsonian"},
            {"name": "United States", "provider": "smithsonian"},
            {"name": "California", "provider": "smithsonian"},
            {"name": "North America", "provider": "smithsonian"},
        ],
        False,
        datetime.datetime(
            2020,
            10,
            15,
            8,
            10,
            42,
            421899,
            tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
        ),
        False,
    )
    expected_calls = [
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
                "raw_license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
            },
            raw_tags=[
                {"name": "1930s", "provider": "smithsonian"},
                {"name": "Dicotyledonae", "provider": "smithsonian"},
                {"name": "United States", "provider": "smithsonian"},
                {"name": "California", "provider": "smithsonian"},
                {"name": "North America", "provider": "smithsonian"},
            ],
            watermarked=False,
            source="smithsonian_national_museum_of_natural_history",
        )
    ]
    with patch.object(pg_cleaner.image, "ImageStore") as mock_image_store:
        image_store_dict = pg_cleaner.ImageStoreDict()
        image_store_dict[("smithsonian", "000000")]

    # This checks for reuse, since otherwise it would init a *real* ImageStore
    # outside of the block, and fail to call mock.add_item.
    pg_cleaner._clean_single_row(row, image_store_dict, "000000")
    mock_image_store.assert_has_calls(expected_calls)


def test_clean_single_row_doesnt_reuse_wrong_image_store_and_adds_row():
    row = (
        "000000ea-9a81-47dd-a83c-a2093ea4741b",
        datetime.datetime(
            2020,
            10,
            12,
            18,
            11,
            57,
            791507,
            tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
        ),
        datetime.datetime(
            2020,
            10,
            15,
            8,
            10,
            42,
            421899,
            tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
        ),
        "provider_api",
        "smithsonian",
        "smithsonian_national_museum_of_natural_history",
        "ark:/65665/m3272d5bfa5716461fbf173e083887621c",
        "https://n2t.net/ark:/65665/3f07eb37b-d022-4d44-90de-179a4aaf1c82",
        "https://ids.si.edu/ids/deliveryService/id/ark:/65665/m3272d5bfa5716461fbf173e083887621c",
        "https://ids.si.edu/ids/deliveryService/id/ark:/65665/m3272d5bfa5716461fbf173e083887621c/90",
        None,
        None,
        None,
        "cc0",
        "1.0",
        "Susan Gabriella Stokes",
        None,
        "Eriogonum latifolium Sm.",
        {
            "unit_code": "NMNHBOTANY",
            "data_source": "NMNH - Botany Dept.",
            "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
            "raw_license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
        },
        [
            {"name": "1930s", "provider": "smithsonian"},
            {"name": "Dicotyledonae", "provider": "smithsonian"},
            {"name": "United States", "provider": "smithsonian"},
            {"name": "California", "provider": "smithsonian"},
            {"name": "North America", "provider": "smithsonian"},
        ],
        False,
        datetime.datetime(
            2020,
            10,
            15,
            8,
            10,
            42,
            421899,
            tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
        ),
        False,
    )
    expected_calls = [
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
                "raw_license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
            },
            raw_tags=[
                {"name": "1930s", "provider": "smithsonian"},
                {"name": "Dicotyledonae", "provider": "smithsonian"},
                {"name": "United States", "provider": "smithsonian"},
                {"name": "California", "provider": "smithsonian"},
                {"name": "North America", "provider": "smithsonian"},
            ],
            watermarked=False,
            source="smithsonian_national_museum_of_natural_history",
        )
    ]
    image_store_dict = pg_cleaner.ImageStoreDict()
    image_store_dict[("samsonion", "000000")]
    with patch.object(pg_cleaner.image, "ImageStore") as mock_image_store:
        pg_cleaner._clean_single_row(row, image_store_dict, "000000")

    mock_image_store.assert_has_calls(expected_calls)


def test_log_and_check_totals_raises_when_number_of_images_cleaned_is_wrong(
    monkeypatch,
):
    monkeypatch.setattr(pg_cleaner.image.ImageStore, "total_images", 1)
    expected_calls = [
        call.info("Total images cleaned:  2"),
        call.info(
            "Image Totals breakdown:  {('abc', '000'): 1, ('def', '000'): 1}"
        ),
        call.warning("total_images_sum NOT EQUAL TO total_rows!"),
        call.warning("total_images_sum: 2"),
        call.warning("total_rows: 3"),
    ]
    image_store_dict = pg_cleaner.ImageStoreDict()
    image_store_dict[("abc", "000")]
    image_store_dict[("def", "000")]
    with patch.object(pg_cleaner, "logger") as mock_logger:
        with pytest.raises(AssertionError):
            pg_cleaner._log_and_check_totals(3, image_store_dict)

    assert mock_logger.has_calls(expected_calls)


def test_log_and_check_totals_logs(monkeypatch):
    monkeypatch.setattr(pg_cleaner.image.ImageStore, "total_images", 1)
    expected_calls = [
        call.info("Total images cleaned:  2"),
        call.info(
            "Image Totals breakdown:  {('abc', '000'): 1, ('def', '000'): 1}"
        ),
    ]
    image_store_dict = pg_cleaner.ImageStoreDict()
    image_store_dict[("abc", "000")]
    image_store_dict[("def", "000")]
    with patch.object(pg_cleaner, "logger") as mock_logger:
        pg_cleaner._log_and_check_totals(2, image_store_dict)

    assert mock_logger.has_calls(expected_calls)

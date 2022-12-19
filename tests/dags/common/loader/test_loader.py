from unittest import mock

import pytest
from common.loader import loader
from common.loader.reporting import RecordMetrics


@pytest.mark.parametrize(
    "load_value, clean_data_value, upsert_value, expected",
    [
        (100, (10, 15), 75, RecordMetrics(75, 10, 15, 0)),
        (100, (0, 15), 75, RecordMetrics(75, 0, 15, 10)),
        (100, (10, 0), 75, RecordMetrics(75, 10, 0, 15)),
    ],
)
def test_upsert_data_calculations(load_value, clean_data_value, upsert_value, expected):
    with mock.patch("common.loader.loader.sql") as sql_mock:
        sql_mock.clean_intermediate_table_data.return_value = clean_data_value
        sql_mock.upsert_records_to_db_table.return_value = upsert_value

        actual = loader.upsert_data(
            mock.Mock(), "fake", "fake", "fake", load_value, clean_data_value
        )
        assert actual == expected

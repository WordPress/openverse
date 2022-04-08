from unittest import mock

import pytest
from common.loader import loader
from common.loader.reporting import RecordMetrics


@pytest.mark.parametrize(
    "load_value, upsert_value, expected",
    [
        ((100, 10, 15), 75, RecordMetrics(75, 10, 15, 0)),
        ((100, 0, 15), 75, RecordMetrics(75, 0, 15, 10)),
        ((100, 10, 0), 75, RecordMetrics(75, 10, 0, 15)),
    ],
)
def test_load_from_s3_calculations(load_value, upsert_value, expected):
    with mock.patch("common.loader.loader.sql") as sql_mock:
        sql_mock.load_s3_data_to_intermediate_table.return_value = load_value
        sql_mock.upsert_records_to_db_table.return_value = upsert_value

        actual = loader.load_from_s3(
            mock.Mock(), "fake", "fake", "fake", "fake", "fake"
        )
        assert actual == expected

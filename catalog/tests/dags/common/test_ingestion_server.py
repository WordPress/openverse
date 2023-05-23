from unittest.mock import MagicMock

import pytest
from airflow.exceptions import AirflowSkipException

from common import ingestion_server


@pytest.mark.parametrize(
    "data, expected",
    [
        ({"exists": True, "is_alias": False, "alt_names": "asdf-1234"}, "1234"),
        pytest.param(
            {"exists": False, "is_alias": None, "alt_names": None},
            None,
            marks=pytest.mark.raises(exception=AirflowSkipException),
        ),
        pytest.param({}, None, marks=pytest.mark.raises(exception=KeyError)),
    ],
)
def test_response_filter_stat(data, expected):
    response = MagicMock()
    response.json.return_value = data
    actual = ingestion_server.response_filter_stat(response)
    assert actual == expected

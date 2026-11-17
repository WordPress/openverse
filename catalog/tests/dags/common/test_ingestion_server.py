from datetime import timedelta
from unittest import mock

import pytest
import requests
from airflow.sdk import DAG
from airflow.sdk.exceptions import AirflowSkipException
from airflow.sdk.timezone import datetime

from common import ingestion_server


TEST_START_DATE = datetime(2022, 2, 1, 0, 0, 0)


@pytest.fixture()
def index_readiness_dag(sample_dag_id_fixture, clean_db):
    # Create a DAG that just has an index_readiness_check task
    with DAG(
        dag_id=sample_dag_id_fixture, schedule=None, start_date=TEST_START_DATE
    ) as dag:
        ingestion_server.index_readiness_check(
            media_type="image", index_suffix="my_test_suffix", timeout=timedelta(days=1)
        )
    return dag


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
    response = mock.MagicMock()
    response.json.return_value = data
    actual = ingestion_server.response_filter_stat(response)
    assert actual == expected


@pytest.mark.parametrize(
    "response_code, response_json, expected",
    [
        pytest.param(
            200,
            {"hits": {"total": {"value": 20_000, "relation": "eq"}}},
            True,
            id="healthy-index",
        ),
        pytest.param(
            200,
            {"hits": {"total": {"value": 100, "relation": "eq"}}},
            False,
            id="not-enough-records",
        ),
        pytest.param(200, {"foo": "bar"}, False, id="missing-hits"),
        pytest.param(
            404,
            {"error": {"root_cause": [{"type": "index_not_found_exception"}]}},
            False,
            id="index-not-found-error",
        ),
    ],
)
def test_index_readiness_check(
    index_readiness_dag, response_code, response_json, expected
):
    sensor = index_readiness_dag.get_task(task_id="index_readiness_check")

    with mock.patch("requests.Session.send") as mock_session_send:
        r = requests.Response()
        r.status_code = response_code
        r.reason = "test"
        r.json = mock.MagicMock(return_value=response_json)
        mock_session_send.return_value = r

        assert sensor.poke(context={}) is expected

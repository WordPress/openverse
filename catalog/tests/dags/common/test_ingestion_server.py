from datetime import timedelta
from unittest import mock

import pytest
import requests
from airflow.exceptions import AirflowSkipException
from airflow.models.dag import DAG
from airflow.utils.state import DagRunState, TaskInstanceState
from airflow.utils.timezone import datetime
from airflow.utils.types import DagRunType

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
    "response_code, response_json, expected_status",
    [
        pytest.param(
            200,
            {"hits": {"total": {"value": 20_000, "relation": "eq"}}},
            TaskInstanceState.SUCCESS,
            id="healthy-index",
        ),
        pytest.param(
            200,
            {"hits": {"total": {"value": 100, "relation": "eq"}}},
            TaskInstanceState.UP_FOR_RESCHEDULE,
            id="not-enough-records",
        ),
        pytest.param(
            200, {"foo": "bar"}, TaskInstanceState.UP_FOR_RESCHEDULE, id="missing-hits"
        ),
        pytest.param(
            404,
            {"error": {"root_cause": [{"type": "index_not_found_exception"}]}},
            TaskInstanceState.UP_FOR_RESCHEDULE,
            id="index-not-found-error",
        ),
    ],
)
def test_index_readiness_check(
    index_readiness_dag, response_code, response_json, expected_status
):
    execution_date = TEST_START_DATE + timedelta(days=1)
    dagrun = index_readiness_dag.create_dagrun(
        start_date=execution_date,
        execution_date=execution_date,
        data_interval=(execution_date, execution_date),
        state=DagRunState.RUNNING,
        run_type=DagRunType.MANUAL,
    )

    with mock.patch(
        "airflow.providers.http.hooks.http.requests.Session.send"
    ) as mock_session_send:
        r = requests.Response()
        r.status_code = response_code
        r.reason = "test"
        r.json = mock.MagicMock(return_value=response_json)
        mock_session_send.return_value = r

        ti = dagrun.get_task_instance(task_id="index_readiness_check")
        ti.task = index_readiness_dag.get_task(task_id="index_readiness_check")
        ti.run()
        assert ti.state == expected_status

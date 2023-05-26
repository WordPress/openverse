from datetime import timedelta
from unittest import mock

import pytest
import requests
from airflow.exceptions import AirflowException, AirflowSkipException
from airflow.models import DagRun, TaskInstance
from airflow.models.dag import DAG
from airflow.utils.session import create_session
from airflow.utils.state import DagRunState, TaskInstanceState
from airflow.utils.timezone import datetime
from airflow.utils.types import DagRunType

from common import ingestion_server


TEST_START_DATE = datetime(2022, 2, 1, 0, 0, 0)
TEST_DAG_ID = "api_healthcheck_test_dag"


@pytest.fixture(autouse=True)
def clean_db():
    with create_session() as session:
        # synchronize_session='fetch' required here to refresh models
        # https://stackoverflow.com/a/51222378 CC BY-SA 4.0
        session.query(DagRun).filter(DagRun.dag_id.startswith(TEST_DAG_ID)).delete(
            synchronize_session="fetch"
        )
        session.query(TaskInstance).filter(
            TaskInstance.dag_id.startswith(TEST_DAG_ID)
        ).delete(synchronize_session="fetch")


@pytest.fixture()
def healthcheck_dag():
    index_suffix = "my-test-suffix"

    # Create a DAG that just has an api_health_check task
    with DAG(dag_id=TEST_DAG_ID, schedule=None, start_date=TEST_START_DATE) as dag:
        ingestion_server.api_health_check(
            media_type="image", index_suffix=index_suffix, timeout=timedelta(days=1)
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
        # Pass
        (200, {"result_count": 10000}, TaskInstanceState.SUCCESS),
        # No result count
        (200, {}, TaskInstanceState.UP_FOR_RESCHEDULE),
        (200, {"foo": "bar"}, TaskInstanceState.UP_FOR_RESCHEDULE),
        # Not enough records
        (200, {"result_count": 0}, TaskInstanceState.UP_FOR_RESCHEDULE),
        (200, {"result_count": 100}, TaskInstanceState.UP_FOR_RESCHEDULE),
        # Errors
        pytest.param(
            400,
            {"detail": {"internal__index": ["Invalid index name `audio-foo`."]}},
            TaskInstanceState.UP_FOR_RETRY,
            marks=pytest.mark.raises(exception=AirflowException),
        ),
    ],
)
def test_api_health_check(
    healthcheck_dag, response_code, response_json, expected_status
):
    execution_date = TEST_START_DATE + timedelta(days=1)
    dagrun = healthcheck_dag.create_dagrun(
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

        ti = dagrun.get_task_instance(task_id="api_health_check")
        ti.task = healthcheck_dag.get_task(task_id="api_health_check")
        ti.run()
        assert ti.state == expected_status

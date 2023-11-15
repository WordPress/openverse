from datetime import timedelta

import pytest
from airflow.models.dag import DAG
from airflow.utils.state import State
from airflow.utils.timezone import datetime
from airflow.utils.types import DagRunType

from common.sensors.utils import get_most_recent_dag_run


TEST_DAG_ID = "data_refresh_dag_factory_test_dag"
TEST_DAG = DAG(TEST_DAG_ID, default_args={"owner": "airflow"})

@pytest.fixture()
def get_test_dag_id():
    return TEST_DAG_ID

def _create_dagrun(start_date, conf={}):
    return TEST_DAG.create_dagrun(
        start_date=start_date,
        execution_date=start_date,
        data_interval=(start_date, start_date),
        state=State.SUCCESS,
        run_type=DagRunType.MANUAL,
        conf=conf,
    )


def test_get_most_recent_dag_run_returns_most_recent_execution_date():
    most_recent = datetime(2023, 5, 10)
    for i in range(3):
        _create_dagrun(most_recent - timedelta(days=i))

    assert get_most_recent_dag_run(TEST_DAG_ID) == most_recent


def test_get_most_recent_dag_run_returns_empty_list_when_no_runs():
    # Relies on ``clean_db`` cleaning up DagRuns from other tests
    assert get_most_recent_dag_run(TEST_DAG_ID) == []

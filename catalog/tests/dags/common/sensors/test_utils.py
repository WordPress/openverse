from datetime import timedelta

from airflow.models.dag import DAG
from airflow.utils.state import State
from airflow.utils.timezone import datetime
from airflow.utils.types import DagRunType

from common.sensors.utils import get_most_recent_dag_run


TEST_DAG_ID = "data_refresh_dag_factory_test_dag"
TEST_DAG = DAG(TEST_DAG_ID, default_args={"owner": "airflow"})


def _create_dagrun(start_date, sample_dag_id_fixture, conf={}):
    return DAG(sample_dag_id_fixture, default_args={"owner": "airflow"}).create_dagrun(
        start_date=start_date,
        execution_date=start_date,
        data_interval=(start_date, start_date),
        state=State.SUCCESS,
        run_type=DagRunType.MANUAL,
        conf=conf,
    )


def test_get_most_recent_dag_run_returns_most_recent_execution_date(
    sample_dag_id_fixture, clean_db
):
    most_recent = datetime(2023, 5, 10)
    for i in range(3):
        _create_dagrun(most_recent - timedelta(days=i), sample_dag_id_fixture)
    assert get_most_recent_dag_run(sample_dag_id_fixture) == most_recent


def test_get_most_recent_dag_run_returns_empty_list_when_no_runs(
    sample_dag_id_fixture, clean_db
):
    # Relies on ``clean_db`` cleaning up DagRuns from other tests
    assert get_most_recent_dag_run(sample_dag_id_fixture) == []

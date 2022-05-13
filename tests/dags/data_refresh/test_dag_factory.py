import pytest
from airflow.models import DagRun
from airflow.models.dag import DAG
from airflow.utils.session import create_session
from airflow.utils.state import State
from airflow.utils.timezone import datetime
from airflow.utils.types import DagRunType
from data_refresh import dag_factory
from data_refresh.dag_factory import (
    REFRESH_MATERIALIZED_VIEW_TASK_ID,
    REFRESH_POPULARITY_METRICS_TASK_ID,
)


TEST_DAG_ID = "data_refresh_dag_factory_test_dag"
TEST_DAG = DAG(TEST_DAG_ID, default_args={"owner": "airflow"})


@pytest.fixture(autouse=True)
def clean_db():
    with create_session() as session:
        session.query(DagRun).filter(DagRun.dag_id == TEST_DAG_ID).delete()


def _create_dagrun(start_date, dag_state, conf={}):
    return TEST_DAG.create_dagrun(
        start_date=start_date,
        execution_date=start_date,
        data_interval=(start_date, start_date),
        state=dag_state,
        run_type=DagRunType.MANUAL,
        conf=conf,
    )


@pytest.mark.parametrize(
    "force_refresh_metrics, last_dagrun_date, today_date, expected_task_id",
    [
        # Last dagrun was in the same month
        (
            None,
            datetime(2022, 3, 1, 0, 0, 0),
            datetime(2022, 3, 2, 0, 0, 0),
            REFRESH_MATERIALIZED_VIEW_TASK_ID,
        ),
        # Last dagrun was in the same month, different year
        (
            None,
            datetime(2021, 3, 1, 0, 0, 0),
            datetime(2022, 3, 2, 0, 0, 0),
            REFRESH_POPULARITY_METRICS_TASK_ID,
        ),
        # Last dagrun was in a previous month
        (
            None,
            datetime(2022, 2, 1, 0, 0, 0),
            datetime(2022, 3, 2, 0, 0, 0),
            REFRESH_POPULARITY_METRICS_TASK_ID,
        ),
        # `force_refresh_metrics` is turned on
        # Last dagrun was in the same month
        (
            True,
            datetime(2022, 3, 1, 0, 0, 0),
            datetime(2022, 3, 2, 0, 0, 0),
            REFRESH_POPULARITY_METRICS_TASK_ID,
        ),
        # Last dagrun was in a previous month
        (
            True,
            datetime(2022, 2, 1, 0, 0, 0),
            datetime(2022, 3, 2, 0, 0, 0),
            REFRESH_POPULARITY_METRICS_TASK_ID,
        ),
        # `force_refresh_metrics` is explicitly false
        # Last dagrun was in the same month
        (
            False,
            datetime(2022, 3, 1, 0, 0, 0),
            datetime(2022, 3, 2, 0, 0, 0),
            REFRESH_MATERIALIZED_VIEW_TASK_ID,
        ),
        # Last dagrun was in a previous month
        (
            False,
            datetime(2022, 2, 1, 0, 0, 0),
            datetime(2022, 3, 2, 0, 0, 0),
            REFRESH_MATERIALIZED_VIEW_TASK_ID,
        ),
    ],
)
def test_month_check_returns_correct_task_id(
    force_refresh_metrics, last_dagrun_date, today_date, expected_task_id
):
    # Create latest dagrun
    _create_dagrun(last_dagrun_date, State.SUCCESS)
    # Create current dagrun
    _create_dagrun(
        today_date, State.RUNNING, {"force_refresh_metrics": force_refresh_metrics}
    )

    next_task_id = dag_factory._month_check(TEST_DAG.dag_id)
    assert next_task_id == expected_task_id


def test_month_check_ignores_failed_dagruns():
    # Create running dagrun
    _create_dagrun(datetime(2022, 3, 2, 0, 0, 0), State.RUNNING)

    # Create previous dagrun in same month, but with failed state
    _create_dagrun(datetime(2022, 3, 1, 0, 0, 0), State.FAILED)

    # Create successful dagrun in previous month
    _create_dagrun(datetime(2022, 2, 1, 0, 0, 0), State.SUCCESS)

    # Even though there was a previous run this month, it failed. The last
    # successful run was last month, so we should refresh metrics.
    next_task_id = dag_factory._month_check(TEST_DAG.dag_id)
    assert next_task_id == REFRESH_POPULARITY_METRICS_TASK_ID

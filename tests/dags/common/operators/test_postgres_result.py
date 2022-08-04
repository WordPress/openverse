"""
Based on:
https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html#unit-tests
"""
import datetime
import os

import pendulum
import pytest
from airflow import DAG
from airflow.models import DagRun, TaskInstance
from airflow.utils.session import create_session
from airflow.utils.state import DagRunState, TaskInstanceState
from airflow.utils.types import DagRunType
from common.operators.postgres_result import PostgresResultOperator


DATA_INTERVAL_START = pendulum.datetime(2021, 9, 13, tz="UTC")
DATA_INTERVAL_END = DATA_INTERVAL_START + datetime.timedelta(days=1)

TEST_DAG_ID = "test_postgres_result_dag"
TEST_TASK_ID = "test_postgres_result_task"
DB_CONN_ID = os.getenv("OPENLEDGER_CONN_ID", "postgres_openledger_testing")


@pytest.fixture(autouse=True)
def clean_db():
    with create_session() as session:
        session.query(DagRun).filter(DagRun.dag_id == TEST_DAG_ID).delete()
        session.query(TaskInstance).filter(TaskInstance.dag_id == TEST_DAG_ID).delete()
        yield
        session.query(DagRun).filter(DagRun.dag_id == TEST_DAG_ID).delete()
        session.query(TaskInstance).filter(TaskInstance.dag_id == TEST_DAG_ID).delete()


def get_dag(sql, handler):
    with DAG(
        dag_id=TEST_DAG_ID,
        schedule_interval="@daily",
        start_date=DATA_INTERVAL_START,
    ) as dag:
        PostgresResultOperator(
            task_id=TEST_TASK_ID, postgres_conn_id=DB_CONN_ID, sql=sql, handler=handler
        )
    return dag


@pytest.mark.parametrize(
    "sql, handler, expected",
    [
        ["SELECT 1", lambda c: c.fetchone(), (1,)],
        ["SELECT 1", lambda c: c.fetchone()[0], 1],
        ["SELECT UNNEST(ARRAY[1, 2, 3])", lambda c: c.fetchone(), (1,)],
        ["SELECT UNNEST(ARRAY[1, 2, 3])", lambda c: c.fetchall(), [(1,), (2,), (3,)]],
        ["SELECT UNNEST(ARRAY[1, 2, 3])", lambda c: c.rowcount, 3],
    ],
)
def test_postgres_result_operator(sql, handler, expected):
    dag = get_dag(sql, handler)
    dagrun = dag.create_dagrun(
        state=DagRunState.RUNNING,
        execution_date=DATA_INTERVAL_START,
        data_interval=(DATA_INTERVAL_START, DATA_INTERVAL_END),
        start_date=DATA_INTERVAL_END,
        run_type=DagRunType.MANUAL,
    )
    ti: TaskInstance = dagrun.get_task_instance(task_id=TEST_TASK_ID)
    ti.task = dag.get_task(task_id=TEST_TASK_ID)
    ti.run(ignore_ti_state=True)
    assert ti.state == TaskInstanceState.SUCCESS
    value = ti.xcom_pull(TEST_TASK_ID)
    assert value == expected

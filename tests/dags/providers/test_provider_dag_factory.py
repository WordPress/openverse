from unittest import mock

import pytest
from airflow.exceptions import AirflowSkipException, BackfillUnfinished
from airflow.executors.debug_executor import DebugExecutor
from airflow.models import DagRun, TaskInstance
from airflow.utils.session import create_session
from pendulum import now
from providers import provider_dag_factory

from tests.conftest import mark_extended


DAG_ID = "test_provider_dag_factory"


def _clean_dag_from_db():
    with create_session() as session:
        session.query(DagRun).filter(DagRun.dag_id == DAG_ID).delete()
        session.query(TaskInstance).filter(TaskInstance.dag_id == DAG_ID).delete()


@pytest.fixture()
def clean_db():
    _clean_dag_from_db()
    yield
    _clean_dag_from_db()


def _generate_tsv_mock(ingestion_callable, media_types, ti, **kwargs):
    for media_type in media_types:
        ti.xcom_push(
            key=f"{media_type}_tsv", value=f"/tmp/{media_type}_does_not_exist.tsv"
        )


@mark_extended
@pytest.mark.parametrize(
    "side_effect",
    [
        # Simple "pull_data" function, no issues raised
        lambda **x: None,
        # Simulated pull_data function skips
        AirflowSkipException("Sample Skip"),
        # Simulated pull_data function raises an exception
        pytest.param(
            ValueError("Oops, something went wrong in ingestion"),
            marks=pytest.mark.raises(exception=BackfillUnfinished),
        ),
    ],
)
def test_skipped_pull_data_runs_successfully(side_effect, clean_db):
    with mock.patch(
        "providers.provider_dag_factory.generate_tsv_filenames"
    ) as generate_filenames_mock, mock.patch(
        "providers.provider_dag_factory.pull_media_wrapper"
    ) as pull_media_mock:
        generate_filenames_mock.side_effect = _generate_tsv_mock
        pull_media_mock.side_effect = side_effect
        dag = provider_dag_factory.create_provider_api_workflow(
            dag_id=DAG_ID,
            ingestion_callable=None,
            default_args={"retries": 0, "on_failure_callback": None},
            schedule_string="@once",
            dated=False,
        )
        dag.run(start_date=now(), executor=DebugExecutor())


def test_create_day_partitioned_ingestion_dag_with_single_layer_dependencies():
    dag = provider_dag_factory.create_day_partitioned_ingestion_dag(
        "test_dag",
        print,
        [[1, 2]],
    )
    today_id = "ingest_0"
    wait0_id = "wait_L0"
    ingest1_id = "ingest_1"
    ingest2_id = "ingest_2"
    today_task = dag.get_task(today_id)
    assert today_task.upstream_task_ids == set()
    assert today_task.downstream_task_ids == {wait0_id}
    ingest1_task = dag.get_task(ingest1_id)
    assert ingest1_task.upstream_task_ids == {wait0_id}
    ingest2_task = dag.get_task(ingest2_id)
    assert ingest2_task.upstream_task_ids == {wait0_id}


def test_create_day_partitioned_ingestion_dag_with_multi_layer_dependencies():
    dag = provider_dag_factory.create_day_partitioned_ingestion_dag(
        "test_dag",
        print,
        [[1, 2], [3, 4, 5]],
    )
    today_id = "ingest_0"
    wait0_id = "wait_L0"
    ingest1_id = "ingest_1"
    ingest2_id = "ingest_2"
    wait1_id = "wait_L1"
    ingest3_id = "ingest_3"
    ingest4_id = "ingest_4"
    ingest5_id = "ingest_5"
    today_task = dag.get_task(today_id)
    assert today_task.upstream_task_ids == set()
    ingest1_task = dag.get_task(ingest1_id)
    assert ingest1_task.upstream_task_ids == {wait0_id}
    ingest2_task = dag.get_task(ingest2_id)
    assert ingest2_task.upstream_task_ids == {wait0_id}
    ingest3_task = dag.get_task(ingest3_id)
    assert ingest3_task.upstream_task_ids == {wait1_id}
    ingest4_task = dag.get_task(ingest4_id)
    assert ingest4_task.upstream_task_ids == {wait1_id}
    ingest5_task = dag.get_task(ingest5_id)
    assert ingest5_task.upstream_task_ids == {wait1_id}

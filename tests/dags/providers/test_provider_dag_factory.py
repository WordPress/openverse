from unittest import mock

import pytest
from airflow.exceptions import AirflowSkipException, BackfillUnfinished
from airflow.executors.debug_executor import DebugExecutor
from airflow.models import DagRun, TaskInstance
from airflow.utils.session import create_session
from pendulum import now
from providers import provider_dag_factory
from providers.provider_reingestion_workflows import ProviderReingestionWorkflow
from providers.provider_workflows import ProviderWorkflow

from tests.conftest import mark_extended
from tests.dags.providers.provider_api_scripts.resources.provider_data_ingester.mock_provider_data_ingester import (
    MockAudioOnlyProviderDataIngester,
    MockImageOnlyProviderDataIngester,
    MockProviderDataIngester,
)


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
        "tests.dags.providers.provider_api_scripts.resources.provider_data_ingester.mock_provider_data_ingester.MockProviderDataIngester.ingest_records"
    ) as ingest_records_mock:
        ingest_records_mock.side_effect = side_effect
        dag = provider_dag_factory.create_provider_api_workflow_dag(
            ProviderWorkflow(
                ingester_class=MockProviderDataIngester,
                default_args={"retries": 0, "on_failure_callback": None},
                schedule_string="@once",
            )
        )
        # Pendulum must be used here in order for Airflow to run this successfully
        dag.run(start_date=now(), executor=DebugExecutor())


def test_create_day_partitioned_ingestion_dag_with_single_layer_dependencies():
    dag = provider_dag_factory.create_day_partitioned_reingestion_dag(
        ProviderReingestionWorkflow(
            ingester_class=MockImageOnlyProviderDataIngester,
        ),
        [[1, 2]],
    )
    # First task in the ingestion step for today
    today_pull_data_id = "ingest_data.pull_image_data"
    # Last task in the ingestion step for today
    today_drop_table_id = "ingest_data.load_image_data.drop_loading_table"
    gather0_id = "gather_partition_0"
    ingest1_id = "ingest_data_day_shift_1.pull_image_data_day_shift_1"
    ingest2_id = "ingest_data_day_shift_2.pull_image_data_day_shift_2"
    today_pull_task = dag.get_task(today_pull_data_id)
    assert today_pull_task.upstream_task_ids == set()
    gather_task = dag.get_task(gather0_id)
    assert gather_task.upstream_task_ids == {today_drop_table_id}
    ingest1_task = dag.get_task(ingest1_id)
    assert ingest1_task.upstream_task_ids == {gather0_id}
    ingest2_task = dag.get_task(ingest2_id)
    assert ingest2_task.upstream_task_ids == {gather0_id}


def test_create_day_partitioned_ingestion_dag_with_multi_layer_dependencies():
    dag = provider_dag_factory.create_day_partitioned_reingestion_dag(
        ProviderReingestionWorkflow(
            ingester_class=MockAudioOnlyProviderDataIngester,
        ),
        [[1, 2], [3, 4, 5]],
    )
    today_id = "ingest_data.pull_audio_data"
    gather0_id = "gather_partition_0"
    ingest1_id = "ingest_data_day_shift_1.pull_audio_data_day_shift_1"
    ingest2_id = "ingest_data_day_shift_2.pull_audio_data_day_shift_2"
    gather1_id = "gather_partition_1"
    ingest3_id = "ingest_data_day_shift_3.pull_audio_data_day_shift_3"
    ingest4_id = "ingest_data_day_shift_4.pull_audio_data_day_shift_4"
    ingest5_id = "ingest_data_day_shift_5.pull_audio_data_day_shift_5"
    today_task = dag.get_task(today_id)
    assert today_task.upstream_task_ids == set()
    ingest1_task = dag.get_task(ingest1_id)
    assert ingest1_task.upstream_task_ids == {gather0_id}
    ingest2_task = dag.get_task(ingest2_id)
    assert ingest2_task.upstream_task_ids == {gather0_id}
    ingest3_task = dag.get_task(ingest3_id)
    assert ingest3_task.upstream_task_ids == {gather1_id}
    ingest4_task = dag.get_task(ingest4_id)
    assert ingest4_task.upstream_task_ids == {gather1_id}
    ingest5_task = dag.get_task(ingest5_id)
    assert ingest5_task.upstream_task_ids == {gather1_id}

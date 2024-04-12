from datetime import datetime, timedelta
from unittest import mock

import pytest
from airflow import DAG
from airflow.exceptions import AirflowSkipException, BackfillUnfinished
from airflow.executors.debug_executor import DebugExecutor
from airflow.operators.empty import EmptyOperator
from pendulum import now
from tests.conftest import mark_extended
from tests.dags.providers.provider_api_scripts.resources.provider_data_ingester.mock_provider_data_ingester import (
    MockAudioOnlyProviderDataIngester,
    MockImageOnlyProviderDataIngester,
    MockProviderDataIngester,
)

from providers import provider_dag_factory
from providers.provider_reingestion_workflows import ProviderReingestionWorkflow
from providers.provider_workflows import ProviderWorkflow


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


@pytest.mark.parametrize(
    "catchup_var, dated, expected_result",
    [
        (True, True, True),
        (False, True, False),
        # Always False if Dag is not dated
        (True, False, False),
        (False, False, False),
    ],
)
def test_catchup_configuration(catchup_var, dated, expected_result):
    with mock.patch("providers.provider_dag_factory.Variable") as MockVariable:
        MockVariable.get.side_effect = [
            catchup_var,
        ]
        dag = provider_dag_factory.create_provider_api_workflow_dag(
            ProviderWorkflow(ingester_class=MockProviderDataIngester, dated=dated)
        )
        assert dag.catchup == expected_result


def test_apply_configuration_overrides():
    # Create a mock DAG
    dag = DAG(
        dag_id="test_dag",
        start_date=datetime(1970, 1, 1),
        default_args={"execution_timeout": timedelta(hours=1)},
    )
    with dag:
        task_with_no_overrides_and_default = EmptyOperator(
            task_id="task_with_no_overrides_and_default"
        )
        task_with_no_overrides = EmptyOperator(
            task_id="task_with_no_overrides", execution_timeout=timedelta(hours=2)
        )
        task_with_override_but_no_timeout = EmptyOperator(
            task_id="task_with_override_but_no_timeout",
            execution_timeout=timedelta(hours=2),
        )
        task_with_override_but_improper_timeout = EmptyOperator(
            task_id="task_with_override_but_improper_timeout",
            execution_timeout=timedelta(hours=2),
        )
        task_with_override = EmptyOperator(
            task_id="task_with_proper_override", execution_timeout=timedelta(hours=2)
        )
        mapped_task_with_override = EmptyOperator.partial(
            task_id="mapped_task_with_override",
        ).expand_kwargs([{"foo": 1}, {"foo": 2}])

    overrides = [
        {"task_id_pattern": "task_with_override_but_no_timeout", "timeout": None},
        {
            "task_id_pattern": "task_with_override_but_improper_timeout",
            "timeout": "foo",  # Improperly formatted timeout should not be applied
        },
        {"task_id_pattern": "task_with_proper_override", "timeout": "1d:0h:0m:0s"},
        {"task_id_pattern": "mapped_task_with_override", "timeout": "4m:0s"},
        {"task_id_pattern": "some_task_that_does_not_exist", "timeout": "1d:2h:3m:4s"},
    ]

    # Apply the overrides to the DAG
    provider_dag_factory._apply_configuration_overrides(dag, overrides)

    # Assert that the overrides were applied
    assert task_with_no_overrides_and_default.execution_timeout == timedelta(hours=1)
    assert task_with_no_overrides.execution_timeout == timedelta(hours=2)
    assert task_with_override_but_no_timeout.execution_timeout == timedelta(hours=2)
    assert task_with_override_but_improper_timeout.execution_timeout == timedelta(
        hours=2
    )
    assert task_with_override.execution_timeout == timedelta(days=1)
    assert mapped_task_with_override.execution_timeout == timedelta(minutes=4)


@pytest.mark.parametrize(
    "task_id, expected_overrides",
    [
        # Fully match the task id
        ("task_baz", {"task_id_pattern": "task_baz", "timeout": "3:3:3:3"}),
        # Partial match
        (
            "task_bar_plus_suffix",
            {"task_id_pattern": "task_bar", "timeout": "2:2:2:2"},
        ),
        # Partial match for a task that is part of a TaskGroup
        (
            "task_group_id.task_foo_plus_suffix",
            {"task_id_pattern": "task_foo", "timeout": "1:1:1:1"},
        ),
        # No match
        ("task_oops", None),
    ],
)
def test_get_overrides_for_task(task_id, expected_overrides):
    overrides = [
        {"task_id_pattern": "task_foo", "timeout": "1:1:1:1"},
        {"task_id_pattern": "task_bar", "timeout": "2:2:2:2"},
        {"task_id_pattern": "task_baz", "timeout": "3:3:3:3"},
    ]

    actual_task_overrides = provider_dag_factory._get_overrides_for_task(
        task_id, overrides
    )
    assert actual_task_overrides == expected_overrides

def test_create_report_load_completion_for_reingestion_dag():
    dag_id = "test_provider_reingestion_workflow"
    media_types = ["image"]
    ingestion_metrics = {
        "duration": "1:00:00",
        "record_counts_by_media_type": {"image": 100},
    }
    dated = False

    with mock.patch("providers.provider_dag_factory.reporting.report_completion") as mock_report_completion:
        report_task = provider_dag_factory.create_report_load_completion(
            dag_id, media_types, ingestion_metrics, dated
        )

        assert report_task.task_id == "report_load_completion"
        assert report_task.python_callable == mock_report_completion

        op_kwargs = report_task.op_kwargs
        assert op_kwargs["dag_id"] == dag_id
        assert op_kwargs["media_types"] == media_types
        assert op_kwargs["duration"] == ingestion_metrics["duration"]
        assert op_kwargs["record_counts_by_media_type"] == ingestion_metrics["record_counts_by_media_type"]
        assert op_kwargs["dated"] == dated
        assert op_kwargs["is_reingestion_workflow"] == True

        assert "date_range_start" not in op_kwargs
        assert "date_range_end" not in op_kwargs

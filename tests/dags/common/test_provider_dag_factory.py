from unittest import mock

import pytest
import requests
from airflow.models import TaskInstance
from common import provider_dag_factory

from tests.dags.common.test_resources import fake_provider_module


@pytest.mark.parametrize(
    "func, media_types, stores",
    [
        # Happy path
        (fake_provider_module.main, ["image"], [fake_provider_module.image_store]),
        # Empty case, no media types provided
        (fake_provider_module.main, [], []),
        # Provided function doesn't have a store at the module level
        pytest.param(
            requests.get,
            ["image"],
            [None],
            marks=pytest.mark.raises(
                exception=ValueError, match="Expected stores in .*? were missing.*"
            ),
        ),
        # Provided function doesn't have all specified stores
        pytest.param(
            fake_provider_module.main,
            ["image", "other"],
            [None, None],
            marks=pytest.mark.raises(
                exception=ValueError, match="Expected stores in .*? were missing.*"
            ),
        ),
    ],
)
def test_push_output_paths_wrapper(func, media_types, stores):
    ti_mock = mock.MagicMock(spec=TaskInstance)
    # This mock, along with the value, get handed into the provided function.
    # For fake_provider_module.main, the mock will be called with the provided value.
    func_mock = mock.MagicMock()
    value = 42
    provider_dag_factory._push_output_paths_wrapper(
        func,
        media_types,
        ti_mock,
        args=[func_mock, value],
    )
    # There should be one call to xcom_push for each provided store, plus
    # one final call to report the task duration.
    expected_xcoms = len(media_types) + 1
    actual_xcoms = ti_mock.xcom_push.call_count
    assert (
        actual_xcoms == expected_xcoms
    ), f"Expected {expected_xcoms} XComs but {actual_xcoms} pushed"
    for args, store in zip(ti_mock.xcom_push.mock_calls[:-1], stores):
        assert args.kwargs["value"] == store.output_path
    # Check that the duration was reported
    assert ti_mock.xcom_push.mock_calls[-1].kwargs["key"] == "duration"

    # Check that the function itself was called with the provided args
    func_mock.assert_called_once_with(value)


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

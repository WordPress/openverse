from unittest import mock

import pytest
from airflow.exceptions import AirflowException
from airflow.sdk.exceptions import AirflowRuntimeError

from common import dag_state


TASK_ID = "wait_task"


@pytest.fixture
def ti():
    ti = mock.MagicMock()
    with mock.patch.object(dag_state, "_task_sdk_ti", return_value=ti):
        yield ti


def test_assert_dag_exists(ti):
    dag_state.assert_dag_exists("some_dag")
    ti.get_dag.assert_called_once_with("some_dag")


def test_assert_dag_exists_fails_for_missing_dag(ti):
    ti.get_dag.side_effect = AirflowRuntimeError(mock.MagicMock())

    with pytest.raises(AirflowException, match="does not exist"):
        dag_state.assert_dag_exists("missing_dag")


def test_count_active_dag_runs(ti):
    ti.get_dr_count.return_value = 2

    assert dag_state.count_active_dag_runs("some_dag") == 2
    ti.get_dr_count.assert_called_once_with(
        dag_id="some_dag", states=["queued", "running"]
    )


def test_count_running_dag_runs_past_task_skips_idle_dags(ti):
    ti.get_dr_count.return_value = 0

    assert dag_state.count_running_dag_runs_past_task("some_dag", TASK_ID) == 0
    ti.get_task_states.assert_not_called()


def test_count_running_dag_runs_past_task_without_succeeded_tasks(ti):
    ti.get_dr_count.return_value = 1
    ti.get_task_states.return_value = {"run_1": {TASK_ID: "running"}}

    assert dag_state.count_running_dag_runs_past_task("some_dag", TASK_ID) == 0
    ti.get_dr_count.assert_called_once_with(dag_id="some_dag", states=["running"])


def test_count_running_dag_runs_past_task(ti):
    succeeded_run_ids = [f"run_{i}" for i in range(dag_state.RUN_ID_BATCH_SIZE + 1)]
    ti.get_task_states.return_value = {
        **{run_id: {TASK_ID: "success"} for run_id in succeeded_run_ids},
        "running_task": {TASK_ID: "running"},
        "other_task": {"other": "success"},
    }
    # One running DAG run, then one per batch of succeeded run ids
    ti.get_dr_count.side_effect = [1, 1, 0]

    assert dag_state.count_running_dag_runs_past_task("some_dag", TASK_ID) == 1
    ti.get_task_states.assert_called_once_with(dag_id="some_dag", task_ids=[TASK_ID])
    assert ti.get_dr_count.call_args_list == [
        mock.call(dag_id="some_dag", states=["running"]),
        mock.call(
            dag_id="some_dag",
            run_ids=succeeded_run_ids[: dag_state.RUN_ID_BATCH_SIZE],
            states=["running"],
        ),
        mock.call(
            dag_id="some_dag",
            run_ids=succeeded_run_ids[dag_state.RUN_ID_BATCH_SIZE :],
            states=["running"],
        ),
    ]


def test_get_task_states(ti):
    dag_run = mock.MagicMock(dag_id="some_dag", run_id="some_run")
    ti.get_task_states.return_value = {"some_run": {TASK_ID: "failed"}}

    assert dag_state.get_task_states(dag_run) == {TASK_ID: "failed"}
    ti.get_task_states.assert_called_once_with(dag_id="some_dag", run_ids=["some_run"])


def test_get_task_states_without_task_instances(ti):
    ti.get_task_states.return_value = {}

    assert dag_state.get_task_states(mock.MagicMock(run_id="some_run")) == {}


@pytest.mark.parametrize(
    "base_url, expected_base",
    [
        pytest.param("https://airflow.test/", "https://airflow.test", id="configured"),
        pytest.param(None, dag_state.DEFAULT_BASE_URL, id="unset"),
    ],
)
def test_ui_urls(base_url, expected_base):
    run_id = "manual__2022-01-01T00:00:00"
    run_url = f"{expected_base}/dags/some_dag/runs/manual__2022-01-01T00%3A00%3A00"

    with mock.patch.object(dag_state.conf, "get", return_value=base_url) as get:
        assert dag_state.dag_run_url("some_dag", run_id) == run_url
        assert (
            dag_state.task_log_url("some_dag", run_id, "group.task")
            == f"{run_url}/tasks/group.task"
        )

    get.assert_called_with("api", "base_url", fallback=None)

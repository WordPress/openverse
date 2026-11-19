from unittest import mock

import pytest
from airflow.exceptions import AirflowException
from airflow.sdk.exceptions import AirflowRuntimeError

from common import dag_state
from common.sensors.single_run_external_dags_sensor import SingleRunExternalDAGsSensor


TEST_TASK_ID = "wait_task"
EXTERNAL_DAG_IDS = ["success_dag", "running_dag"]


class FakeTaskInstance:
    """
    Answers the Task SDK calls in `common.dag_state` from a list of DAG runs, given as
    `(dag_id, run_id, run_state, wait_task_state)` rows.
    """

    def __init__(self, runs, dag_ids=EXTERNAL_DAG_IDS):
        self.runs = runs
        self.dag_ids = set(dag_ids)

    def get_dag(self, dag_id):
        if dag_id not in self.dag_ids:
            raise AirflowRuntimeError(mock.MagicMock())

    def get_dr_count(self, dag_id, run_ids=None, states=None):
        return sum(
            1
            for run_dag_id, run_id, run_state, _ in self.runs
            if run_dag_id == dag_id
            and (run_ids is None or run_id in run_ids)
            and (states is None or run_state in states)
        )

    def get_task_states(self, dag_id, task_ids):
        return {
            run_id: {TEST_TASK_ID: task_state}
            for run_dag_id, run_id, _, task_state in self.runs
            if run_dag_id == dag_id
        }


@pytest.fixture
def set_runs():
    with mock.patch.object(dag_state, "_task_sdk_ti") as task_sdk_ti:

        def set_runs(runs, **kwargs):
            ti = FakeTaskInstance(runs, **kwargs)
            task_sdk_ti.return_value = ti
            return ti

        yield set_runs


def _sensor(external_dag_ids=EXTERNAL_DAG_IDS, **kwargs):
    return SingleRunExternalDAGsSensor(
        task_id=TEST_TASK_ID,
        external_dag_ids=external_dag_ids,
        poke_interval=5,
        mode="reschedule",
        **kwargs,
    )


@pytest.mark.parametrize(
    "runs",
    [
        pytest.param([], id="no-runs"),
        pytest.param(
            [
                ("success_dag", "run_1", "success", "success"),
                ("running_dag", "run_1", "failed", "success"),
            ],
            id="finished-runs",
        ),
        pytest.param(
            [("running_dag", "run_1", "running", "up_for_reschedule")],
            id="running-dag-still-waiting",
        ),
    ],
)
def test_succeeds_if_no_running_dags(runs, set_runs):
    set_runs(runs)

    assert _sensor().poke(context={}) is True


def test_retries_if_running_dags_with_completed_sensor_task(set_runs):
    set_runs([("running_dag", "run_1", "running", "success")])

    assert _sensor().poke(context={}) is False


def test_passes_with_allow_concurrent_runs(set_runs):
    set_runs([("running_dag", "run_1", "running", "success")])

    assert _sensor(allow_concurrent_runs=True).poke(context={}) is True


def test_check_existence_runs_on_every_poke(set_runs):
    ti = set_runs([], dag_ids=["dag_a", "dag_b"])
    sensor = _sensor(["dag_a", "dag_b"], check_existence=True)
    assert sensor.poke(context={}) is True

    ti.dag_ids.remove("dag_b")

    with pytest.raises(AirflowException, match="dag_b does not exist"):
        sensor.poke(context={})

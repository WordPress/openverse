from unittest import mock

import pytest
from airflow.exceptions import AirflowException

from common.sensors.single_run_external_dags_sensor import SingleRunExternalDAGsSensor


TEST_TASK_ID = "wait_task"
EXTERNAL_DAG_IDS = ["success_dag", "running_dag"]


def _sensor(allow_concurrent_runs=False):
    sensor = SingleRunExternalDAGsSensor(
        task_id=TEST_TASK_ID,
        external_dag_ids=EXTERNAL_DAG_IDS,
        allow_concurrent_runs=allow_concurrent_runs,
        poke_interval=5,
        mode="reschedule",
    )
    # Operators log through structlog, which caplog does not capture
    sensor._log = sensor._cached_logger = mock.MagicMock()
    return sensor


def _logged(sensor) -> str:
    return "\n".join(
        call.args[0] % call.args[1:] for call in sensor.log.info.call_args_list
    )


@pytest.fixture
def running_counts():
    counts = {}
    with mock.patch(
        "common.sensors.single_run_external_dags_sensor.count_running_dag_runs_past_task",
        side_effect=lambda dag_id, task_id: counts.get((dag_id, task_id), 0),
    ) as count:
        yield counts, count


def test_succeeds_if_no_running_dags(running_counts):
    _, count = running_counts
    sensor = _sensor()

    assert sensor.poke(context={}) is True

    assert count.call_args_list == [
        mock.call(dag_id, TEST_TASK_ID) for dag_id in EXTERNAL_DAG_IDS
    ]
    assert f"Poking for DAGs {EXTERNAL_DAG_IDS} ..." in _logged(sensor)
    assert "None of the DAGs are in the running state" in _logged(sensor)


def test_retries_if_running_dags_with_completed_sensor_task(running_counts):
    counts, _ = running_counts
    counts[("running_dag", TEST_TASK_ID)] = 1
    sensor = _sensor()

    assert sensor.poke(context={}) is False

    assert "DAG running_dag is in the running state" in _logged(sensor)


def test_passes_with_allow_concurrent_runs(running_counts):
    counts, count = running_counts
    counts[("running_dag", TEST_TASK_ID)] = 1
    sensor = _sensor(allow_concurrent_runs=True)

    assert sensor.poke(context={}) is True

    count.assert_not_called()
    assert f"Poking for DAGs {EXTERNAL_DAG_IDS} ..." in _logged(sensor)
    assert (
        "`allow_concurrent_runs` is enabled. Returning without checking for"
        " running DAGs." in _logged(sensor)
    )


def _existence_sensor(external_dag_ids):
    return SingleRunExternalDAGsSensor(
        task_id=TEST_TASK_ID,
        external_dag_ids=external_dag_ids,
        check_existence=True,
        poke_interval=5,
        mode="reschedule",
    )


@pytest.mark.usefixtures("running_counts")
def test_check_existence_checks_each_external_dag_on_every_poke():
    sensor = _existence_sensor(["dag_a", "dag_b"])
    with mock.patch(
        "common.sensors.single_run_external_dags_sensor.assert_dag_exists"
    ) as assert_dag_exists:
        assert sensor.poke(context={}) is True
        assert sensor.poke(context={}) is True

    assert assert_dag_exists.call_args_list == [
        mock.call("dag_a"),
        mock.call("dag_b"),
        mock.call("dag_a"),
        mock.call("dag_b"),
    ]


@pytest.mark.usefixtures("running_counts")
def test_check_existence_fails_for_missing_dag():
    sensor = _existence_sensor(["nonexistent_dag_id"])
    with mock.patch(
        "common.sensors.single_run_external_dags_sensor.assert_dag_exists",
        side_effect=AirflowException(
            "The external DAG nonexistent_dag_id does not exist."
        ),
    ):
        with pytest.raises(AirflowException, match="does not exist"):
            sensor.poke(context={})

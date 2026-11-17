from datetime import timedelta
from unittest import mock

import pytest
from airflow.models.dag import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.utils.state import DagRunState, TaskInstanceState
from airflow.utils.timezone import datetime
from airflow.utils.types import DagRunType

from common import dag_state


DEFAULT_DATE = datetime(2022, 1, 1)
TASK_ID = "wait_task"


@pytest.fixture
def airflow_3_ti():
    ti = mock.MagicMock()
    with (
        mock.patch.object(dag_state, "IS_AIRFLOW_3", True),
        mock.patch.object(dag_state, "_task_sdk_ti", return_value=ti),
    ):
        yield ti


@pytest.fixture
def airflow_2():
    with mock.patch.object(dag_state, "IS_AIRFLOW_3", False):
        yield


def _create_dag_run(dag_id, state, run_number=0, task_state=None):
    with DAG(dag_id, schedule=None, start_date=DEFAULT_DATE) as dag:
        EmptyOperator(task_id=TASK_ID)
    logical_date = DEFAULT_DATE + timedelta(days=run_number)
    dag_run = dag.create_dagrun(
        run_id=f"{dag_id}_{run_number}",
        start_date=logical_date,
        execution_date=logical_date,
        data_interval=(logical_date, logical_date),
        state=state,
        run_type=DagRunType.MANUAL,
    )
    if task_state:
        ti = dag_run.get_task_instance(TASK_ID)
        ti.set_state(task_state)
    return dag_run


@pytest.mark.usefixtures("airflow_2", "clean_db")
@pytest.mark.parametrize(
    "states, expected",
    [
        pytest.param([], 0, id="no-runs"),
        pytest.param([DagRunState.SUCCESS, DagRunState.FAILED], 0, id="finished"),
        pytest.param([DagRunState.SUCCESS, DagRunState.RUNNING], 1, id="running"),
        pytest.param([DagRunState.QUEUED, DagRunState.RUNNING], 2, id="queued"),
    ],
)
def test_count_active_dag_runs_on_airflow_2(sample_dag_id_fixture, states, expected):
    for run_number, state in enumerate(states):
        _create_dag_run(sample_dag_id_fixture, state, run_number)

    assert dag_state.count_active_dag_runs(sample_dag_id_fixture) == expected


def test_count_active_dag_runs_on_airflow_3(airflow_3_ti):
    airflow_3_ti.get_dr_count.return_value = 2

    assert dag_state.count_active_dag_runs("some_dag") == 2
    airflow_3_ti.get_dr_count.assert_called_once_with(
        dag_id="some_dag", states=["queued", "running"]
    )


@pytest.mark.usefixtures("airflow_2", "clean_db")
@pytest.mark.parametrize(
    "runs, expected",
    [
        pytest.param([], 0, id="no-runs"),
        pytest.param([(DagRunState.RUNNING, None)], 0, id="task-not-started"),
        pytest.param(
            [(DagRunState.RUNNING, TaskInstanceState.RUNNING)], 0, id="task-running"
        ),
        pytest.param(
            [(DagRunState.SUCCESS, TaskInstanceState.SUCCESS)], 0, id="run-finished"
        ),
        pytest.param(
            [
                (DagRunState.RUNNING, TaskInstanceState.SUCCESS),
                (DagRunState.SUCCESS, TaskInstanceState.SUCCESS),
            ],
            1,
            id="task-succeeded-in-running-run",
        ),
    ],
)
def test_count_running_dag_runs_past_task_on_airflow_2(
    sample_dag_id_fixture, runs, expected
):
    for run_number, (state, task_state) in enumerate(runs):
        _create_dag_run(sample_dag_id_fixture, state, run_number, task_state)

    assert (
        dag_state.count_running_dag_runs_past_task(sample_dag_id_fixture, TASK_ID)
        == expected
    )


def test_count_running_dag_runs_past_task_on_airflow_3_skips_idle_dags(airflow_3_ti):
    airflow_3_ti.get_dr_count.return_value = 0

    assert dag_state.count_running_dag_runs_past_task("some_dag", TASK_ID) == 0
    airflow_3_ti.get_task_states.assert_not_called()


def test_count_running_dag_runs_past_task_on_airflow_3(airflow_3_ti):
    succeeded_run_ids = [f"run_{i}" for i in range(dag_state.RUN_ID_BATCH_SIZE + 1)]
    airflow_3_ti.get_task_states.return_value = {
        **{run_id: {TASK_ID: "success"} for run_id in succeeded_run_ids},
        "running_task": {TASK_ID: "running"},
        "other_task": {"other": "success"},
    }
    # One running DAG run, then one per batch of succeeded run ids
    airflow_3_ti.get_dr_count.side_effect = [1, 1, 0]

    assert dag_state.count_running_dag_runs_past_task("some_dag", TASK_ID) == 1
    airflow_3_ti.get_task_states.assert_called_once_with(
        dag_id="some_dag", task_ids=[TASK_ID]
    )
    assert airflow_3_ti.get_dr_count.call_args_list == [
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


@pytest.mark.usefixtures("airflow_2", "clean_db")
def test_get_task_states_on_airflow_2(sample_dag_id_fixture):
    dag_run = _create_dag_run(
        sample_dag_id_fixture, DagRunState.RUNNING, task_state=TaskInstanceState.FAILED
    )

    assert dag_state.get_task_states(dag_run) == {TASK_ID: "failed"}


def test_get_task_states_on_airflow_3(airflow_3_ti):
    dag_run = mock.MagicMock(dag_id="some_dag", run_id="some_run")
    airflow_3_ti.get_task_states.return_value = {"some_run": {TASK_ID: "failed"}}

    assert dag_state.get_task_states(dag_run) == {TASK_ID: "failed"}
    airflow_3_ti.get_task_states.assert_called_once_with(
        dag_id="some_dag", run_ids=["some_run"]
    )


@pytest.mark.parametrize(
    "is_airflow_3, section, expected_run_url, expected_log_url",
    [
        pytest.param(
            False,
            "webserver",
            "https://airflow.test/dags/some_dag/grid?dag_run_id=manual__2022-01-01T00%3A00%3A00",
            "https://airflow.test/dags/some_dag/grid?dag_run_id=manual__2022-01-01T00%3A00%3A00"
            "&task_id=group.task&tab=logs",
            id="airflow-2",
        ),
        pytest.param(
            True,
            "api",
            "https://airflow.test/dags/some_dag/runs/manual__2022-01-01T00%3A00%3A00",
            "https://airflow.test/dags/some_dag/runs/manual__2022-01-01T00%3A00%3A00"
            "/tasks/group.task",
            id="airflow-3",
        ),
    ],
)
def test_ui_urls(is_airflow_3, section, expected_run_url, expected_log_url):
    run_id = "manual__2022-01-01T00:00:00"

    def get_conf(conf_section, key):
        assert (conf_section, key) == (section, "base_url")
        return "https://airflow.test/"

    with (
        mock.patch.object(dag_state, "IS_AIRFLOW_3", is_airflow_3),
        mock.patch.object(dag_state.conf, "get", side_effect=get_conf),
    ):
        assert dag_state.dag_run_url("some_dag", run_id) == expected_run_url
        assert (
            dag_state.task_log_url("some_dag", run_id, "group.task") == expected_log_url
        )

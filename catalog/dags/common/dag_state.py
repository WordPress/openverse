"""
Read DAG run and task instance states from inside a running task.

Tasks cannot query the metadata database, so these functions ask the API server
through the Task SDK methods on the running task instance.
"""

from urllib.parse import quote

from airflow.configuration import conf
from airflow.exceptions import AirflowException
from airflow.sdk import get_current_context
from airflow.sdk.exceptions import AirflowRuntimeError
from airflow.utils.state import DagRunState, TaskInstanceState


ACTIVE_DAG_RUN_STATES = [DagRunState.QUEUED.value, DagRunState.RUNNING.value]

# Run ids are sent to the API server as query parameters, so look them up in
# batches to keep the request URL short
RUN_ID_BATCH_SIZE = 20

# Used when `[api] base_url` is not set: the API server's default local address
DEFAULT_BASE_URL = "http://localhost:8080"


def _task_sdk_ti():
    return get_current_context()["ti"]


def assert_dag_exists(dag_id: str) -> None:
    """Raise an `AirflowException` if no DAG with `dag_id` is deployed."""
    try:
        _task_sdk_ti().get_dag(dag_id)
    except AirflowRuntimeError as error:
        raise AirflowException(f"The external DAG {dag_id} does not exist.") from error


def count_active_dag_runs(dag_id: str) -> int:
    """Return the number of queued or running DAG runs for `dag_id`."""
    return _task_sdk_ti().get_dr_count(dag_id=dag_id, states=ACTIVE_DAG_RUN_STATES)


def count_running_dag_runs_past_task(dag_id: str, task_id: str) -> int:
    """
    Return the number of running DAG runs for `dag_id` in which the task `task_id`
    has already succeeded.
    """
    running = DagRunState.RUNNING.value
    ti = _task_sdk_ti()
    if not ti.get_dr_count(dag_id=dag_id, states=[running]):
        return 0

    task_states = ti.get_task_states(dag_id=dag_id, task_ids=[task_id])
    succeeded_run_ids = [
        run_id
        for run_id, states in task_states.items()
        if states.get(task_id) == TaskInstanceState.SUCCESS.value
    ]
    return sum(
        ti.get_dr_count(
            dag_id=dag_id,
            run_ids=succeeded_run_ids[i : i + RUN_ID_BATCH_SIZE],
            states=[running],
        )
        for i in range(0, len(succeeded_run_ids), RUN_ID_BATCH_SIZE)
    )


def get_task_states(dag_run) -> dict[str, str | None]:
    """
    Return the state of each task instance in `dag_run`, keyed by task id. Mapped
    task instances are keyed by `<task_id>_<map_index>`.
    """
    task_states = _task_sdk_ti().get_task_states(
        dag_id=dag_run.dag_id, run_ids=[dag_run.run_id]
    )
    return task_states.get(dag_run.run_id, {})


def _base_url() -> str:
    return (conf.get("api", "base_url", fallback=None) or DEFAULT_BASE_URL).rstrip("/")


def dag_run_url(dag_id: str, run_id: str) -> str:
    """Return the Airflow UI URL of a DAG run."""
    return f"{_base_url()}/dags/{quote(dag_id)}/runs/{quote(run_id)}"


def task_log_url(dag_id: str, run_id: str, task_id: str) -> str:
    """Return the Airflow UI URL of a task instance's logs."""
    return f"{dag_run_url(dag_id, run_id)}/tasks/{quote(task_id)}"

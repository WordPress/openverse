"""
Read DAG run and task instance states from inside a running task.

Airflow 2 tasks can query the metadata database directly. Airflow 3 blocks that,
and tasks ask the API server through the Task SDK methods on the running task
instance instead. Each function here picks the implementation for the installed
Airflow version, so the DAGs behave the same on both. The Airflow 2 branches can
be removed once the catalog runs Airflow 3.
"""

from urllib.parse import quote

from airflow import __version__ as airflow_version
from airflow.configuration import conf
from airflow.exceptions import AirflowException
from airflow.providers.standard.operators.python import get_current_context
from airflow.utils.state import DagRunState, TaskInstanceState
from packaging.version import Version


IS_AIRFLOW_3 = Version(airflow_version).major >= 3

ACTIVE_DAG_RUN_STATES = [DagRunState.QUEUED.value, DagRunState.RUNNING.value]

# Run ids are sent to the API server as query parameters, so look them up in
# batches to keep the request URL short
RUN_ID_BATCH_SIZE = 20


def _task_sdk_ti():
    return get_current_context()["ti"]


def assert_dag_exists(dag_id: str) -> None:
    """Raise an `AirflowException` if no DAG with `dag_id` is deployed."""
    if IS_AIRFLOW_3:
        from airflow.sdk.exceptions import AirflowRuntimeError

        try:
            _task_sdk_ti().get_dag(dag_id)
        except AirflowRuntimeError as error:
            raise AirflowException(
                f"The external DAG {dag_id} does not exist."
            ) from error
        return

    from airflow.models import DagModel
    from airflow.utils.session import create_session

    with create_session() as session:
        if not session.query(DagModel).filter(DagModel.dag_id == dag_id).first():
            raise AirflowException(f"The external DAG {dag_id} does not exist.")


def count_active_dag_runs(dag_id: str) -> int:
    """Return the number of queued or running DAG runs for `dag_id`."""
    if IS_AIRFLOW_3:
        return _task_sdk_ti().get_dr_count(dag_id=dag_id, states=ACTIVE_DAG_RUN_STATES)

    from airflow.models import DagRun
    from airflow.utils.session import create_session

    with create_session() as session:
        return (
            session.query(DagRun)
            .filter(
                DagRun.dag_id == dag_id,
                DagRun.state.in_(ACTIVE_DAG_RUN_STATES),
            )
            .count()
        )


def count_running_dag_runs_past_task(dag_id: str, task_id: str) -> int:
    """
    Return the number of running DAG runs for `dag_id` in which the task `task_id`
    has already succeeded.
    """
    running = DagRunState.RUNNING.value
    success = TaskInstanceState.SUCCESS.value

    if IS_AIRFLOW_3:
        ti = _task_sdk_ti()
        if not ti.get_dr_count(dag_id=dag_id, states=[running]):
            return 0
        task_states = ti.get_task_states(dag_id=dag_id, task_ids=[task_id])
        succeeded_run_ids = [
            run_id
            for run_id, states in task_states.items()
            if states.get(task_id) == success
        ]
        return sum(
            ti.get_dr_count(
                dag_id=dag_id,
                run_ids=succeeded_run_ids[i : i + RUN_ID_BATCH_SIZE],
                states=[running],
            )
            for i in range(0, len(succeeded_run_ids), RUN_ID_BATCH_SIZE)
        )

    from airflow.models import DagRun, TaskInstance
    from airflow.utils.session import create_session

    with create_session() as session:
        return (
            session.query(DagRun)
            .filter(DagRun.dag_id == dag_id, DagRun.state == running)
            .join(
                TaskInstance,
                (TaskInstance.dag_id == DagRun.dag_id)
                & (TaskInstance.run_id == DagRun.run_id),
            )
            .filter(TaskInstance.task_id == task_id, TaskInstance.state == success)
            .count()
        )


def get_task_states(dag_run) -> dict[str, str | None]:
    """
    Return the state of each task instance in `dag_run`, keyed by task id. Mapped
    task instances are keyed by `<task_id>_<map_index>`.
    """
    if IS_AIRFLOW_3:
        task_states = _task_sdk_ti().get_task_states(
            dag_id=dag_run.dag_id, run_ids=[dag_run.run_id]
        )
        return task_states.get(dag_run.run_id, {})

    return {
        (ti.task_id if ti.map_index < 0 else f"{ti.task_id}_{ti.map_index}"): ti.state
        for ti in dag_run.get_task_instances()
    }


def _base_url() -> str:
    section = "api" if IS_AIRFLOW_3 else "webserver"
    return conf.get(section, "base_url").rstrip("/")


def dag_run_url(dag_id: str, run_id: str) -> str:
    """Return the Airflow UI URL of a DAG run."""
    if IS_AIRFLOW_3:
        return f"{_base_url()}/dags/{quote(dag_id)}/runs/{quote(run_id)}"
    return f"{_base_url()}/dags/{quote(dag_id)}/grid?dag_run_id={quote(run_id)}"


def task_log_url(dag_id: str, run_id: str, task_id: str) -> str:
    """Return the Airflow UI URL of a task instance's logs."""
    if IS_AIRFLOW_3:
        return f"{dag_run_url(dag_id, run_id)}/tasks/{quote(task_id)}"
    return f"{dag_run_url(dag_id, run_id)}&task_id={quote(task_id)}&tab=logs"

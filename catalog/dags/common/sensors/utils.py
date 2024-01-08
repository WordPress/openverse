from datetime import datetime

from airflow.decorators import task, task_group
from airflow.exceptions import AirflowSensorTimeout
from airflow.models import DagRun
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.utils.state import State

from common.constants import REFRESH_POKE_INTERVAL


def get_most_recent_dag_run(dag_id) -> list[datetime] | datetime:
    """
    Retrieve the most recent DAG run's execution date.

    For use as ``execution_date_fn`` argument to ``ExternalTaskSensor``.

    Adapted from https://stackoverflow.com/a/74017474
    CC BY-SA 4.0 by Stack Overflow user Nahid O.
    """
    dag_runs = DagRun.find(dag_id=dag_id)
    dag_runs.sort(key=lambda x: x.execution_date, reverse=True)
    if dag_runs:
        return dag_runs[0].execution_date

    # If there are no DAG runs, return an empty list to indicate that
    # there are no execution dates to check.
    # This works because the sensor waits until the number
    # of runs for the execution dates in the ``allowed_states`` matches the
    # length of the list of execution dates to check. If there are no runs
    # for this DAG, then the only possible number of required states
    # we can have is 0. See ``ExternalTaskSensor::poke`` and
    # ``ExternalTaskSensor::get_count``, especially the handling
    # of ``dttm_filter`` for the relevant implementation details.
    return []


def wait_for_external_dag(external_dag_id: str, task_id: str | None = None):
    """
    Return a Sensor task which will wait if the given external DAG is
    running.

    To fully ensure that the waiting DAG and the external DAG do not run
    concurrently, the external DAG should have a `prevent_concurrency_with_dag`
    task which fails immediately if the waiting DAG is running.

    If the external DAG should _not_ fail when the waiting DAG is running,
    but instead wait its turn, use the SingleRunExternalDagSensor in both
    DAGs to avoid deadlock.
    """
    if not task_id:
        task_id = f"wait_for_{external_dag_id}"

    return ExternalTaskSensor(
        task_id=task_id,
        poke_interval=REFRESH_POKE_INTERVAL,
        external_dag_id=external_dag_id,
        # Wait for the whole DAG, not just a part of it
        external_task_id=None,
        check_existence=False,
        execution_date_fn=lambda _: get_most_recent_dag_run(external_dag_id),
        mode="reschedule",
        # Any "finished" state is sufficient for us to continue
        allowed_states=[State.SUCCESS, State.FAILED],
    )


@task_group(group_id="wait_for_external_dags")
def wait_for_external_dags(external_dag_ids: list[str]):
    """
    Wait for all DAGs with the given external DAG ids to no longer be
    in a running state before continuing.
    """
    for dag_id in external_dag_ids:
        wait_for_external_dag(dag_id)


@task(retries=0)
def prevent_concurrency_with_dag(external_dag_id: str, **context):
    """
    Prevent concurrency with the given external DAG, by failing
    immediately if that DAG is running.
    """

    wait_for_dag = wait_for_external_dag(
        external_dag_id=external_dag_id,
        task_id=f"check_for_running_{external_dag_id}",
    )
    wait_for_dag.timeout = 0
    try:
        wait_for_dag.execute(context)
    except AirflowSensorTimeout:
        raise ValueError(f"Concurrency check with {external_dag_id} failed.")


@task_group(group_id="prevent_concurrency")
def prevent_concurrency_with_dags(external_dag_ids: list[str]):
    """Fail immediately if any of the given external dags are in progress."""
    for dag_id in external_dag_ids:
        prevent_concurrency_with_dag.override(
            task_id=f"prevent_concurrency_with_{dag_id}"
        )(dag_id)

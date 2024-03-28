from datetime import datetime

from airflow.decorators import task, task_group
from airflow.exceptions import AirflowSensorTimeout
from airflow.models import DagModel, DagRun, DagTag
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.utils.session import provide_session
from airflow.utils.state import State

from common.constants import REFRESH_POKE_INTERVAL


THREE_DAYS = 60 * 60 * 24 * 3


def _get_most_recent_dag_run(dag_id) -> list[datetime] | datetime:
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


@task
def get_dags_with_concurrency_tag(
    tag: str, excluded_dag_ids: list[str], session=None, dag=None
):
    """
    Get a list of DAG ids with the given tag. The id of the running DAG is excluded,
    as well as any ids in the `excluded_dag_ids` list.
    """
    dags = session.query(DagModel).filter(DagModel.tags.any(DagTag.name == tag)).all()
    dag_ids = [dag.dag_id for dag in dags]

    running_dag_id = dag.dag_id
    if running_dag_id not in dag_ids:
        raise ValueError(
            f"The `{running_dag_id}` DAG tried preventing concurrency with the `{tag}`,"
            " tag, but does not have the tag itself. To ensure that other DAGs with this"
            f" tag will also avoid running concurrently with `{running_dag_id}`, it must"
            f"have the `{tag}` tag applied."
        )

    # Return just the ids of DAGs to prevent concurrency with. This excludes the running dag id,
    # and any supplied `excluded_dag_ids`
    return [id for id in dag_ids if id not in {*excluded_dag_ids, running_dag_id}]


@task
def wait_for_external_dag(
    external_dag_id: str,
    task_id: str | None = None,
    timeout: int | None = THREE_DAYS,
    **context,
):
    """
    Execute a Sensor task which will wait if the given external DAG is
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

    sensor = ExternalTaskSensor(
        task_id=task_id,
        poke_interval=REFRESH_POKE_INTERVAL,
        external_dag_id=external_dag_id,
        # Wait for the whole DAG, not just a part of it
        external_task_id=None,
        check_existence=False,
        execution_date_fn=lambda _: _get_most_recent_dag_run(external_dag_id),
        mode="reschedule",
        # Any "finished" state is sufficient for us to continue
        allowed_states=[State.SUCCESS, State.FAILED],
        # execution_timeout for the task does not include time that the sensor
        # was up for reschedule but not actually running. `timeout` does
        timeout=timeout,
    )

    sensor.execute(context)


@task_group(group_id="wait_for_external_dags")
@provide_session
def wait_for_external_dags_with_tag(
    tag: str, excluded_dag_ids: list[str] = None, session=None
):
    """
    Wait until all DAGs with the given `tag`, excluding those identified by the
    `excluded_dag_ids`, are no longer in the running state before continuing.
    """
    external_dag_ids = get_dags_with_concurrency_tag.override(
        task_id=f"get_dags_in_{tag}_group"
    )(tag=tag, excluded_dag_ids=excluded_dag_ids or [], session=session)

    wait_for_external_dag.expand(external_dag_id=external_dag_ids)


@task(retries=0)
def prevent_concurrency_with_dag(external_dag_id: str, **context):
    """
    Prevent concurrency with the given external DAG, by failing
    immediately if that DAG is running.
    """
    try:
        wait_for_external_dag.function(
            external_dag_id=external_dag_id,
            task_id=f"check_for_running_{external_dag_id}",
            timeout=0,
            **context,
        )
    except AirflowSensorTimeout:
        raise ValueError(f"Concurrency check with {external_dag_id} failed.")


@task_group(group_id="prevent_concurrency_with_dags")
@provide_session
def prevent_concurrency_with_dags_with_tag(
    tag: str, excluded_dag_ids: list[str] = None, session=None
):
    """
    Prevent concurrency with any DAGs that have the given `tag`, excluding
    those identified by the `excluded_dag_ids`. Concurrency is prevented by
    failing the task immediately if any of the tagged DAGs are in the running
    state.
    """
    external_dag_ids = get_dags_with_concurrency_tag.override(
        task_id=f"get_dags_in_{tag}_group"
    )(tag=tag, excluded_dag_ids=excluded_dag_ids or [], session=session)

    prevent_concurrency_with_dag.expand(external_dag_id=external_dag_ids)


@task(retries=0)
def is_concurrent_with_any(external_dag_ids: list[str], **context):
    """
    Detect whether any of the external DAG are running.

    Returns the ID of the first DAG found to be running. Otherwise,
    returns None.
    """
    for dag_id in external_dag_ids:
        try:
            prevent_concurrency_with_dag.function(dag_id, **context)
        except ValueError:
            return dag_id

    # Explicit return None to clarify expectations
    return None

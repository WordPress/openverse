from airflow.decorators import task, task_group
from airflow.exceptions import AirflowSensorTimeout
from airflow.providers.standard.sensors.python import PythonSensor

from common.constants import REFRESH_POKE_INTERVAL
from common.dag_state import count_active_dag_runs
from common.sensors.constants import CONCURRENCY_TAG_DAG_IDS


THREE_DAYS = 60 * 60 * 24 * 3


@task
def get_dags_with_concurrency_tag(tag: str, excluded_dag_ids: list[str], dag=None):
    """
    Get a list of DAG ids with the given tag. The id of the running DAG is excluded,
    as well as any ids in the `excluded_dag_ids` list.
    """
    dag_ids = CONCURRENCY_TAG_DAG_IDS.get(tag, [])

    running_dag_id = dag.dag_id
    if running_dag_id not in dag_ids:
        raise ValueError(
            f"The `{running_dag_id}` DAG tried preventing concurrency with the `{tag}`,"
            " tag, but does not have the tag itself. To ensure that other DAGs with this"
            f" tag will also avoid running concurrently with `{running_dag_id}`, it must"
            f" have the `{tag}` tag applied and be listed under it in"
            " `CONCURRENCY_TAG_DAG_IDS`."
        )

    # Return just the ids of DAGs to prevent concurrency with. This excludes the running dag id,
    # and any supplied `excluded_dag_ids`
    return [id for id in dag_ids if id not in {*excluded_dag_ids, running_dag_id}]


@task(map_index_template="{{ task.op_kwargs['external_dag_id'] }}")
def wait_for_external_dag(
    external_dag_id: str,
    task_id: str | None = None,
    timeout: int | None = THREE_DAYS,
    **context,
):
    """
    Execute a Sensor task which will wait if the given external DAG is
    queued or running.

    To fully ensure that the waiting DAG and the external DAG do not run
    concurrently, the external DAG should have a `prevent_concurrency_with_dag`
    task which fails immediately if the waiting DAG is running.

    If the external DAG should _not_ fail when the waiting DAG is running,
    but instead wait its turn, use the SingleRunExternalDagSensor in both
    DAGs to avoid deadlock.
    """
    if not task_id:
        task_id = f"wait_for_{external_dag_id}"

    sensor = PythonSensor(
        task_id=task_id,
        poke_interval=REFRESH_POKE_INTERVAL,
        # Wait until no run of the external DAG is queued or running
        python_callable=lambda: count_active_dag_runs(external_dag_id) == 0,
        mode="reschedule",
        # execution_timeout for the task does not include time that the sensor
        # was up for reschedule but not actually running. `timeout` does
        timeout=timeout,
    )

    sensor.execute(context)


@task_group(group_id="wait_for_external_dags")
def wait_for_external_dags_with_tag(tag: str, excluded_dag_ids: list[str] = None):
    """
    Wait until all DAGs with the given `tag`, excluding those identified by the
    `excluded_dag_ids`, are no longer in the running state before continuing.
    """
    external_dag_ids = get_dags_with_concurrency_tag.override(
        task_id=f"get_dags_in_{tag}_group"
    )(tag=tag, excluded_dag_ids=excluded_dag_ids or [])

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
def prevent_concurrency_with_dags_with_tag(
    tag: str, excluded_dag_ids: list[str] = None
):
    """
    Prevent concurrency with any DAGs that have the given `tag`, excluding
    those identified by the `excluded_dag_ids`. Concurrency is prevented by
    failing the task immediately if any of the tagged DAGs are in the running
    state.
    """
    external_dag_ids = get_dags_with_concurrency_tag.override(
        task_id=f"get_dags_in_{tag}_group"
    )(tag=tag, excluded_dag_ids=excluded_dag_ids or [])

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

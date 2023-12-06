from datetime import timedelta

from airflow.decorators import task, task_group
from airflow.exceptions import AirflowSensorTimeout
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.utils.state import State

from common import ingestion_server
from common.sensors.utils import get_most_recent_dag_run
from data_refresh.data_refresh_types import DATA_REFRESH_CONFIGS
from database.staging_database_restore.constants import (
    DAG_ID as STAGING_DB_RESTORE_DAG_ID,
)


DAG_ID = "recreate_full_staging_index"


@task(retries=0)
def prevent_concurrency_with_staging_database_restore(**context):
    wait_for_dag = ExternalTaskSensor(
        task_id="check_for_running_staging_db_restore",
        external_dag_id=STAGING_DB_RESTORE_DAG_ID,
        # Set timeout to 0 to prevent retries. If the staging DB restoration is running,
        # immediately fail the staging index creation DAG.
        timeout=0,
        # Wait for the whole DAG, not just a part of it
        external_task_id=None,
        check_existence=False,
        execution_date_fn=lambda _: get_most_recent_dag_run(STAGING_DB_RESTORE_DAG_ID),
        # Any "finished" state is sufficient for us to continue.
        allowed_states=[State.SUCCESS, State.FAILED],
        mode="reschedule",
    )
    try:
        wait_for_dag.execute(context)
    except AirflowSensorTimeout:
        raise ValueError(
            "Concurrency check failed. Staging index creation cannot start"
            " during staging DB restoration."
        )


@task
def get_target_alias(media_type: str, target_alias_override: str):
    return target_alias_override or f"{media_type}-full"


@task.branch
def should_delete_index(should_delete: bool, old_index: str):
    if should_delete and old_index:
        # We should try to delete the old index only if the param is enabled,
        # and we were able to find an index with the target_alias in the
        # preceding task.
        return "trigger_delete_index"
    # Skip straight to notifying Slack.
    return "notify_complete"


@task_group(group_id="create_index")
def create_index(media_type: str, index_suffix: str) -> None:
    """Create the new elasticsearch index on the staging cluster."""

    # Get the DataRefresh config associated with this media type, in order to get
    # the reindexing timeout information.
    config = DATA_REFRESH_CONFIGS.get(media_type)
    data_refresh_timeout = config.data_refresh_timeout if config else timedelta(days=1)

    ingestion_server.trigger_and_wait_for_task(
        action="REINDEX",
        model=media_type,
        data={"index_suffix": index_suffix},
        timeout=data_refresh_timeout,
        http_conn_id="staging_data_refresh",
    )


@task_group(group_id="point_alias")
def point_alias(media_type: str, target_alias: str, index_suffix: str) -> None:
    """
    Alias the index with the given suffix to the target_alias, first removing the
    target_alias from any other indices to which it is linked.
    """
    point_alias_payload = {
        "alias": target_alias,
        "index_suffix": index_suffix,
    }

    ingestion_server.trigger_and_wait_for_task(
        action="POINT_ALIAS",
        model=media_type,
        data=point_alias_payload,
        timeout=timedelta(hours=12),  # matches the ingestion server's wait time
        http_conn_id="staging_data_refresh",
    )

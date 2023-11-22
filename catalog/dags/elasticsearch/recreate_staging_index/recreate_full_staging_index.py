from datetime import timedelta

from airflow.decorators import task, task_group

from common import ingestion_server
from data_refresh.data_refresh_types import DATA_REFRESH_CONFIGS


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

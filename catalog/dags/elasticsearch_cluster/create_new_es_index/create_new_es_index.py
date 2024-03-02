import logging

from airflow.decorators import task

from common.elasticsearch import remove_excluded_index_settings
from elasticsearch_cluster.create_new_es_index.utils import merge_configurations


logger = logging.getLogger(__name__)


GET_FINAL_INDEX_CONFIG_TASK_NAME = "get_final_index_configuration"
GET_CURRENT_INDEX_CONFIG_TASK_NAME = "get_current_index_configuration"


@task
def get_index_name(media_type: str, index_suffix: str):
    return f"{media_type}-{index_suffix}".lower()


@task.branch
def check_override_config(override):
    if override:
        # Skip the steps to fetch the current index configuration
        # and merge changes in.
        return GET_FINAL_INDEX_CONFIG_TASK_NAME

    return GET_CURRENT_INDEX_CONFIG_TASK_NAME


@task
def merge_index_configurations(new_index_config, current_index_config):
    """
    Merge the `new_index_config` into the `current_index_config`, and
    return an index configuration in the appropriate format for being
    passed to the `create_index` API.
    """
    remove_excluded_index_settings(current_index_config)

    # Merge the new configuration values into the current configuration
    return merge_configurations(current_index_config, new_index_config)


@task
def get_final_index_configuration(
    override_config: bool,
    index_config,
    merged_config,
    index_name: str,
):
    """
    Resolve the final index configuration to be used in the `create_index`
    task.

    Required arguments:

    override_config: Whether the index_config should be used instead of
                     the merged_config
    index_config:    The new index configuration which was passed in via
                     DAG params
    merged_config:   The result of merging the index_config with the current
                     index configuration. This may be None if the merge
                     tasks were skipped using the override param.
    index_name:      Name of the index to update.
    """
    config = index_config if override_config else merged_config

    # Apply the desired index name
    config["index"] = index_name
    return config

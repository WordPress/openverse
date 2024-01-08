import logging
from datetime import timedelta

from airflow.decorators import task, task_group
from airflow.exceptions import AirflowException
from airflow.providers.elasticsearch.hooks.elasticsearch import ElasticsearchPythonHook
from airflow.sensors.python import PythonSensor
from es.create_new_es_index.utils import merge_configurations

from common.constants import REFRESH_POKE_INTERVAL


logger = logging.getLogger(__name__)


# Index settings that should not be copied over from the base configuration when
# creating a new index.
EXCLUDED_INDEX_SETTINGS = ["provided_name", "creation_date", "uuid", "version"]

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
def get_current_index_configuration(
    source_index: str,
    es_host: str,
):
    """
    Return the configuration for the current index, identified by the
    `source_index` param. `source_index` may be either an index name
    or an alias, but must uniquely identify one existing index or an
    error will be raised.
    """
    hook = ElasticsearchPythonHook(es_host)
    es_conn = hook.get_conn

    response = es_conn.indices.get(
        index=source_index,
        # Return empty dict instead of throwing error if no index can be
        # found. We raise our own error instead.
        ignore_unavailable=True,
    )

    if len(response) != 1:
        raise AirflowException(
            f"Index {source_index} could not be uniquely identified."
        )

    # The response has the form:
    #   { index_name: index_configuration }
    # However, since `source_index` can be an alias rather than the index name,
    # we do not necessarily know the index_name so we cannot access the configuration
    # directly by key. We instead get the first value from the dict, knowing that we
    # have already ensured in a previous check that there is exactly one value in the
    # response.
    config = next(iter(response.values()))
    return config


@task
def merge_index_configurations(new_index_config, current_index_config):
    """
    Merge the `new_index_config` into the `current_index_config`, and
    return an index configuration in the appropriate format for being
    passed to the `create_index` API.
    """
    # Do not automatically apply any aliases to the new index
    current_index_config.pop("aliases")

    # Remove fields from the current_index_config that should not be copied
    # over into the new index (such as uuid)
    for setting in EXCLUDED_INDEX_SETTINGS:
        current_index_config.get("settings", {}).get("index", {}).pop(setting)

    # Merge the new configuration values into the current configuration
    return merge_configurations(current_index_config, new_index_config)


@task
def get_final_index_configuration(
    override_config: bool,
    # The new config which was passed in via DAG params
    index_config,
    # The result of merging the index_config with the current index config.
    # This may be None if the merge tasks were skipped using the override param.
    merged_config,
    index_name: str,
):
    """
    Resolve the final index configuration to be used in the `create_index`
    task.
    """
    config = index_config if override_config else merged_config

    # Apply the desired index name
    config["index"] = index_name
    return config


@task
def create_index(index_config, es_host: str):
    hook = ElasticsearchPythonHook(es_host)
    es_conn = hook.get_conn

    new_index = es_conn.indices.create(**index_config)

    return new_index


@task_group(group_id="trigger_and_wait_for_reindex")
def trigger_and_wait_for_reindex(
    index_name: str, source_index: str, query: dict, timeout: timedelta, es_host: str
):
    @task
    def trigger_reindex(index_name: str, source_index: str, query: dict, es_host: str):
        hook = ElasticsearchPythonHook(es_host)
        es_conn = hook.get_conn

        source = {"index": source_index}
        # An empty query is not accepted; only pass it
        # if a query was actually supplied
        if query:
            source["query"] = query

        response = es_conn.reindex(
            source=source,
            dest={"index": index_name},
            # Parallelize indexing
            slices="auto",
            # Do not hold the slot while awaiting completion
            wait_for_completion=False,
            # Immediately refresh the index after completion to make
            # the data available for search
            refresh=True,
        )

        return response["task"]

    def _wait_for_reindex(task_id: str, es_host: str):
        hook = ElasticsearchPythonHook(es_host)
        es_conn = hook.get_conn

        response = es_conn.tasks.get(task_id=task_id)
        return response.get("completed")

    trigger_reindex_task = trigger_reindex(index_name, source_index, query, es_host)

    wait_for_reindex = PythonSensor(
        task_id="wait_for_reindex",
        python_callable=_wait_for_reindex,
        timeout=timeout,
        poke_interval=REFRESH_POKE_INTERVAL,
        op_kwargs={"task_id": trigger_reindex_task, "es_host": es_host},
    )

    trigger_reindex_task >> wait_for_reindex

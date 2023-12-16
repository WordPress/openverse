import logging

from airflow.decorators import task, task_group
from airflow.exceptions import AirflowException, AirflowSensorTimeout
from airflow.providers.elasticsearch.hooks.elasticsearch import ElasticsearchPythonHook
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.sensors.python import PythonSensor
from airflow.utils.state import State
from es.create_new_es_index.utils import merge_configurations

from common.sensors.utils import get_most_recent_dag_run


logger = logging.getLogger(__name__)


# Index settings that should not be copied over from the base configuration when
# creating a new index.
EXCLUDED_INDEX_SETTINGS = ["provided_name", "creation_date", "uuid", "version"]


# TODO: This can be removed in favor of the utility in
# https://github.com/WordPress/openverse/pull/3482
@task(retries=0)
def prevent_concurrency_with_dag(external_dag_id: str, **context):
    """
    Prevent concurrency with the given external DAG, by failing
    immediately if that DAG is running.
    """

    wait_for_dag = ExternalTaskSensor(
        task_id=f"prevent_concurrency_with_{external_dag_id}",
        external_dag_id=external_dag_id,
        # Wait for the whole DAG, not just a part of it
        external_task_id=None,
        check_existence=False,
        execution_date_fn=lambda _: get_most_recent_dag_run(external_dag_id),
        mode="reschedule",
        retries=0,
        # Any "finished" state is sufficient for us to continue
        allowed_states=[State.SUCCESS, State.FAILED],
    )
    wait_for_dag.timeout = 0
    try:
        wait_for_dag.execute(context)
    except AirflowSensorTimeout:
        raise ValueError(f"Concurrency check with {external_dag_id} failed.")


@task_group(group_id="prevent_concurrency")
def prevent_concurrency_with_dags(external_dag_ids: list[str]):
    """Fail immediately if any of the given external dags are in progress."""
    # TODO: Double check if these need to be chained or if they can
    # run concurrently
    for dag_id in external_dag_ids:
        prevent_concurrency_with_dag.override(
            task_id=f"prevent_concurrency_with_{dag_id}"
        )(dag_id)


@task
def get_index_name(media_type: str, index_suffix: str):
    return f"{media_type}-{index_suffix}".lower()


@task.branch
def check_override_config(override):
    if override:
        # Skip the steps to fetch the current index configuration
        # and merge changes in.
        return "get_final_index_configuration"

    return "get_current_index_configuration"


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
    logger.info(es_host)
    hook = ElasticsearchPythonHook(es_host)
    es_conn = hook.get_conn

    response = es_conn.indices.get(
        index=source_index,
        # Return empty dict instead of throwing error if no index can be
        # found. This lets us raise our own error.
        ignore_unavailable=True,
    )

    if len(response) != 1:
        raise AirflowException(
            f"Index {source_index} could not be uniquely identified."
        )

    # The response has the form:
    #   { index_name: index_configuration }
    # However, since `source_index` can be an alias rather than the index name,
    # we can not reliably know the value of the key. We instead get the first
    # value, knowing that we have already ensured in a previous check that there
    # is exactly one value in the response.
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
    # over into the new index
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
    # This may be None if the merge tasks were skipped.
    merged_config,
    index_name: str,
):
    """
    Resolve the final index configuration to be used in the `create_index`
    task.
    """
    config = index_config if override_config else merged_config

    # Apply the index name
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
    index_name: str, source_index: str, query: dict, es_host: str
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

    PythonSensor(
        task_id="wait_for_reindex",
        python_callable=_wait_for_reindex,
        op_kwargs={"task_id": trigger_reindex_task, "es_host": es_host},
    )

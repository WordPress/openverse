import logging
from datetime import timedelta

from airflow.decorators import task, task_group
from airflow.models.connection import Connection
from airflow.providers.elasticsearch.hooks.elasticsearch import ElasticsearchPythonHook
from airflow.sensors.python import PythonSensor

from common.constants import REFRESH_POKE_INTERVAL


logger = logging.getLogger(__name__)


# Index settings that should not be copied over from the base configuration when
# creating a new index.
EXCLUDED_INDEX_SETTINGS = ["provided_name", "creation_date", "uuid", "version"]


@task
def get_es_host(environment: str):
    conn = Connection.get_connection_from_secrets(f"elasticsearch_http_{environment}")
    return conn.get_uri()


@task
def get_index_configuration(
    source_index: str,
    es_host: str,
):
    """
    Return the configuration for the index identified by the
    `source_index` param. `source_index` may be either an index name
    or an alias, but must uniquely identify one existing index or an
    error will be raised.
    """
    es_conn = ElasticsearchPythonHook(hosts=[es_host]).get_conn

    response = es_conn.indices.get(
        index=source_index,
        # Return empty dict instead of throwing error if no index can be
        # found. We raise our own error instead.
        ignore_unavailable=True,
    )

    if len(response) != 1:
        raise ValueError(f"Index {source_index} could not be uniquely identified.")

    # The response has the form:
    #   { index_name: index_configuration }
    # However, since `source_index` can be an alias rather than the index name,
    # we do not necessarily know the index_name so we cannot access the configuration
    # directly by key. We instead get the first value from the dict, knowing that we
    # have already ensured in a previous check that there is exactly one value in the
    # response.
    config = next(iter(response.values()))
    return config


def remove_excluded_index_settings(index_config):
    """
    Remove fields from the given index configuration that should not be included when
    using it to create a new index.
    """
    # Remove fields from the current_index_config that should not be copied
    # over into the new index (such as uuid)
    for setting in EXCLUDED_INDEX_SETTINGS:
        index_config.get("settings", {}).get("index", {}).pop(setting)

    # Aliases should also not by applied automatically
    index_config.pop("aliases")

    return index_config


@task
def create_index(index_config, es_host: str):
    es_conn = ElasticsearchPythonHook(hosts=[es_host]).get_conn

    new_index = es_conn.indices.create(**index_config)

    return new_index


@task_group(group_id="trigger_and_wait_for_reindex")
def trigger_and_wait_for_reindex(
    destination_index: str,
    source_index: str,
    query: dict,
    timeout: timedelta,
    requests_per_second: int,
    es_host: str,
    max_docs: int | None = None,
):
    @task
    def trigger_reindex(
        es_host: str,
        destination_index: str,
        source_index: str,
        query: dict,
        requests_per_second: int,
        max_docs: int | None,
    ):
        es_conn = ElasticsearchPythonHook(hosts=[es_host]).get_conn

        logger.info(query)
        logger.info(max_docs)

        source = {"index": source_index}
        # An empty query is not accepted; only pass it
        # if a query was actually supplied
        if query:
            source["query"] = query

        response = es_conn.reindex(
            source=source,
            dest={"index": destination_index},
            max_docs=max_docs,
            # Parallelize indexing
            slices="auto",
            # Do not hold the slot while awaiting completion
            wait_for_completion=False,
            # Immediately refresh the index after completion to make
            # the data available for search
            refresh=True,
            # Throttle
            requests_per_second=requests_per_second,
        )

        return response["task"]

    def _wait_for_reindex(task_id: str, es_host: str):
        es_conn = ElasticsearchPythonHook(hosts=[es_host]).get_conn

        response = es_conn.tasks.get(task_id=task_id)
        return response.get("completed")

    trigger_reindex_task = trigger_reindex(
        es_host, destination_index, source_index, query, requests_per_second, max_docs
    )

    wait_for_reindex = PythonSensor(
        task_id="wait_for_reindex",
        python_callable=_wait_for_reindex,
        timeout=timeout,
        poke_interval=REFRESH_POKE_INTERVAL,
        op_kwargs={"task_id": trigger_reindex_task, "es_host": es_host},
    )

    trigger_reindex_task >> wait_for_reindex

import logging
from datetime import timedelta
from typing import Literal, Union

from airflow.decorators import task, task_group
from airflow.exceptions import AirflowSkipException
from airflow.models.connection import Connection
from airflow.providers.elasticsearch.hooks.elasticsearch import ElasticsearchPythonHook
from airflow.sensors.base import PokeReturnValue
from airflow.utils.trigger_rule import TriggerRule
from elasticsearch.exceptions import NotFoundError

from common.constants import REFRESH_POKE_INTERVAL


logger = logging.getLogger(__name__)


# Index settings that should not be copied over from the base configuration when
# creating a new index.
EXCLUDED_INDEX_SETTINGS = {"provided_name", "creation_date", "uuid", "version"}


@task
def get_es_host(environment: str):
    es_conn = Connection.get_connection_from_secrets(
        f"elasticsearch_http_{environment}"
    )
    return es_conn.get_uri()


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
    es_host: str,
    destination_index: str,
    source_index: str,
    timeout: timedelta,
    requests_per_second: int,
    query: dict | None = None,
    max_docs: int | None = None,
    refresh: bool = True,
    slices: Union[int, Literal["auto"]] = "auto",
):
    @task
    def trigger_reindex(
        es_host: str,
        destination_index: str,
        source_index: str,
        query: dict,
        requests_per_second: int,
        max_docs: int | None,
        slices: Union[int, Literal["auto"]],
    ):
        es_conn = ElasticsearchPythonHook(hosts=[es_host]).get_conn
        source = {"index": source_index}
        # An empty query is not accepted; only pass it
        # if a query was actually supplied
        if query:
            source["query"] = query

        response = es_conn.reindex(
            source=source,
            dest={"index": destination_index},
            max_docs=max_docs,
            # Parallelize indexing when not None
            slices=slices,
            # Do not hold the slot while awaiting completion
            wait_for_completion=False,
            # Whether to immediately refresh the index after completion to make
            # the data available for search
            refresh=refresh,
            # Throttle
            requests_per_second=requests_per_second,
        )
        return response["task"]

    @task.sensor(
        poke_interval=REFRESH_POKE_INTERVAL, timeout=timeout, mode="reschedule"
    )
    def wait_for_reindex(
        es_host: str, task_id: str, expected_docs: int | None = None
    ) -> PokeReturnValue:
        es_conn = ElasticsearchPythonHook(hosts=[es_host]).get_conn

        response = es_conn.tasks.get(task_id=task_id)

        count = response.get("task", {}).get("status", {}).get("total")
        if expected_docs and count != expected_docs:
            logger.info(
                f"Reindexed {count} documents, but {expected_docs} were expected."
            )
        else:
            logger.info(f"Reindexed {count} documents.")

        return PokeReturnValue(is_done=response.get("completed") is True)

    trigger_reindex_task = trigger_reindex(
        es_host,
        destination_index,
        source_index,
        query,
        requests_per_second,
        max_docs,
        slices,
    )

    wait_for_reindex_task = wait_for_reindex(
        task_id=trigger_reindex_task, expected_docs=max_docs, es_host=es_host
    )

    trigger_reindex_task >> wait_for_reindex_task


@task
def refresh_index(es_host: str, index_name: str):
    es_conn = ElasticsearchPythonHook(hosts=[es_host]).get_conn
    return es_conn.indices.refresh(index=index_name)


@task_group(group_id="point_alias")
def point_alias(
    es_host: str,
    target_index: str,
    target_alias: str,
    should_delete_old_index: bool = False,
):
    """
    Point the target alias to the given index. If the alias is already being
    used by another index, it will be removed from this index first. Optionally,
    that index may also be automatically deleted.

    Required Arguments:

    es_host:      Connection string for elasticsearch
    target_index: Str identifier for the target index. May be either the index name
                  or an existing alias.
    target_alias: The new alias to be applied to the target index

    Optional Arguments:

    should_delete_old_index:    If True, any indices with the target alias _other_
                                  than the target index will be deleted.
    """

    @task
    def get_existing_index(es_host: str, target_alias: str):
        """Get the index to which the target alias currently points, if it exists."""
        if not target_alias:
            raise AirflowSkipException("No target alias was provided.")

        es_conn = ElasticsearchPythonHook(hosts=[es_host]).get_conn

        try:
            response = es_conn.indices.get_alias(name=target_alias)
            if len(response) > 1:
                raise ValueError(
                    "Expected at most one existing index with target alias"
                    f"{target_alias}, but {len(response)} were found."
                )
            return list(response.keys())[0]
        except NotFoundError:
            logger.info(f"Target alias {target_alias} does not exist.")
            return None

    @task
    def remove_alias_from_existing_index(
        es_host: str,
        index_name: str,
        target_alias: str,
    ):
        """Remove the given alias from the given index."""
        if not index_name:
            raise AirflowSkipException(
                "No existing index from which to remove the target alias."
            )

        es_conn = ElasticsearchPythonHook(hosts=[es_host]).get_conn
        response = es_conn.indices.delete_alias(
            name=target_alias,
            index=index_name,
        )
        return response.get("acknowledged")

    @task
    def point_new_alias(
        es_host: str,
        target_index: str,
        target_alias: str,
    ):
        if not target_alias:
            raise AirflowSkipException("No target alias was provided.")

        es_conn = ElasticsearchPythonHook(hosts=[es_host]).get_conn
        response = es_conn.indices.put_alias(index=target_index, name=target_alias)
        return response.get("acknowledged")

    @task
    def delete_old_index(es_host: str, index_name: str, should_delete_old_index: bool):
        if not should_delete_old_index:
            raise AirflowSkipException("`should_delete_old_index` is set to `False`.")

        es_conn = ElasticsearchPythonHook(hosts=[es_host]).get_conn
        response = es_conn.indices.delete(
            index=index_name,
        )
        return response.get("acknowledged")

    existing_index = get_existing_index(es_host, target_alias)
    remove_alias = remove_alias_from_existing_index(
        es_host, existing_index, target_alias
    )

    point_alias = point_new_alias.override(
        # `remove_alias_from_existing_index` is skipped if there is no
        # existing index
        trigger_rule=TriggerRule.NONE_FAILED
    )(es_host, target_index, target_alias)

    delete_index = delete_old_index(es_host, existing_index, should_delete_old_index)

    existing_index >> remove_alias >> point_alias
    point_alias >> delete_index

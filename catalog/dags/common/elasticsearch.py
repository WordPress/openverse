import json
import logging
import time
from datetime import timedelta
from typing import Literal

from airflow.providers.elasticsearch.hooks.elasticsearch import ElasticsearchPythonHook
from airflow.providers.standard.triggers.temporal import TimeDeltaTrigger
from airflow.sdk import BaseOperator, Connection, task, task_group
from airflow.sdk.exceptions import AirflowFailException, AirflowSkipException
from elasticsearch.exceptions import NotFoundError

from common.constants import REFRESH_POKE_INTERVAL


logger = logging.getLogger(__name__)


# Index settings that should not be copied over from the base configuration when
# creating a new index.
EXCLUDED_INDEX_SETTINGS = {"provided_name", "creation_date", "uuid", "version"}

# Reindex errors caused by an overloaded cluster rather than by the data: rejected
# searches or writes, a tripped memory circuit breaker, or a scroll lost while
# shards were busy. A reindex that fails only with these is restarted.
OVERLOAD_REINDEX_ERRORS = (
    "es_rejected_execution_exception",
    "circuit_breaking_exception",
    "search_context_missing_exception",
    "No search context found",
)
REINDEX_MAX_RESTARTS = 5
# Doubles on each restart: 10, 20, 40, 80 and 160 minutes
REINDEX_RESTART_BACKOFF = timedelta(minutes=10)


@task
def get_es_host(environment: str):
    es_conn = Connection.get(f"elasticsearch_http_{environment}")
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
def get_index_configuration_copy(
    source_index: str, target_index_name: str, es_host: str
):
    """
    Create a new index configuration based off the `source_index` but with the given
    `target_index_name`, in the format needed for `create_index`. Removes fields that
    should not be copied into a new index configuration such as the uuid.
    """
    base_config = get_index_configuration.function(source_index, es_host)

    cleaned_config = remove_excluded_index_settings(base_config)

    cleaned_config["index"] = target_index_name

    return cleaned_config


@task
def get_record_count_group_by_sources(es_host: str, index: str):
    """
    Return a dict where the keys are the sources, and the values are the counts.
    Calls Elasticsearch to run an aggs query to do a count grouped by the field "source", and parses the result into a dict.
    """
    body = {"aggs": {"unique_sources": {"terms": {"field": "source"}}}}

    # Unfornately the ElasticsearchPythonHook's search function doesn't work with aggs, because it returns the "hits" key only
    # See source code at https://airflow.apache.org/docs/apache-airflow-providers-elasticsearch/stable/_modules/airflow/providers/elasticsearch/hooks/elasticsearch.html#ElasticsearchPythonHook
    # Therefore using get_conn to call the search from the ES client
    es_client = ElasticsearchPythonHook(hosts=[es_host]).get_conn
    try:
        es_result = es_client.search(body=body, index=index)
    except NotFoundError as err:
        logger.warning(f"Elasticsearch index: {index} does not exist. Error msg: {err}")
        return {}

    # es_buckets object looks like: [{'key': 'flickr', 'doc_count': 2500}, {'key': 'stocksnap', 'doc_count': 2500}]
    es_buckets = es_result["aggregations"]["unique_sources"]["buckets"]
    result = {
        source_count["key"]: source_count["doc_count"] for source_count in es_buckets
    }

    return result


@task
def create_index(index_config, es_host: str, exist_ok: bool = False):
    """
    Create the index described by ``index_config``.

    With ``exist_ok``, an index of that name left by an earlier attempt is reused,
    so that clearing a failed run continues filling it. An index that an alias
    points to is in use, so it is never reused.
    """
    es_conn = ElasticsearchPythonHook(hosts=[es_host]).get_conn
    index_name = index_config["index"]

    if exist_ok and es_conn.indices.exists(index=index_name):
        if aliases := es_conn.indices.get_alias(index=index_name)[index_name].get(
            "aliases"
        ):
            raise AirflowFailException(
                f"Index {index_name} already exists and is aliased by "
                f"{list(aliases)}, so it cannot be reused."
            )
        logger.info(f"Reusing the existing index {index_name}.")
        return

    new_index = es_conn.indices.create(**index_config).body

    return new_index


def get_reindex_failure_reasons(response: dict) -> dict:
    """
    Return why a finished reindex task failed, or an empty dict if it succeeded.

    A reindex run with ``wait_for_completion=False`` still reports ``completed`` when
    it fails, with the cause in ``error`` (for example, an expired scroll),
    ``response.failures`` (rejected documents), ``response.canceled`` (cancelled
    through the tasks API) or ``response.timed_out``.
    """
    body = response.get("response", {})
    reasons = {
        "error": response.get("error"),
        "failures": (body.get("failures") or [])[:5],
        "canceled": body.get("canceled"),
        "timed_out": body.get("timed_out"),
    }
    return {key: value for key, value in reasons.items() if value}


def raise_for_reindex_failure(response: dict) -> None:
    """
    Raise if a finished reindex task failed.

    Raises ``AirflowFailException`` so the task does not retry: polling the same
    finished ES task again cannot succeed. To recover, clear the whole
    ``trigger_and_wait_for_reindex`` group so the reindex is triggered again.
    """
    if reasons := get_reindex_failure_reasons(response):
        raise AirflowFailException(
            f"Reindex failed: {reasons}. Clear the trigger_and_wait_for_reindex "
            "task group to trigger the reindex again."
        )


def _is_overload_failure(failure: dict) -> bool:
    text = json.dumps(failure, default=str)
    return '"status": 429' in text or any(
        marker in text for marker in OVERLOAD_REINDEX_ERRORS
    )


def is_retryable_reindex_failure(response: dict) -> bool:
    """
    Whether a finished reindex failed only because the cluster was overloaded, so
    restarting it later can succeed.

    A reindex that was cancelled or timed out, or that has any other kind of
    failure (such as a mapping error), is not retryable.
    """
    body = response.get("response", {})
    if body.get("canceled") or body.get("timed_out"):
        return False
    failures = [response["error"]] if response.get("error") else []
    failures += body.get("failures") or []
    return bool(failures) and all(_is_overload_failure(f) for f in failures)


def start_reindex(
    es_conn,
    destination_index: str,
    source_index: str,
    query: dict | None,
    requests_per_second: int,
    max_docs: int | None,
    slices: int | Literal["auto"] | None,
    refresh: bool,
) -> str:
    """Start a reindex without waiting for it, and return its ES task ID."""
    source = {"index": source_index}
    # An empty query is not accepted; only pass it
    # if a query was actually supplied
    if query:
        source["query"] = query

    response = es_conn.reindex(
        source=source,
        # Only create documents that are missing from the destination, so that a
        # restarted reindex skips the ones an earlier attempt already copied.
        dest={"index": destination_index, "op_type": "create"},
        # Skipped documents are reported as version conflicts; count them
        # instead of failing on them.
        conflicts="proceed",
        max_docs=max_docs,
        # Parallelize indexing when not None
        slices=slices,
        # The default 5m scroll keep-alive expires while slow bulk writes to the
        # destination index hold up a slice, failing the whole reindex with
        # "No search context found".
        scroll="1h",
        # Do not hold the slot while awaiting completion
        wait_for_completion=False,
        # Whether to immediately refresh the index after completion to make
        # the data available for search
        refresh=refresh,
        # Throttle
        requests_per_second=requests_per_second,
    )
    return response["task"]


class WaitForReindexOperator(BaseOperator):
    """
    Wait for a reindex started by ``trigger_reindex``, restarting it when it fails
    because the cluster is overloaded.

    It defers between checks, which frees the worker slot and carries the current
    ES task ID from one check to the next. Each restart waits twice as long as the
    one before, and only creates the documents that are still missing.
    """

    template_fields = ("es_host", "reindex")

    def __init__(
        self,
        *,
        es_host: str,
        reindex: dict,
        reindex_timeout: timedelta,
        poke_interval: int = REFRESH_POKE_INTERVAL,
        max_restarts: int = REINDEX_MAX_RESTARTS,
        restart_backoff: timedelta = REINDEX_RESTART_BACKOFF,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.es_host = es_host
        # The output of `trigger_reindex`: the ES task ID and the reindex arguments
        self.reindex = reindex
        self.reindex_timeout = reindex_timeout
        self.poke_interval = poke_interval
        self.max_restarts = max_restarts
        self.restart_backoff = restart_backoff

    def execute(self, context):
        deadline = time.time() + self.reindex_timeout.total_seconds()
        self.check_reindex(
            context,
            es_task_id=self.reindex["es_task_id"],
            restarts=0,
            created_before=0,
            deadline=deadline,
        )

    def check_reindex(
        self,
        context,
        event=None,
        *,
        es_task_id: str,
        restarts: int,
        created_before: int,
        deadline: float,
    ):
        """
        Check the reindex task, and defer until the next check, defer until a
        restart, or finish.

        ``created_before`` is the number of documents earlier attempts created.
        """
        es_conn = ElasticsearchPythonHook(hosts=[self.es_host]).get_conn
        response = es_conn.tasks.get(task_id=es_task_id)
        status = response.get("task", {}).get("status", {})
        created = created_before + (status.get("created") or 0)
        logger.info(
            f"Reindex task {es_task_id}: {created} documents created so far, "
            f"{status.get('version_conflicts') or 0} already present, "
            f"{restarts} restarts."
        )

        if not response.get("completed"):
            if time.time() > deadline:
                raise AirflowFailException(
                    f"Reindex did not finish within {self.reindex_timeout}."
                )
            self._defer(
                "check_reindex",
                timedelta(seconds=self.poke_interval),
                es_task_id=es_task_id,
                restarts=restarts,
                created_before=created_before,
                deadline=deadline,
            )

        if not get_reindex_failure_reasons(response):
            expected_docs = self.reindex["kwargs"].get("max_docs")
            if expected_docs and created != expected_docs:
                logger.info(
                    f"Reindexed {created} documents, but {expected_docs} were expected."
                )
            else:
                logger.info(f"Reindexed {created} documents.")
            return

        if restarts < self.max_restarts and is_retryable_reindex_failure(response):
            backoff = self.restart_backoff * 2**restarts
            logger.warning(
                "Reindex failed because the cluster is overloaded: "
                f"{get_reindex_failure_reasons(response)}. Restarting in {backoff} "
                f"(restart {restarts + 1} of {self.max_restarts})."
            )
            self._defer(
                "restart_reindex",
                backoff,
                restarts=restarts + 1,
                created_before=created,
                deadline=deadline,
            )

        raise_for_reindex_failure(response)

    def restart_reindex(
        self,
        context,
        event=None,
        *,
        restarts: int,
        created_before: int,
        deadline: float,
    ):
        if time.time() > deadline:
            raise AirflowFailException(
                f"Reindex did not finish within {self.reindex_timeout}."
            )

        reindex_kwargs = dict(self.reindex["kwargs"])
        if max_docs := reindex_kwargs.get("max_docs"):
            # The earlier attempts already created some of the requested documents
            reindex_kwargs["max_docs"] = max_docs - created_before
            if reindex_kwargs["max_docs"] <= 0:
                logger.info(f"Reindexed {created_before} documents.")
                return

        es_conn = ElasticsearchPythonHook(hosts=[self.es_host]).get_conn
        es_task_id = start_reindex(es_conn, **reindex_kwargs)
        logger.info(f"Restarted the reindex as task {es_task_id}.")
        self._defer(
            "check_reindex",
            timedelta(seconds=self.poke_interval),
            es_task_id=es_task_id,
            restarts=restarts,
            created_before=created_before,
            deadline=deadline,
        )

    def _defer(self, method_name: str, delay: timedelta, **kwargs):
        self.defer(
            trigger=TimeDeltaTrigger(delay),
            method_name=method_name,
            kwargs=kwargs,
        )


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
    slices: int | Literal["auto"] | None = "auto",
    poke_interval: int = REFRESH_POKE_INTERVAL,
):
    @task
    def trigger_reindex(
        es_host: str,
        destination_index: str,
        source_index: str,
        query: dict,
        requests_per_second: int,
        max_docs: int | None,
        slices: int | Literal["auto"] | None,
    ):
        reindex_kwargs = {
            "destination_index": destination_index,
            "source_index": source_index,
            "query": query,
            "requests_per_second": requests_per_second,
            "max_docs": max_docs,
            "slices": slices,
            "refresh": refresh,
        }
        es_conn = ElasticsearchPythonHook(hosts=[es_host]).get_conn
        es_task_id = start_reindex(es_conn, **reindex_kwargs)
        # Return the rendered arguments too, so a restart uses the same ones
        return {"es_task_id": es_task_id, "kwargs": reindex_kwargs}

    trigger_reindex_task = trigger_reindex(
        es_host,
        destination_index,
        source_index,
        query,
        requests_per_second,
        max_docs,
        slices,
    )

    WaitForReindexOperator(
        task_id="wait_for_reindex",
        es_host=es_host,
        reindex=trigger_reindex_task,
        reindex_timeout=timeout,
        poke_interval=poke_interval,
    )


@task
def refresh_index(es_host: str, index_name: str):
    es_conn = ElasticsearchPythonHook(hosts=[es_host]).get_conn
    return es_conn.indices.refresh(index=index_name).body


@task
def enable_replicas(es_host: str, index_names: list[str]):
    """
    Give each index one replica of every shard. Indices are built without replicas
    to speed up reindexing, but serving one without them leaves a single copy of
    the data and half the shards to spread searches over.
    """
    es_conn = ElasticsearchPythonHook(hosts=[es_host]).get_conn
    return es_conn.indices.put_settings(
        index=",".join(index_names),
        settings={"index": {"number_of_replicas": 1}},
    ).body


@task.sensor(mode="reschedule")
def wait_for_green_indices(es_host: str, index_names: list[str]) -> bool:
    """Wait until every shard of the indices, replicas included, is allocated."""
    es_conn = ElasticsearchPythonHook(hosts=[es_host]).get_conn
    health = es_conn.cluster.health(index=",".join(index_names))
    logger.info(
        f"{index_names} are {health['status']}: "
        f"{health['initializing_shards']} shards initializing, "
        f"{health['unassigned_shards']} unassigned."
    )
    return health["status"] == "green"


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

    should_delete_old_index:    If True, the index previously pointed to by the target
                                alias (if one exists) will be deleted.
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
    def point_new_alias(
        es_host: str,
        target_index: str,
        existing_index: str,
        target_alias: str,
    ):
        """
        Remove the target_alias from the existing index to which it applies, if
        applicable, and point it to the target_index in one atomic operation.
        """
        if not target_alias:
            raise AirflowSkipException("No target alias was provided.")

        es_conn = ElasticsearchPythonHook(hosts=[es_host]).get_conn

        actions = []
        if existing_index:
            actions.append({"remove": {"index": existing_index, "alias": target_alias}})
        actions.append({"add": {"index": target_index, "alias": target_alias}})
        logger.info(f"Applying actions: {actions}")

        response = es_conn.indices.update_aliases(body={"actions": actions})
        return response.get("acknowledged")

    @task
    def delete_old_index(es_host: str, index_name: str, should_delete_old_index: bool):
        if not should_delete_old_index:
            raise AirflowSkipException("`should_delete_old_index` is set to `False`.")
        if not index_name:
            raise AirflowSkipException("No applicable index to delete.")

        es_conn = ElasticsearchPythonHook(hosts=[es_host]).get_conn
        response = es_conn.indices.delete(index=index_name)
        return response.get("acknowledged")

    existing_index = get_existing_index(es_host, target_alias)

    point_alias = point_new_alias(es_host, target_index, existing_index, target_alias)

    delete_index = delete_old_index(es_host, existing_index, should_delete_old_index)

    existing_index >> point_alias >> delete_index

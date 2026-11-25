import time
from datetime import timedelta
from types import SimpleNamespace
from unittest import mock

import pytest
from airflow.sdk import timezone
from airflow.sdk.exceptions import AirflowFailException, TaskDeferred
from elasticsearch.exceptions import ApiError

from common import elasticsearch as es
from common.elasticsearch import (
    REINDEX_RESTART_BACKOFF,
    WaitForDeleteByQueryOperator,
    WaitForReindexOperator,
    is_retryable_reindex_failure,
    raise_for_reindex_failure,
)


@pytest.mark.parametrize(
    "response",
    [
        pytest.param(
            {"completed": True, "response": {"total": 10, "failures": []}},
            id="succeeded",
        ),
        pytest.param({"completed": True}, id="no_response_body"),
        pytest.param(
            {"completed": True, "response": {"canceled": "", "timed_out": False}},
            id="not_canceled_or_timed_out",
        ),
    ],
)
def test_raise_for_reindex_failure_passes(response):
    raise_for_reindex_failure(response)


@pytest.mark.parametrize(
    "response",
    [
        pytest.param(
            {
                "completed": True,
                "error": {
                    "type": "search_phase_execution_exception",
                    "reason": "No search context found for id [42]",
                },
            },
            id="task_error",
        ),
        pytest.param(
            {
                "completed": True,
                "response": {
                    "total": 10,
                    "failures": [{"index": "dest", "id": "1", "status": 400}],
                },
            },
            id="document_failures",
        ),
        pytest.param(
            {
                "completed": True,
                "response": {"failures": [], "canceled": "by user request"},
            },
            id="canceled",
        ),
        pytest.param(
            {"completed": True, "response": {"failures": [], "timed_out": True}},
            id="timed_out",
        ),
    ],
)
def test_raise_for_reindex_failure_raises(response):
    with pytest.raises(AirflowFailException, match="Reindex failed"):
        raise_for_reindex_failure(response)


def _hook(monkeypatch, es_conn):
    monkeypatch.setattr(
        es, "ElasticsearchPythonHook", lambda hosts: SimpleNamespace(get_conn=es_conn)
    )


def _task_response(completed=True, created=0, error=None, **body):
    response = {
        "completed": completed,
        "task": {"status": {"created": created, "version_conflicts": 0}},
    }
    if error:
        response["error"] = error
    if completed:
        response["response"] = {"failures": [], **body}
    return response


REJECTED_SEARCH = {
    "type": "search_phase_execution_exception",
    "caused_by": {"type": "es_rejected_execution_exception", "reason": "rejected"},
}
LOST_SCROLL = {
    "type": "search_phase_execution_exception",
    "reason": "No search context found for id [42]",
}
REJECTED_DOC = {"index": "dest", "id": "1", "status": 429, "cause": {}}
MAPPING_ERROR = {
    "index": "dest",
    "id": "2",
    "status": 400,
    "cause": {"type": "mapper_parsing_exception"},
}


@pytest.mark.parametrize(
    "response, expected",
    [
        pytest.param(_task_response(error=REJECTED_SEARCH), True, id="rejected_search"),
        pytest.param(_task_response(error=LOST_SCROLL), True, id="lost_scroll"),
        pytest.param(
            _task_response(failures=[REJECTED_DOC]), True, id="rejected_documents"
        ),
        pytest.param(
            _task_response(failures=[REJECTED_DOC, MAPPING_ERROR]),
            False,
            id="rejected_and_mapping_error",
        ),
        pytest.param(_task_response(failures=[MAPPING_ERROR]), False, id="mapping"),
        pytest.param(
            _task_response(error=REJECTED_SEARCH, canceled="by user request"),
            False,
            id="canceled",
        ),
        pytest.param(_task_response(timed_out=True), False, id="timed_out"),
        pytest.param(_task_response(), False, id="succeeded"),
    ],
)
def test_is_retryable_reindex_failure(response, expected):
    assert is_retryable_reindex_failure(response) is expected


REINDEX_KWARGS = {
    "destination_index": "image-new-filtered",
    "source_index": "image-new",
    "query": {"match_all": {}},
    "requests_per_second": 20_000,
    "max_docs": None,
    "slices": "auto",
    "refresh": False,
}


def _operator(max_docs=None, max_restarts=2):
    return WaitForReindexOperator(
        task_id="wait_for_reindex",
        es_host="http://es:9200",
        reindex={
            "es_task_id": "node:1",
            "kwargs": {**REINDEX_KWARGS, "max_docs": max_docs},
        },
        reindex_timeout=timedelta(hours=1),
        poke_interval=60,
        max_restarts=max_restarts,
    )


def test_wait_for_reindex_defers_while_running(monkeypatch):
    es_conn = mock.Mock()
    es_conn.tasks.get.return_value = _task_response(completed=False, created=5)
    _hook(monkeypatch, es_conn)

    with pytest.raises(TaskDeferred) as deferred:
        _operator().execute({})

    assert deferred.value.method_name == "check_reindex"
    assert deferred.value.kwargs["es_task_id"] == "node:1"
    assert deferred.value.kwargs["restarts"] == 0


def test_wait_for_reindex_finishes_on_success(monkeypatch):
    es_conn = mock.Mock()
    es_conn.tasks.get.return_value = _task_response(created=10)
    _hook(monkeypatch, es_conn)

    _operator().execute({})

    es_conn.reindex.assert_not_called()


def test_wait_for_reindex_restarts_after_overload(monkeypatch):
    es_conn = mock.Mock()
    es_conn.tasks.get.return_value = _task_response(created=7, error=REJECTED_SEARCH)
    _hook(monkeypatch, es_conn)

    with pytest.raises(TaskDeferred) as deferred:
        _operator().execute({})

    assert deferred.value.method_name == "restart_reindex"
    assert deferred.value.kwargs["restarts"] == 1
    assert deferred.value.kwargs["created_before"] == 7
    wait = deferred.value.trigger.moment - timezone.utcnow()
    assert REINDEX_RESTART_BACKOFF - timedelta(minutes=1) < wait
    assert wait <= REINDEX_RESTART_BACKOFF


@pytest.mark.parametrize(
    "max_docs, expected_max_docs", [(None, None), (100, 93)], ids=["all", "max_docs"]
)
def test_restart_reindex_creates_only_missing_documents(
    monkeypatch, max_docs, expected_max_docs
):
    es_conn = mock.Mock()
    es_conn.reindex.return_value = {"task": "node:2"}
    _hook(monkeypatch, es_conn)

    with pytest.raises(TaskDeferred) as deferred:
        _operator(max_docs=max_docs).restart_reindex(
            {}, restarts=1, created_before=7, deadline=time.time() + 60
        )

    reindex_call = es_conn.reindex.call_args.kwargs
    assert reindex_call["dest"] == {"index": "image-new-filtered", "op_type": "create"}
    assert reindex_call["conflicts"] == "proceed"
    assert reindex_call["max_docs"] == expected_max_docs
    assert deferred.value.method_name == "check_reindex"
    assert deferred.value.kwargs["es_task_id"] == "node:2"
    assert deferred.value.kwargs["created_before"] == 7


def test_restart_reindex_skips_when_max_docs_reached(monkeypatch):
    es_conn = mock.Mock()
    _hook(monkeypatch, es_conn)

    _operator(max_docs=7).restart_reindex(
        {}, restarts=1, created_before=7, deadline=time.time() + 60
    )

    es_conn.reindex.assert_not_called()


@pytest.mark.parametrize(
    "response, restarts",
    [
        pytest.param(_task_response(failures=[MAPPING_ERROR]), 0, id="not_retryable"),
        pytest.param(_task_response(error=REJECTED_SEARCH), 2, id="out_of_restarts"),
    ],
)
def test_wait_for_reindex_fails(monkeypatch, response, restarts):
    es_conn = mock.Mock()
    es_conn.tasks.get.return_value = response
    _hook(monkeypatch, es_conn)

    with pytest.raises(AirflowFailException, match="Reindex failed"):
        _operator(max_restarts=2).check_reindex(
            {},
            es_task_id="node:1",
            restarts=restarts,
            created_before=0,
            deadline=time.time() + 60,
        )


def test_wait_for_reindex_fails_after_deadline(monkeypatch):
    es_conn = mock.Mock()
    es_conn.tasks.get.return_value = _task_response(completed=False)
    _hook(monkeypatch, es_conn)

    with pytest.raises(AirflowFailException, match="did not finish"):
        _operator().check_reindex(
            {},
            es_task_id="node:1",
            restarts=0,
            created_before=0,
            deadline=time.time() - 1,
        )


@pytest.mark.parametrize(
    "exists, aliases, exist_ok, should_create",
    [
        pytest.param(False, {}, True, True, id="new_index"),
        pytest.param(True, {}, True, False, id="reuse_existing"),
        pytest.param(True, {}, False, True, id="existing_without_exist_ok"),
    ],
)
def test_create_index(monkeypatch, exists, aliases, exist_ok, should_create):
    es_conn = mock.Mock()
    es_conn.indices.exists.return_value = exists
    es_conn.indices.get_alias.return_value = {"image-new": {"aliases": aliases}}
    _hook(monkeypatch, es_conn)

    es.create_index.function({"index": "image-new"}, "http://es:9200", exist_ok)

    assert es_conn.indices.create.called is should_create


def test_create_index_does_not_reuse_aliased_index(monkeypatch):
    es_conn = mock.Mock()
    es_conn.indices.exists.return_value = True
    es_conn.indices.get_alias.return_value = {"image-new": {"aliases": {"image": {}}}}
    _hook(monkeypatch, es_conn)

    with pytest.raises(AirflowFailException, match="aliased by"):
        es.create_index.function({"index": "image-new"}, "http://es:9200", True)

    es_conn.indices.create.assert_not_called()


@pytest.mark.parametrize("data_nodes, expected_replicas", [(1, 0), (2, 1), (3, 1)])
def test_enable_replicas(monkeypatch, data_nodes, expected_replicas):
    es_conn = mock.Mock()
    es_conn.cluster.health.return_value = {"number_of_data_nodes": data_nodes}
    _hook(monkeypatch, es_conn)

    es.enable_replicas.function("http://es:9200", ["image-new", "image-new-filtered"])

    es_conn.indices.put_settings.assert_called_once_with(
        index="image-new,image-new-filtered",
        settings={"index": {"number_of_replicas": expected_replicas}},
    )


@pytest.mark.parametrize(
    "status, expected",
    [("green", True), ("yellow", False), ("red", False)],
)
def test_wait_for_green_indices(monkeypatch, status, expected):
    es_conn = mock.Mock()
    es_conn.cluster.health.return_value = {
        "status": status,
        "initializing_shards": 0,
        "unassigned_shards": 0,
    }
    _hook(monkeypatch, es_conn)

    assert (
        es.wait_for_green_indices.function("http://es:9200", ["image-new"]) is expected
    )
    es_conn.cluster.health.assert_called_once_with(index="image-new")
    es_conn.cluster.allocation_explain.assert_not_called()


def _unassigned_es_conn():
    es_conn = mock.Mock()
    es_conn.cluster.health.return_value = {
        "status": "yellow",
        "initializing_shards": 0,
        "unassigned_shards": 1,
    }
    es_conn.cat.shards.return_value = [
        {"index": "image-new", "shard": "0", "prirep": "p", "state": "STARTED"},
        {"index": "image-new", "shard": "3", "prirep": "r", "state": "UNASSIGNED"},
    ]
    return es_conn


def test_wait_for_green_indices_logs_why_a_shard_is_unassigned(monkeypatch, caplog):
    es_conn = _unassigned_es_conn()
    es_conn.cluster.allocation_explain.return_value = {
        "allocate_explanation": "cannot allocate",
        "node_allocation_decisions": [
            {"deciders": [{"explanation": "the node is above the high watermark"}]}
        ],
    }
    _hook(monkeypatch, es_conn)

    with caplog.at_level("INFO", logger="common.elasticsearch"):
        assert not es.wait_for_green_indices.function("http://es:9200", ["image-new"])

    es_conn.cluster.allocation_explain.assert_called_once_with(
        index="image-new", shard=3, primary=False
    )
    assert "the node is above the high watermark" in caplog.text


def test_wait_for_green_indices_survives_a_failed_explanation(monkeypatch):
    es_conn = _unassigned_es_conn()
    es_conn.cluster.allocation_explain.side_effect = ApiError(
        "no unassigned shard", mock.Mock(status=400), {}
    )
    _hook(monkeypatch, es_conn)

    assert not es.wait_for_green_indices.function("http://es:9200", ["image-new"])


DELETE_KWARGS = {
    "index": "image-new-filtered",
    "query": {"bool": {"should": [], "minimum_should_match": 1}},
    "requests_per_second": 20_000,
    "slices": "auto",
}


def _delete_operator():
    return WaitForDeleteByQueryOperator(
        task_id="wait_for_delete_by_query",
        es_host="http://es:9200",
        reindex={"es_task_id": "node:1", "kwargs": DELETE_KWARGS},
        reindex_timeout=timedelta(hours=1),
        poke_interval=60,
        max_restarts=2,
    )


def _delete_response(deleted, error=None):
    response = {
        "completed": True,
        "task": {"status": {"deleted": deleted, "version_conflicts": 0}},
        "response": {"failures": []},
    }
    if error:
        response["error"] = error
    return response


def test_wait_for_delete_by_query_restarts_after_overload(monkeypatch):
    es_conn = mock.Mock()
    es_conn.tasks.get.return_value = _delete_response(4, error=REJECTED_SEARCH)
    _hook(monkeypatch, es_conn)

    with pytest.raises(TaskDeferred) as deferred:
        _delete_operator().execute({})

    assert deferred.value.method_name == "restart_reindex"
    assert deferred.value.kwargs["created_before"] == 4


def test_restart_delete_by_query_starts_a_new_delete(monkeypatch):
    es_conn = mock.Mock()
    es_conn.delete_by_query.return_value = {"task": "node:2"}
    _hook(monkeypatch, es_conn)

    with pytest.raises(TaskDeferred) as deferred:
        _delete_operator().restart_reindex(
            {}, restarts=1, created_before=4, deadline=time.time() + 60
        )

    es_conn.reindex.assert_not_called()
    call = es_conn.delete_by_query.call_args.kwargs
    assert call["index"] == "image-new-filtered"
    assert call["query"] == DELETE_KWARGS["query"]
    assert call["conflicts"] == "proceed"
    assert call["wait_for_completion"] is False
    assert deferred.value.kwargs["es_task_id"] == "node:2"


def test_wait_for_delete_by_query_fails_with_its_group(monkeypatch):
    es_conn = mock.Mock()
    es_conn.tasks.get.return_value = _delete_response(0, error=MAPPING_ERROR)
    _hook(monkeypatch, es_conn)

    with pytest.raises(
        AirflowFailException,
        match="Delete by query failed.*trigger_and_wait_for_delete_by_query",
    ):
        _delete_operator().execute({})


@pytest.mark.parametrize(
    "counts, should_fail",
    [((10, 10), False), ((10, 0), True), ((10, 9), True)],
    ids=["same", "empty_filtered_index", "missing_documents"],
)
def test_assert_same_document_count(monkeypatch, counts, should_fail):
    es_conn = mock.Mock()
    es_conn.count.side_effect = [
        {"count": count, "_shards": _shards()} for count in counts
    ]
    _hook(monkeypatch, es_conn)

    if should_fail:
        with pytest.raises(AirflowFailException, match="documents, but"):
            es.assert_same_document_count.function(
                "http://es:9200", "image-new", "image-new-filtered"
            )
    else:
        assert (
            es.assert_same_document_count.function(
                "http://es:9200", "image-new", "image-new-filtered"
            )
            == 10
        )


def _shards(failed: int = 0) -> dict:
    failures = [{"shard": 3, "reason": {"type": "es_rejected_execution_exception"}}]
    return {
        "total": 18,
        "successful": 18 - failed,
        "skipped": 0,
        "failed": failed,
        **({"failures": failures * failed} if failed else {}),
    }


def test_assert_same_document_count_fails_on_failed_shards(monkeypatch):
    es_conn = mock.Mock()
    es_conn.count.side_effect = [
        {"count": 10, "_shards": _shards()},
        {"count": 9, "_shards": _shards(failed=1)},
    ]
    _hook(monkeypatch, es_conn)

    with pytest.raises(es.IncompleteResponseError, match="1 of 18 shards failed"):
        es.assert_same_document_count.function(
            "http://es:9200", "image-new", "image-new-filtered"
        )


def _source_count_response(failed: int = 0, sum_other_doc_count: int = 0) -> dict:
    return {
        "_shards": _shards(failed),
        "aggregations": {
            "unique_sources": {
                "sum_other_doc_count": sum_other_doc_count,
                "buckets": [
                    {"key": "flickr", "doc_count": 2500},
                    {"key": "stocksnap", "doc_count": 100},
                ],
            }
        },
    }


def test_get_record_count_group_by_sources(monkeypatch):
    es_conn = mock.Mock()
    es_conn.search.return_value = _source_count_response()
    _hook(monkeypatch, es_conn)

    counts = es.get_record_count_group_by_sources.function("http://es:9200", "image")

    assert counts == {"flickr": 2500, "stocksnap": 100}
    aggregation = es_conn.search.call_args.kwargs["body"]["aggs"]["unique_sources"]
    assert aggregation["terms"]["size"] == es.SOURCE_COUNT_BUCKETS


@pytest.mark.parametrize(
    "response, error, match",
    [
        pytest.param(
            _source_count_response(failed=3),
            es.IncompleteResponseError,
            "3 of 18 shards failed",
            id="failed_shards",
        ),
        pytest.param(
            _source_count_response(sum_other_doc_count=40),
            AirflowFailException,
            "40 documents were left out",
            id="more_sources_than_buckets",
        ),
    ],
)
def test_get_record_count_group_by_sources_fails_on_incomplete_counts(
    monkeypatch, response, error, match
):
    es_conn = mock.Mock()
    es_conn.search.return_value = response
    _hook(monkeypatch, es_conn)

    with pytest.raises(error, match=match):
        es.get_record_count_group_by_sources.function("http://es:9200", "image")

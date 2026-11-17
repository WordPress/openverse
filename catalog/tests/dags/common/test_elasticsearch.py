import time
from datetime import timedelta
from types import SimpleNamespace
from unittest import mock

import pytest
from airflow.sdk import timezone
from airflow.sdk.exceptions import AirflowFailException, TaskDeferred

from common import elasticsearch as es
from common.elasticsearch import (
    REINDEX_RESTART_BACKOFF,
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

import elastic_transport
import pytest

from indexer_worker import indexer
from indexer_worker.indexer import BulkUploadError, _bulk_upload


DOCS = [{"_index": "image-test", "_id": doc_id, "title": "x"} for doc_id in (1, 2, 3)]


def _item(doc_id, status):
    # Shaped like a bulk response item; `_id` comes back as a string
    return {"index": {"_index": "image-test", "_id": str(doc_id), "status": status}}


@pytest.fixture
def sleeps(monkeypatch):
    calls = []
    monkeypatch.setattr(indexer.time, "sleep", calls.append)
    return calls


@pytest.fixture
def bulk(monkeypatch):
    """
    Replace ``parallel_bulk`` with a fake that answers each call with the next
    scripted response: a dict of doc ID to status, or an exception to raise.
    """
    calls = []
    responses = []

    def fake_parallel_bulk(client, actions, **kwargs):
        actions = list(actions)
        calls.append([doc["_id"] for doc in actions])
        response = responses.pop(0)
        if isinstance(response, Exception):
            raise response
        for doc in actions:
            status = response.get(doc["_id"], 201)
            yield 200 <= status < 300, _item(doc["_id"], status)

    monkeypatch.setattr(indexer.helpers, "parallel_bulk", fake_parallel_bulk)
    return calls, responses


def test_bulk_upload_succeeds_first_time(bulk, sleeps):
    calls, responses = bulk
    responses.append({})

    _bulk_upload(None, DOCS)

    assert calls == [[1, 2, 3]]
    assert sleeps == []


def test_bulk_upload_retries_only_rejected_docs(bulk, sleeps):
    calls, responses = bulk
    responses.extend([{2: 429, 3: 503}, {3: 429}, {}])

    _bulk_upload(None, DOCS)

    assert calls == [[1, 2, 3], [2, 3], [3]]
    assert sleeps == [indexer.BULK_INITIAL_BACKOFF, indexer.BULK_INITIAL_BACKOFF * 2]


def test_bulk_upload_retries_all_docs_after_connection_error(bulk, sleeps):
    calls, responses = bulk
    responses.extend([elastic_transport.ConnectionTimeout("timed out"), {}])

    _bulk_upload(None, DOCS)

    assert calls == [[1, 2, 3], [1, 2, 3]]


def test_bulk_upload_fails_on_non_retryable_error(bulk, sleeps):
    calls, responses = bulk
    responses.append({2: 400})

    with pytest.raises(BulkUploadError, match="1 docs failed to index"):
        _bulk_upload(None, DOCS)

    assert len(calls) == 1


def test_bulk_upload_fails_when_rejections_outlast_retries(bulk, sleeps, monkeypatch):
    monkeypatch.setattr(indexer, "BULK_MAX_RETRIES", 2)
    calls, responses = bulk
    responses.extend([{1: 429}] * 3)

    with pytest.raises(BulkUploadError, match="still rejected 1 docs after 2 retries"):
        _bulk_upload(None, DOCS)

    assert calls == [[1, 2, 3], [1], [1]]


def test_bulk_upload_caps_backoff(bulk, sleeps, monkeypatch):
    monkeypatch.setattr(indexer, "BULK_MAX_BACKOFF", 12)
    calls, responses = bulk
    responses.extend([{1: 429}] * 3 + [{}])

    _bulk_upload(None, DOCS)

    assert sleeps == [5, 10, 12]

from unittest import mock

import elastic_transport
import pytest

from indexer_worker import indexer
from indexer_worker.indexer import BulkUploadError, _bulk_upload


DOCS = [{"_index": "image-test", "_id": doc_id, "title": "x"} for doc_id in (1, 2, 3)]


def _item(doc, status):
    # Shaped like a bulk response item; `_id` comes back as a string
    return {
        "index": {"_index": doc["_index"], "_id": str(doc["_id"]), "status": status}
    }


@pytest.fixture
def sleeps(monkeypatch):
    calls = []
    monkeypatch.setattr(indexer.time, "sleep", calls.append)
    return calls


@pytest.fixture
def bulk(monkeypatch):
    """
    Replace ``parallel_bulk`` with a fake that answers each call with the next
    scripted response: a dict of doc ID, or of (index, doc ID), to status, or an
    exception to raise.
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
            status = response.get(
                (doc["_index"], doc["_id"]), response.get(doc["_id"], 201)
            )
            yield 200 <= status < 300, _item(doc, status)

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


def test_bulk_upload_retries_the_rejected_copy_of_a_doc(monkeypatch, sleeps):
    sent = []

    def fake_parallel_bulk(client, actions, **kwargs):
        actions = list(actions)
        sent.append([doc["_index"] for doc in actions])
        for doc in actions:
            rejected = len(sent) == 1 and doc["_index"] == "image-test"
            yield not rejected, _item(doc, 429 if rejected else 201)

    monkeypatch.setattr(indexer.helpers, "parallel_bulk", fake_parallel_bulk)
    docs = [
        {"_index": index, "_id": 1, "title": "x"}
        for index in ("image-test", "image-test-filtered")
    ]

    _bulk_upload(None, docs)

    assert sent == [["image-test", "image-test-filtered"], ["image-test"]]


def _rows(*overrides):
    columns = [
        "id",
        "identifier",
        "title",
        "removed_from_source",
        "deleted",
    ]
    rows = [
        tuple(
            {"id": 1, "removed_from_source": False, "deleted": False, **o}.get(c)
            for c in columns
        )
        for o in overrides
    ]
    return rows, [(column,) for column in columns]


@pytest.mark.parametrize(
    "filtered_target_index, expected_indices",
    [
        (None, ["image-test"]),
        ("image-test-filtered", ["image-test", "image-test-filtered"]),
    ],
)
def test_pg_chunk_to_es_copies_docs_to_filtered_index(
    monkeypatch, filtered_target_index, expected_indices
):
    converted = mock.Mock()
    converted.to_dict.return_value = {"_index": "image", "_id": 1, "_source": {}}
    model = mock.Mock()
    model.database_row_to_elasticsearch_doc.return_value = converted
    monkeypatch.setitem(indexer.media_type_to_elasticsearch_model, "image", model)
    rows, columns = _rows({}, {"removed_from_source": True}, {"deleted": True})

    docs = indexer.pg_chunk_to_es(
        rows, columns, "image", "image-test", filtered_target_index
    )

    assert [doc["_index"] for doc in docs] == expected_indices
    assert all(doc["_id"] == 1 for doc in docs)

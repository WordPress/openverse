from collections.abc import Callable
from typing import Any

import aiohttp
import pook
import pytest
from elasticsearch_dsl.response import Hit
from structlog.testing import capture_logs

from api.utils.check_dead_links import HEADERS, check_dead_links
from test.factory.es_http import create_mock_es_http_image_hit


def _make_hits(
    count: int, gen_fields: Callable[[int], dict[str, Any]] = lambda _: dict()
):
    return [
        Hit(create_mock_es_http_image_hit(_id, "image", live=True, **gen_fields(_id)))
        for _id in range(40)
    ]


@pook.on
def test_sends_user_agent():
    query_hash = "test_sends_user_agent"
    results = _make_hits(40)
    start_slice = 0

    head_mock = (
        pook.head(pook.regex(r"https://example.com/openverse-live-image-result-url/\d"))
        .headers(HEADERS)
        .times(len(results))
        .reply(200)
        .mock
    )

    check_dead_links(query_hash, start_slice, results)

    assert head_mock.calls == len(results)
    requested_urls = [req.rawurl for req in head_mock.matches]
    for result in results:
        assert result.url in requested_urls


def test_handles_timeout(monkeypatch):
    query_hash = "test_handles_timeout"
    results = _make_hits(1)
    start_slice = 0

    async def raise_timeout_error(*args, **kwargs):
        raise aiohttp.ServerTimeoutError()

    monkeypatch.setattr(aiohttp.ClientSession, "_request", raise_timeout_error)
    with capture_logs() as logs:
        check_dead_links(query_hash, start_slice, results)

    # `check_dead_links` directly modifies the results list
    # if the results are timing out then they're considered dead and discarded
    # so should not appear in the final list of results.
    assert len(results) == 0

    # A timeout should not get logged as an error
    log_event = next((log for log in logs if log["log_level"] == "error"), None)
    assert log_event is None


def test_handles_error(monkeypatch):
    query_hash = "test_handles_timeout"
    results = _make_hits(1)
    start_slice = 0

    async def raise_nontimeout_error(*args, **kwargs):
        raise aiohttp.InvalidURL("https://invalid-url")

    monkeypatch.setattr(aiohttp.ClientSession, "_request", raise_nontimeout_error)
    with capture_logs() as logs:
        check_dead_links(query_hash, start_slice, results)

    # `check_dead_links` directly modifies the results list
    # if the results are erroring out then they're considered dead and discarded
    # so should not appear in the final list of results.
    assert len(results) == 0

    # A non-timeout exception should get logged as an error
    log_event = next((log for log in logs if log["log_level"] == "error"), None)
    assert log_event is not None


@pook.on
@pytest.mark.parametrize("provider", ("thingiverse", "flickr"))
def test_403_considered_dead(provider):
    query_hash = f"test_{provider}_403_considered_dead"
    other_provider = "fake_other_provider"
    results = _make_hits(
        4, lambda i: {"provider": provider if i % 2 else other_provider}
    )
    len_results = len(results)
    start_slice = 0

    head_mock = (
        pook.head(pook.regex(r"https://example.com/openverse-live-image-result-url/\d"))
        .times(len(results))
        .reply(403)
        .mock
    )

    check_dead_links(query_hash, start_slice, results)

    assert head_mock.calls == len_results

    # All the provider's results should be filtered out, leaving only the "other" provider
    assert all([r["provider"] == other_provider for r in results])


@pook.on
@pytest.mark.parametrize(
    "is_cache_reachable, cache_name",
    [(True, "redis"), (False, "unreachable_redis")],
)
def test_mset_and_expire_for_responses(is_cache_reachable, cache_name, request):
    cache = request.getfixturevalue(cache_name)

    query_hash = "test_mset_and_expiry_for_responses"
    results = _make_hits(40)
    start_slice = 0

    (
        pook.head(pook.regex(r"https://example.com/openverse-live-image-result-url/\d"))
        .headers(HEADERS)
        .times(len(results))
        .reply(200)
    )

    with capture_logs() as cap_logs:
        check_dead_links(query_hash, start_slice, results)

    if is_cache_reachable:
        for result in results:
            assert cache.get(f"valid:{result.url}") == b"200"
            # TTL is 30 days for 2xx responses
            assert cache.ttl(f"valid:{result.url}") == 2592000
    else:
        messages = [record["event"] for record in cap_logs]
        assert all(
            message in messages
            for message in [
                "Redis connect failed, validating all URLs without cache.",
                "Redis connect failed, cannot cache link liveness.",
            ]
        )


@pook.on
def test_unknown_status_log_names_the_checked_url():
    query_hash = "test_unknown_status_log_names_the_checked_url"
    results = [
        Hit(create_mock_es_http_image_hit("live", "image", live=True)),
        Hit(create_mock_es_http_image_hit("blocked", "image", live=True)),
    ]
    live_url, blocked_url = (result.url for result in results)
    pook.head(live_url).reply(200)
    pook.head(blocked_url).reply(429)

    with capture_logs() as cap_logs:
        check_dead_links(query_hash, 0, results)

    # A 429 is not a dead link, so both results are kept
    assert len(results) == 2
    warnings = [log["event"] for log in cap_logs if log["log_level"] == "warning"]
    assert len(warnings) == 1
    assert f"url={blocked_url} " in warnings[0]
    assert f"url={live_url} " not in warnings[0]


@pook.on
@pytest.mark.parametrize("index", ("image", "audio"))
def test_dead_link_logs_name_the_index(index):
    query_hash = f"test_dead_link_logs_name_the_index_{index}"
    results = [
        Hit(create_mock_es_http_image_hit("blocked", index, live=True)),
        Hit(create_mock_es_http_image_hit("dead", index, live=False)),
    ]
    blocked, dead = results
    pook.head(blocked.url).reply(429)
    pook.head(dead.url).reply(404)

    with capture_logs() as cap_logs:
        check_dead_links(query_hash, 0, results)

    assert results == [blocked]
    events = {log["log_level"]: log["event"] for log in cap_logs}
    # The messages are not specific to images, and name the index of the result
    # so that it can be found in the matching table.
    for level in ("warning", "info"):
        assert "image" not in events[level].split(" index=")[0].lower()
        assert f"index={index} " in events[level]
    assert f"id={dead['identifier']} " in events["info"]

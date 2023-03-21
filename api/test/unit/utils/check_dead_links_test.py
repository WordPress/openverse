import asyncio
from unittest import mock

import aiohttp
import pook

from catalog.api.utils.check_dead_links import HEADERS, check_dead_links


@mock.patch.object(aiohttp, "ClientSession", wraps=aiohttp.ClientSession)
@pook.on
def test_sends_user_agent(wrapped_client_session: mock.AsyncMock):
    query_hash = "test_sends_user_agent"
    results = [object() for _ in range(40)]
    image_urls = [f"https://example.org/{i}" for i in range(len(results))]
    start_slice = 0

    head_mock = (
        pook.head(pook.regex(r"https://example.org/\d"))
        .times(len(results))
        .reply(200)
        .mock
    )

    check_dead_links(query_hash, start_slice, results, image_urls)

    assert head_mock.calls == len(results)
    requested_urls = [req.rawurl for req in head_mock.matches]
    for url in image_urls:
        assert url in requested_urls

    wrapped_client_session.assert_called_once_with(headers=HEADERS, timeout=mock.ANY)


def test_handles_timeout():
    """
    Test that case where timeout occurs.

    Note: This test takes just over 3 seconds to run as it simulates network delay of
    3 seconds.
    """
    query_hash = "test_handles_timeout"
    results = [{"identifier": i} for i in range(1)]
    image_urls = [f"https://example.org/{i}" for i in range(len(results))]
    start_slice = 0

    def raise_timeout_error(*args, **kwargs):
        raise asyncio.TimeoutError()

    with mock.patch(
        "aiohttp.client.ClientSession._request", side_effect=raise_timeout_error
    ):
        check_dead_links(query_hash, start_slice, results, image_urls)

    # `check_dead_links` directly modifies the results list
    # if the results are timing out then they're considered dead and discarded
    # so should not appear in the final list of results.
    assert len(results) == 0


def test_thingiverse_403_considered_dead():
    query_hash = "test_thingiverse_403_considered_dead"
    results = [
        {"identifier": i, "provider": "thingiverse" if i % 2 else "flickr"}
        for i in range(4)
    ]
    image_urls = [f"https://example.org/{i}" for i in range(len(results))]
    start_slice = 0

    head_mock = (
        pook.head(pook.regex(r"https://example.org/\d"))
        .times(len(results))
        .reply(403)
        .mock
    )

    check_dead_links(query_hash, start_slice, results, image_urls)

    assert head_mock.calls == len(results)

    # All the "thingiverse" results should have been filtered out
    # whereas the flickr results should be left
    assert all([r["provider"] == "flickr" for r in results])

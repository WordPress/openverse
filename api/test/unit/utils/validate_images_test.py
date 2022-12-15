from unittest import mock

import aiohttp
import pook
import pytest
from fakeredis import FakeRedis

from catalog.api.utils.validate_images import HEADERS, validate_images


@pytest.fixture(autouse=True)
def redis(monkeypatch) -> FakeRedis:
    fake_redis = FakeRedis()

    def get_redis_connection(*args, **kwargs):
        return fake_redis

    monkeypatch.setattr("django_redis.get_redis_connection", get_redis_connection)

    yield fake_redis
    fake_redis.client().close()


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

    validate_images(query_hash, start_slice, results, image_urls)

    assert head_mock.calls == len(results)
    requested_urls = [req.rawurl for req in head_mock.matches]
    for url in image_urls:
        assert url in requested_urls

    wrapped_client_session.assert_called_once_with(headers=HEADERS)

from collections.abc import Callable
from dataclasses import dataclass

import pytest
from fakeredis import FakeRedis
from grequests import AsyncRequest
from requests import Response

from catalog.api.utils.validate_images import HEADERS, validate_images


@pytest.fixture(autouse=True)
def redis(monkeypatch) -> FakeRedis:
    fake_redis = FakeRedis()

    def get_redis_connection(*args, **kwargs):
        return fake_redis

    monkeypatch.setattr("django_redis.get_redis_connection", get_redis_connection)

    yield fake_redis
    fake_redis.client().close()


@dataclass
class GRequestsFixture:
    requests: list[AsyncRequest]
    response_factory: Callable[
        [AsyncRequest], Response
    ] = lambda x: GRequestsFixture._default_response_factory(x)

    @staticmethod
    def _default_response_factory(req: AsyncRequest) -> Response:
        res = Response()
        res.url = req.url
        res.status_code = 200
        return res


@pytest.fixture(autouse=True)
def grequests(monkeypatch) -> GRequestsFixture:
    fixture = GRequestsFixture([])

    def map_reqs(reqs, **kwargs):
        nonlocal fixture
        fixture.requests += list(reqs)
        responses = [fixture.response_factory(r) for r in fixture.requests]
        return responses

    monkeypatch.setattr("grequests.map", map_reqs)

    return fixture


def test_sends_user_agent(grequests):
    query_hash = "test_sends_user_agent"
    results = [object() for _ in range(40)]
    image_urls = [f"http://example.org/{i}" for i in range(len(results))]
    start_slice = 0

    validate_images(query_hash, start_slice, results, image_urls)

    requested_urls = [r.url for r in grequests.requests]
    for url in image_urls:
        assert url in requested_urls

    assert len(grequests.requests) > 0
    for r in grequests.requests:
        assert r.kwargs["headers"] == HEADERS

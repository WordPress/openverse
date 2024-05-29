from django.core.cache import caches

import pytest
from django_redis.cache import RedisCache
from fakeredis import FakeRedis, FakeServer


@pytest.fixture(autouse=True)
def redis(monkeypatch) -> FakeRedis:
    """Emulate a Redis connection that does not affect the real cache."""

    fake_redis = FakeRedis()

    def get_redis_connection(*args, **kwargs):
        return fake_redis

    monkeypatch.setattr("django_redis.get_redis_connection", get_redis_connection)
    yield fake_redis
    fake_redis.client().close()


@pytest.fixture
def unreachable_redis(monkeypatch) -> FakeRedis:
    """
    Emulate a broken Redis connection that does not affect the real cache.

    This fixture is useful for testing the resiliency of the API to withstand a
    Redis outage. Attempts to read/write to this Redis instance will raise
    ``ConnectionError``.
    """

    fake_server = FakeServer()
    fake_server.connected = False
    fake_redis = FakeRedis(server=fake_server)

    def get_redis_connection(*args, **kwargs):
        return fake_redis

    monkeypatch.setattr("django_redis.get_redis_connection", get_redis_connection)
    yield fake_redis
    fake_server.connected = True
    fake_redis.client().close()


@pytest.fixture(autouse=True)
def django_cache(redis) -> RedisCache:
    """Use the fake Redis fixture ``redis`` as Django's default cache."""

    original_default_cache = caches["default"]
    cache = RedisCache(" ", {})
    client = cache.client
    client._clients = [redis]
    caches["default"] = cache
    yield cache
    caches["default"] = original_default_cache


@pytest.fixture
def unreachable_django_cache(unreachable_redis) -> RedisCache:
    """
    Use the fake Redis fixture ``unreachable_redis`` as Django's default cache.

    This fixture is useful for testing the resiliency of the API to withstand a
    Redis outage. Attempts to read/write to this Redis instance will raise
    ``ConnectionError``.
    """

    original_default_cache = caches["default"]
    cache = RedisCache(" ", {})
    client = cache.client
    client._clients = [unreachable_redis]
    caches["default"] = unreachable_redis
    yield cache
    caches["default"] = original_default_cache

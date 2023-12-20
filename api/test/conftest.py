"""Fixtures usable by or necessary for both unit and integration tests."""

from test.fixtures.asynchronous import ensure_asgi_lifecycle, get_new_loop, session_loop
from test.fixtures.cache import (
    django_cache,
    redis,
    unreachable_django_cache,
    unreachable_redis,
)
from test.fixtures.rest_framework import api_client, request_factory


__all__ = [
    "ensure_asgi_lifecycle",
    "get_new_loop",
    "session_loop",
    "django_cache",
    "redis",
    "unreachable_django_cache",
    "unreachable_redis",
    "api_client",
    "request_factory",
]

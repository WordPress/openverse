"""Fixtures usable by or necessary for both unit and integration tests."""

from test.fixtures.asynchronous import ensure_asgi_lifecycle, get_new_loop, session_loop
from test.fixtures.cache import (
    django_cache,
    redis,
    unreachable_django_cache,
    unreachable_redis,
)
from test.fixtures.media_type_config import (
    audio_media_type_config,
    cleanup_elasticsearch_test_documents,
    image_media_type_config,
    media_type_config,
)
from test.fixtures.rest_framework import (
    access_token,
    anon_request,
    api_client,
    authed_request,
    request_factory,
)


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
    "access_token",
    "authed_request",
    "anon_request",
    "image_media_type_config",
    "audio_media_type_config",
    "media_type_config",
    "cleanup_elasticsearch_test_documents",
]

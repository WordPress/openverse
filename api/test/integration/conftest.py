from test.fixtures.asynchronous import ensure_asgi_lifecycle, session_loop
from test.fixtures.cache import (
    django_cache,
    redis,
    unreachable_django_cache,
    unreachable_redis,
)

import pytest


@pytest.fixture
def django_db_setup():
    """
    We want the integration tests to use the real database so that we can test
    the complete behaviour of the system. This fixture overrides the fixture
    from ``pytest-django`` that sets up the tests database and because it's a
    no-op, the tests will use the real database.
    """

    pass


__all__ = [
    "ensure_asgi_lifecycle",
    "session_loop",
    "django_cache",
    "redis",
    "unreachable_django_cache",
    "unreachable_redis",
]

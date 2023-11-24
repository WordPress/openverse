import pytest
from asgiref.sync import async_to_sync

from conf.asgi import application


@pytest.fixture(scope="session", autouse=True)
def ensure_asgi_lifecycle():
    """
    Call application shutdown lifecycle event.

    This cannot be an async fixture because the scope is session
    and pytest-asynio's `event_loop` fixture, which is auto-used
    for async tests and fixtures, is function scoped, which is
    incomatible with session scoped fixtures. `async_to_sync` works
    fine here, so it's not a problem.

    This cannot yet call the startup signal due to:
    https://github.com/illagrenan/django-asgi-lifespan/pull/80
    """
    scope = {"type": "lifespan"}

    async def noop(*args, **kwargs):
        ...

    async def shutdown():
        return {"type": "lifespan.shutdown"}

    yield
    async_to_sync(application)(scope, shutdown, noop)

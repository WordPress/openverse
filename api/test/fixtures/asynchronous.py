import asyncio

import pytest

from conf.asgi import application


@pytest.fixture
def get_new_loop():
    loops: list[asyncio.AbstractEventLoop] = []

    def _get_new_loop() -> asyncio.AbstractEventLoop:
        loop = asyncio.new_event_loop()
        loops.append(loop)
        return loop

    yield _get_new_loop

    for loop in loops:
        loop.close()


@pytest.fixture(scope="session")
def session_loop() -> asyncio.AbstractEventLoop:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def ensure_asgi_lifecycle(session_loop: asyncio.AbstractEventLoop):
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

    async def noop(*args, **kwargs): ...

    async def shutdown():
        return {"type": "lifespan.shutdown"}

    yield
    session_loop.run_until_complete(application(scope, shutdown, noop))

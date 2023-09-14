import pytest
from asgiref.sync import async_to_sync

from conf.asgi import application


@pytest.fixture(scope="session", autouse=True)
def call_application_shutdown():
    """
    Call application shutdown during test session teardown.

    This cannot be an async fixture because the scope is session
    and pytest-asynio's `event_loop` fixture, which is auto-used
    for async tests and fixtures, is function scoped, which is
    incomatible with session scoped fixtures. `async_to_sync` works
    fine here, so it's not a problem.
    """
    yield
    async_to_sync(application.shutdown)()

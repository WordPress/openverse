import pytest

from conf.wsgi import application


@pytest.fixture(scope="session", autouse=True)
def call_application_shutdown():
    yield
    application.shutdown()

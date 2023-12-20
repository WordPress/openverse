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

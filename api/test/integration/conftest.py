import socket
from urllib.parse import urlparse

from django.conf import settings

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


@pytest.fixture(autouse=True)
def no_external_hosts(monkeypatch):
    """
    Fail the test if it connects to a host outside the local stack.

    A request to a provider, such as a dead link check, makes the test depend
    on a third-party host that can be slow, rate-limited or down. Answer such
    requests with ``pook`` instead.
    """

    local_hosts = {
        "localhost",
        "127.0.0.1",
        "::1",
        urlparse(settings.ES_ENDPOINT).hostname,
    }
    external_hosts = set()
    getaddrinfo = socket.getaddrinfo

    def local_getaddrinfo(host, *args, **kwargs):
        if host not in local_hosts:
            external_hosts.add(host)
            raise socket.gaierror(socket.EAI_NONAME, f"{host} is not a local host")
        return getaddrinfo(host, *args, **kwargs)

    monkeypatch.setattr(socket, "getaddrinfo", local_getaddrinfo)
    yield
    assert not external_hosts, f"The test connected to {sorted(external_hosts)}"

import sys

from django.db.utils import OperationalError

import pytest
from psycopg_pool import PoolTimeout

from conf.settings.sentry import before_send


SSL_LOG_MESSAGE = (
    "Fatal error on SSL protocol\n"
    "protocol: <uvloop.loop.SSLProtocol object at 0x7fc2e0f5e820>\n"
    "transport: <TCPTransport closed=True reading=False 0x558f2baa0e70>"
)


def _exc_info(raise_exc):
    try:
        raise_exc()
    except Exception:
        return sys.exc_info()


def _raise_wrapped_pool_timeout():
    # Mirrors ``django.db.utils.DatabaseErrorWrapper``.
    try:
        raise PoolTimeout("couldn't get a connection after 10.00 sec")
    except PoolTimeout as exc:
        raise OperationalError(str(exc)) from exc


def _raise_operational_error():
    raise OperationalError("server closed the connection unexpectedly")


@pytest.mark.parametrize(
    "event, raise_exc",
    [
        pytest.param({}, _raise_wrapped_pool_timeout, id="pool_timeout"),
        pytest.param(
            {"logger": "asyncio", "message": SSL_LOG_MESSAGE},
            None,
            id="asyncio_ssl_log",
        ),
    ],
)
def test_drops_noise(event, raise_exc):
    hint = {"exc_info": _exc_info(raise_exc)} if raise_exc else {}

    assert before_send(event, hint) is None


@pytest.mark.parametrize(
    "event, raise_exc",
    [
        pytest.param({}, _raise_operational_error, id="other_db_error"),
        pytest.param(
            {"logger": "asyncio", "message": "Task exception was never retrieved"},
            None,
            id="other_asyncio_log",
        ),
        pytest.param(
            {"logger": "api.views", "message": SSL_LOG_MESSAGE},
            None,
            id="ssl_message_from_other_logger",
        ),
        pytest.param({"logger": "asyncio"}, None, id="asyncio_without_message"),
    ],
)
def test_keeps_other_events(event, raise_exc):
    hint = {"exc_info": _exc_info(raise_exc)} if raise_exc else {}

    assert before_send(event, hint) is event

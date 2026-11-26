from unittest.mock import MagicMock, patch

import pytest
from requests import Response
from requests.exceptions import ConnectionError, HTTPError

from common.retries import retry_on_exceptions, retry_on_http_status


@pytest.fixture(autouse=True)
def no_sleep():
    with patch("time.sleep") as sleep:
        yield sleep


def _http_error(status_code: int) -> HTTPError:
    response = Response()
    response.status_code = status_code
    return HTTPError(response=response)


@pytest.mark.parametrize("status_code", [502, 503, 504])
def test_retry_on_http_status_retries_server_errors(status_code):
    func = MagicMock(side_effect=[_http_error(status_code), "ok"])

    assert retry_on_http_status(max_time=60)(func)() == "ok"
    assert func.call_count == 2


@pytest.mark.parametrize("status_code", [400, 404, 500])
def test_retry_on_http_status_raises_other_errors_immediately(status_code):
    func = MagicMock(side_effect=_http_error(status_code))

    with pytest.raises(HTTPError):
        retry_on_http_status(max_time=60)(func)()
    assert func.call_count == 1


def test_retry_on_http_status_uses_custom_status_codes():
    func = MagicMock(side_effect=[_http_error(400), "ok"])

    assert retry_on_http_status(max_time=60, status_codes={400})(func)() == "ok"


def test_retry_on_http_status_raises_http_error_without_response():
    func = MagicMock(side_effect=HTTPError())

    with pytest.raises(HTTPError):
        retry_on_http_status(max_time=60)(func)()
    assert func.call_count == 1


def test_retry_on_http_status_reraises_last_error_after_max_time():
    func = MagicMock(side_effect=_http_error(503))

    with pytest.raises(HTTPError):
        retry_on_http_status(max_time=0)(func)()
    assert func.call_count == 1


def test_retry_on_exceptions_stops_after_max_tries():
    func = MagicMock(side_effect=ConnectionError())

    with pytest.raises(ConnectionError):
        retry_on_exceptions((ConnectionError,), max_tries=3)(func)()
    assert func.call_count == 3


def test_retry_on_exceptions_does_not_retry_other_exceptions():
    func = MagicMock(side_effect=KeyError())

    with pytest.raises(KeyError):
        retry_on_exceptions(ValueError, max_tries=3)(func)()
    assert func.call_count == 1


def test_retry_on_exceptions_returns_after_recovering(no_sleep):
    func = MagicMock(side_effect=[ValueError(), ValueError(), "ok"])

    assert retry_on_exceptions(ValueError, max_tries=3)(func)() == "ok"
    assert no_sleep.call_count == 2

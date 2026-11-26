import pytest
from requests import Response
from requests.exceptions import ConnectionError, HTTPError, SSLError

from common.retries import retry_on_exceptions, retry_on_http_status


@pytest.fixture(autouse=True)
def skip_waits(monkeypatch):
    # The decorators wait for up to several seconds between attempts.
    monkeypatch.setattr("time.sleep", lambda seconds: None)


def http_error(status_code: int | None = None) -> HTTPError:
    if status_code is None:
        return HTTPError()
    response = Response()
    response.status_code = status_code
    return HTTPError(response=response)


class Flaky:
    """Raise each of ``errors`` on successive calls, then return ``"ok"``."""

    def __init__(self, *errors: BaseException):
        self.errors = list(errors)
        self.calls = 0

    def __call__(self):
        self.calls += 1
        if self.errors:
            raise self.errors.pop(0)
        return "ok"


@pytest.mark.parametrize(
    "decorator, errors",
    [
        pytest.param(retry_on_http_status(max_time=60), [http_error(502)], id="502"),
        pytest.param(retry_on_http_status(max_time=60), [http_error(503)], id="503"),
        pytest.param(
            retry_on_http_status(max_time=60),
            [http_error(504), http_error(503), http_error(502)],
            id="several-server-errors",
        ),
        pytest.param(
            retry_on_http_status(max_time=60, status_codes={400}),
            [http_error(400)],
            id="custom-status-code",
        ),
        pytest.param(
            retry_on_exceptions(ValueError, max_tries=3),
            [ValueError(), ValueError()],
            id="exception-within-max-tries",
        ),
        pytest.param(
            retry_on_exceptions((SSLError, ConnectionError), max_tries=3),
            [SSLError(), ConnectionError()],
            id="any-of-several-exceptions",
        ),
    ],
)
def test_retries_until_the_call_succeeds(decorator, errors):
    func = Flaky(*errors)

    assert decorator(func)() == "ok"
    assert func.calls == len(errors) + 1


@pytest.mark.parametrize(
    "decorator, error",
    [
        pytest.param(retry_on_http_status(max_time=60), http_error(400), id="400"),
        pytest.param(retry_on_http_status(max_time=60), http_error(404), id="404"),
        pytest.param(retry_on_http_status(max_time=60), http_error(500), id="500"),
        pytest.param(
            retry_on_http_status(max_time=60, status_codes={400}),
            http_error(503),
            id="status-code-not-in-custom-codes",
        ),
        pytest.param(
            retry_on_http_status(max_time=60), http_error(), id="http-error-no-response"
        ),
        pytest.param(retry_on_http_status(max_time=60), ValueError(), id="not-http"),
        pytest.param(
            retry_on_exceptions(ValueError, max_tries=3),
            KeyError(),
            id="exception-not-listed",
        ),
    ],
)
def test_raises_other_errors_without_retrying(decorator, error):
    func = Flaky(error)

    with pytest.raises(type(error)) as exc_info:
        decorator(func)()

    assert exc_info.value is error
    assert func.calls == 1


@pytest.mark.parametrize("max_tries", [1, 3])
def test_retry_on_exceptions_raises_the_last_error_after_max_tries(max_tries):
    errors = [ConnectionError(f"attempt {n}") for n in range(max_tries + 1)]
    func = Flaky(*errors)

    with pytest.raises(ConnectionError) as exc_info:
        retry_on_exceptions(ConnectionError, max_tries=max_tries)(func)()

    assert exc_info.value is errors[max_tries - 1]
    assert func.calls == max_tries


def test_retry_on_http_status_raises_the_error_once_max_time_has_passed():
    error = http_error(503)
    func = Flaky(error, http_error(503))

    with pytest.raises(HTTPError) as exc_info:
        retry_on_http_status(max_time=0)(func)()

    assert exc_info.value is error
    assert func.calls == 1

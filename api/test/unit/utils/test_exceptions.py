from rest_framework.exceptions import NotFound

import pytest
from elastic_transport import ConnectionError as ESConnectionError
from elastic_transport import ConnectionTimeout

from api.utils.es_transport import SearchCapacityExceeded
from api.utils.exceptions import exception_handler


@pytest.mark.parametrize(
    "ex, status_code",
    [
        (SearchCapacityExceeded("no socket free"), 503),
        (ConnectionTimeout("Connection timed out"), 504),
        (ESConnectionError("connection refused"), 503),
    ],
)
def test_search_backend_failures_are_not_server_errors(ex, status_code):
    res = exception_handler(ex, {})

    assert res.status_code == status_code
    assert res["Retry-After"] == "5"
    assert "retry" in res.data["detail"]


def test_other_exceptions_are_left_to_drf():
    res = exception_handler(NotFound(), {})

    assert res.status_code == 404

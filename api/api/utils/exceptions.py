from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

import structlog
from elastic_transport import ConnectionError as ESConnectionError
from elastic_transport import ConnectionTimeout

from api.utils.es_transport import SearchCapacityExceeded


logger = structlog.get_logger(__name__)

# Elasticsearch failing to answer is a backend outage the client can only wait
# out, so it is reported as one. Answering here also keeps these out of Sentry,
# which otherwise receives one 500 per timed-out search.
SEARCH_BACKEND_FAILURES = {
    SearchCapacityExceeded: (
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "Search is over capacity, please retry shortly.",
    ),
    ConnectionTimeout: (
        status.HTTP_504_GATEWAY_TIMEOUT,
        "Search timed out, please retry shortly.",
    ),
    ESConnectionError: (
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "Search is temporarily unavailable, please retry shortly.",
    ),
}


def exception_handler(ex, context):
    """
    Handle the exception raised in a DRF context.

    See `DRF docs`_.
    .. _DRF docs: https://www.django-rest-framework.org/api-guide/exceptions/#custom-exception-handling

    :param ex: the exception that has occurred
    :param context: additional data about the context of the exception
    :return: the response to show for the exception
    """  # noqa: E501

    for exc_type, (status_code, detail) in SEARCH_BACKEND_FAILURES.items():
        if isinstance(ex, exc_type):
            logger.warning(
                "Search backend failure", exc_type=type(ex).__name__, status=status_code
            )
            return Response(
                {"detail": detail},
                status=status_code,
                headers={"Retry-After": "5"},
            )

    res = drf_exception_handler(ex, context)
    if isinstance(ex, ValidationError):
        # Wrap validation errors inside a `detail` key for consistency
        res.data = {"detail": res.data}
    return res

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from api.utils.es_transport import SearchCapacityExceeded


def exception_handler(ex, context):
    """
    Handle the exception raised in a DRF context.

    See `DRF docs`_.
    .. _DRF docs: https://www.django-rest-framework.org/api-guide/exceptions/#custom-exception-handling

    :param ex: the exception that has occurred
    :param context: additional data about the context of the exception
    :return: the response to show for the exception
    """  # noqa: E501

    if isinstance(ex, SearchCapacityExceeded):
        return Response(
            {"detail": "Search is over capacity, please retry shortly."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
            headers={"Retry-After": "5"},
        )

    res = drf_exception_handler(ex, context)
    if isinstance(ex, ValidationError):
        # Wrap validation errors inside a `detail` key for consistency
        res.data = {"detail": res.data}
    return res

from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler as drf_exception_handler


def exception_handler(ex, context):
    """
    Handle the exception raised in a DRF context.

    See `DRF docs`_.
    .. _DRF docs: https://www.django-rest-framework.org/api-guide/exceptions/#custom-exception-handling

    :param ex: the exception that has occurred
    :param context: additional data about the context of the exception
    :return: the response to show for the exception
    """  # noqa: E501

    res = drf_exception_handler(ex, context)
    if isinstance(ex, ValidationError):
        # Wrap validation errors inside a `detail` key for consistency
        res.data = {"detail": res.data}
    return res

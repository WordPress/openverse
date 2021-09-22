from rest_framework.serializers import ValidationError
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler as drf_exception_handler


def get_api_exception(error_message, response_code=500, error_code=None):
    """
    Returns an instance of a subclass of ``APIException`` with the given error
    message, error code and response status code.

    The returned object should be used with the ``raise`` keyword.

    :param error_message: the detailed error message shown to the user
    :param response_code: the HTTP response status code
    :param error_code: the codename of the error
    :return: an instance of a subclass of ``APIException``
    """

    class SubAPIException(APIException):
        status_code = response_code
        default_detail = error_message
        default_code = error_code
    return SubAPIException()


def exception_handler(ex, context):
    """
    Handle the exception raised in a DRF context. See `DRF docs`_.
    .. _DRF docs: https://www.django-rest-framework.org/api-guide/exceptions/#custom-exception-handling  # noqa: E501

    :param ex: the exception that has occurred
    :param context: additional data about the context of the exception
    :return: the response to show for the exception
    """

    res = drf_exception_handler(ex, context)
    if isinstance(ex, ValidationError):
        # Wrap validation errors inside a `detail` key for consistency
        res.data = {
            'detail': res.data
        }
    return res

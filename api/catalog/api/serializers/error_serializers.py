"""
These serializers handle error responses sent by API endpoints.

Reference for exception handling in Django REST Framework:
    https://www.django-rest-framework.org/api-guide/exceptions/
"""

from rest_framework import serializers


class InputErrorSerializer(serializers.Serializer):
    """Returned if invalid query parameters are passed."""

    detail = serializers.DictField(
        help_text="Mapping of field names with errors from to that field.",
        child=serializers.ListField(child=serializers.CharField()),
    )


class NotFoundErrorSerializer(serializers.Serializer):
    """Returned if the requested content could not be found."""

    detail = serializers.CharField(help_text="The description for error.")


class ForbiddenErrorSerializer(serializers.Serializer):
    """Returned if access to requested content is forbidden."""

    detail = serializers.CharField(help_text="The description for error.")


class InternalServerErrorSerializer(serializers.Serializer):
    """Returned if the request could not be processed."""

    detail = serializers.CharField(help_text="The description for error.")

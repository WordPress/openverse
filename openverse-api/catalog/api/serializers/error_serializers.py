from rest_framework import serializers


class InputErrorSerializer(serializers.Serializer):
    """ Returned if invalid query parameters are passed. """
    error = serializers.CharField(
        help_text="The name of error."
    )
    detail = serializers.CharField(
        help_text="The description for error."
    )
    fields = serializers.ListField(
        help_text="List of query parameters that causes error."
    )


class NotFoundErrorSerializer(serializers.Serializer):
    """ Returned if the requested content could not be found. """
    detail = serializers.CharField(
        help_text="The description for error"
    )


class ForbiddenErrorSerializer(serializers.Serializer):
    """ Returned if access to requested content is forbidden for
    some reason."""
    detail = serializers.CharField(
        help_text="The description for error"
    )


class InternalServerErrorSerializer(serializers.Serializer):
    """ Returned if the request could not be processed by the server for an
    unknown reason."""
    detail = serializers.CharField(
        help_text="The description for error"
    )

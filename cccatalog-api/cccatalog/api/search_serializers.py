from rest_framework import serializers
from cccatalog.api.licenses import LICENSE_GROUPS
from cccatalog.api.search_controller import get_providers


class _SearchQueryStringSerializer(serializers.Serializer):
    """ Base class for search query parameters. """

    """ Parse and validate search query string parameters. """
    q = serializers.CharField(
        label="query",
        help_text="A comma-separated list of keywords. Should not exceed 200 "
                  "characters in length. Example: `hello,world`",
    )
    li = serializers.CharField(
        label="licenses",
        help_text="A comma-separated list of licenses. Example: `by,cc0`."
                  " Valid inputs: `{}`".format(list(LICENSE_GROUPS['all'])),
        required=False,
    )
    lt = serializers.CharField(
        label="license type",
        help_text="A list of license types. "
                  "Valid inputs: `{}`".format((list(LICENSE_GROUPS.keys()))),
        required=False,
    )

    provider = serializers.CharField(
        label="provider",
        help_text="A comma separated list of data sources to search.",
        required=False
    )

    page = serializers.IntegerField(
        label="page number",
        help_text="The page number to retrieve.",
        default=1
    )
    pagesize = serializers.IntegerField(
        label="page size",
        help_text="The number of results to return in the requested page. "
                  "Should be an integer between 1 and 500.",
        default=20
    )

    def validate(self, data):
        if 'li' in data and 'lt' in data:
            raise serializers.ValidationError(
                "Only license type or individual licenses can be defined, not "
                "both."
            )
        else:
            return data

    def validate_q(self, value):
        if len(value) > 200:
            return value[0:199]
        else:
            return value

    def validate_li(self, value):
        licenses = [x.upper() for x in value.split(',')]
        for _license in licenses:
            if _license not in LICENSE_GROUPS['all']:
                raise serializers.ValidationError(
                    "License \'{}\' does not exist.".format(_license)
                )
        return value.lower().split(',')

    def validate_lt(self, value):
        """
        Resolves a license type to a list of licenses.
        Example: commercial -> ['BY', 'BY-SA', 'BY-ND', 'CC0', 'PDM']
        """
        license_types = [x.lower() for x in value.split(',')]
        resolved_licenses = set()
        for _type in license_types:
            if _type not in LICENSE_GROUPS:
                raise serializers.ValidationError(
                    "License type \'{}\' does not exist.".format(_type)
                )
            licenses = LICENSE_GROUPS[_type]
            for _license in licenses:
                resolved_licenses.add(_license.lower())

        return ','.join(list(resolved_licenses))

    def validate_page(self, value):
        if value < 1:
            return 1
        else:
            return value

    def validate_pagesize(self, value):
        if 1 <= value < 500:
            return value
        else:
            return 20


class ImageSearchQueryStringSerializer(_SearchQueryStringSerializer):
    """ Query parameters specific to image search."""
    provider = serializers.CharField(
        label="provider",
        help_text="A comma separated list of data sources to search. Valid "
                  "inputs:"
                  " `{}`".format(get_providers('image')),
        required=False
    )

    def validate_provider(self, value):
        allowed_providers = get_providers('image')
        if value not in allowed_providers:
            raise serializers.ValidationError(
                "Provider \'{}\' does not exist.".format(value)
            )
        else:
            return value.lower()


class ElasticsearchImageResultSerializer(serializers.Serializer):
    """ A single Elasticsearch result."""
    title = serializers.CharField(required=False)
    identifier = serializers.CharField(required=False)
    creator = serializers.CharField(required=False, allow_blank=True)
    creator_url = serializers.URLField(required=False)
    tags = serializers.ListField(required=False)
    url = serializers.URLField()
    thumbnail = serializers.URLField(required=False, allow_blank=True)
    provider = serializers.CharField(required=False)
    source = serializers.CharField(required=False)
    license = serializers.CharField()
    license_version = serializers.CharField(required=False)
    foreign_landing_url = serializers.URLField(required=False)
    meta_data = serializers.CharField(required=False)


class ImageSearchResultSerializer(serializers.Serializer):
    """ The full image search response. """
    result_count = serializers.IntegerField()
    page_count = serializers.IntegerField()
    results = ElasticsearchImageResultSerializer(many=True)


class ValidationErrorSerializer(serializers.Serializer):
    """ Returned if invalid query parameters are passed. """
    validation_error = serializers.JSONField()


class InternalServerErrorSerializer(serializers.Serializer):
    """ Serializer for error 500"""
    internal_server_error = serializers.JSONField()

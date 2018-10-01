from rest_framework import serializers
from cccatalog.api.licenses import LICENSE_GROUPS
from cccatalog.api.controllers.search_controller import get_providers


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
    creator = serializers.CharField(
        label="creator",
        help_text="Filter results so that only those by a certain author will"
                  " appear.",
        required=False
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
        return value.lower()

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

    def validate_creator(self, value):
        if len(value) <= 2000:
            return value
        else:
            raise serializers.ValidationError(
                "Creator query exceeds 2000 characters."
            )

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
                  " `{}`".format(list(get_providers('image').keys())),
        required=False
    )

    def validate_provider(self, input_providers):
        allowed_providers = list(get_providers('image').keys())

        for input_provider in input_providers.split(','):
            if input_provider not in allowed_providers:
                raise serializers.ValidationError(
                    "Provider \'{}\' does not exist.".format(input_providers)
                )
        return input_providers.lower()


class TagSerializer(serializers.Serializer):
    name = serializers.CharField(
        required=True,
        help_text="The name of a detailed tag."
    )
    accuracy = serializers.FloatField(
        required=False,
        help_text="The accuracy of a machine-generated tag. Human-generated "
                  "tags do not have an accuracy field."
    )


class ImageSerializer(serializers.Serializer):
    """ A single image. Used in search results."""
    title = serializers.CharField(required=False)
    identifier = serializers.CharField(required=False)
    creator = serializers.CharField(required=False, allow_blank=True)
    creator_url = serializers.URLField(required=False)
    legacy_tags = serializers.ListField(required=False)
    tags = TagSerializer(
        required=False,
        many=True,
        help_text="Tags with detailed metadata, such as accuracy."
    )
    url = serializers.URLField()
    thumbnail = serializers.URLField(required=False, allow_blank=True)
    provider = serializers.CharField(required=False)
    source = serializers.CharField(required=False)
    license = serializers.CharField()
    license_version = serializers.CharField(required=False)
    foreign_landing_url = serializers.URLField(required=False)
    meta_data = serializers.CharField(required=False)
    id = serializers.IntegerField(
        required=True,
        help_text="The unique identifier of the image."
    )
    detail = serializers.URLField(
        required=True,
        help_text="A direct link to the detail view of an image."
    )


class ImageSearchResultsSerializer(serializers.Serializer):
    """ The full image search response. """
    result_count = serializers.IntegerField()
    page_count = serializers.IntegerField()
    results = ImageSerializer(many=True)


class ValidationErrorSerializer(serializers.Serializer):
    """ Returned if invalid query parameters are passed. """
    validation_error = serializers.JSONField()

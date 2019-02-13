from rest_framework import serializers
from cccatalog.api.licenses import LICENSE_GROUPS
from cccatalog.api.controllers.search_controller import get_providers


class ImageSearchQueryStringSerializer(serializers.Serializer):
    """ Base class for search query parameters. """

    """ Parse and validate search query string parameters. """
    q = serializers.CharField(
        label="query",
        help_text="A comma-separated list of keywords. Should not exceed 200 "
                  "characters in length. Example: `hello,world`",
        required=False,
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
        help_text="Search by creator.",
        required=False,
        max_length=200
    )
    tags = serializers.CharField(
        label="tags",
        help_text="Search by tag.",
        required=False,
        max_length=200
    )
    title = serializers.CharField(
        label="title",
        help_text="Search by title.",
        required=False,
        max_length=200
    )
    filter_dead = serializers.BooleanField(
        label="filter_dead",
        help_text="Control whether 404 links are filtered out.",
        required=False,
        default=True
    )
    provider = serializers.CharField(
        label="provider",
        help_text="A comma separated list of data sources to search. Valid "
                  "inputs:"
                  " `{}`".format(list(get_providers('image').keys())),
        required=False
    )

    def validate_q(self, value):
        if len(value) > 200:
            return value[0:199]
        else:
            return value

    def validate_creator(self, value):
        return self.validate_q(value)

    def validate_tags(self, value):
        return self.validate_q(value)

    def validate_title(self, value):
        return self.validate_q(value)

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

    def validate_provider(self, input_providers):
        allowed_providers = list(get_providers('image').keys())

        for input_provider in input_providers.split(','):
            if input_provider not in allowed_providers:
                raise serializers.ValidationError(
                    "Provider \'{}\' does not exist.".format(input_providers)
                )
        return input_providers.lower()

    def validate(self, data):
        advanced_search = 'creator' in data or 'title' in data or 'tags' in data
        if 'q' in data and advanced_search:
            raise serializers.ValidationError(
                "You cannot use `q` in combination with advanced search "
                "parameters `title`, `tags`, or `creator`."
            )
        elif 'li' in data and 'lt' in data:
            raise serializers.ValidationError(
                "Only license type or individual licenses can be defined, not "
                "both."
            )
        else:
            return data


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
    id = serializers.CharField(
        required=True,
        help_text="The unique identifier for the image.",
        source='identifier'
    )
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

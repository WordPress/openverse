from rest_framework import serializers
from cccatalog.api.licenses import LICENSE_GROUPS
from cccatalog.api.controllers.search_controller import get_providers


def _validate_page(value):
    if value < 1:
        return 1
    else:
        return value


def _validate_pagesize(value):
    if 1 <= value < 500:
        return value
    else:
        return 20


def _validate_lt(value):
    license_types = [x.lower() for x in value.split(',')]
    license_groups = []
    for _type in license_types:
        if _type not in LICENSE_GROUPS:
            raise serializers.ValidationError(
                "License type \'{}\' does not exist.".format(_type)
            )
        license_groups.append(LICENSE_GROUPS[_type])
    intersected = set.intersection(*license_groups)
    cleaned = {_license.lower() for _license in intersected}

    return ','.join(list(cleaned))


def _validate_li(value):
    licenses = [x.upper() for x in value.split(',')]
    for _license in licenses:
        if _license not in LICENSE_GROUPS['all']:
            raise serializers.ValidationError(
                "License \'{}\' does not exist.".format(_license)
            )
    return value.lower()


class BrowseImageQueryStringSerializer(serializers.Serializer):
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
    filter_dead = serializers.BooleanField(
        label="filter_dead",
        help_text="Control whether 404 links are filtered out.",
        required=False,
        default=True
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

    @staticmethod
    def validate_page(value):
        return _validate_page(value)

    @staticmethod
    def validate_pagesize(value):
        return _validate_pagesize(value)

    @staticmethod
    def validate_li(value):
        return _validate_li(value)

    @staticmethod
    def validate_lt(value):
        """
        Resolves a list of license types to a list of licenses.
        Example: commercial -> ['BY', 'BY-SA', 'BY-ND', 'CC0', 'PDM']
        """
        return _validate_lt(value)

    def validate(self, data):
        if 'li' in data and 'lt' in data:
            raise serializers.ValidationError(
                "Only license type or individual licenses can be defined, not "
                "both."
            )
        else:
            return data


class ImageSearchQueryStringSerializer(serializers.Serializer):
    """ Base class for search query parameters. """

    """ Parse and validate search query string parameters. """
    q = serializers.CharField(
        label="query",
        help_text="A query string that should not exceed 200 characters in "
                  "length",
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
        help_text="Search by creator only. Cannot be used with `q`.",
        required=False,
        max_length=200
    )
    tags = serializers.CharField(
        label="tags",
        help_text="Search by tag only. Cannot be used with `q`.",
        required=False,
        max_length=200
    )
    title = serializers.CharField(
        label="title",
        help_text="Search by title only. Cannot be used with `q`.",
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
    extension = serializers.CharField(
        label="extension",
        help_text="Filter by file extension, such as JPG or GIF.",
        required=False
    )
    qa = serializers.BooleanField(
        label='quality_assurance',
        help_text="If enabled, searches are performed against the quality"
                  " assurance index instead of production.",
        required=False,
        default=False
    )

    @staticmethod
    def validate_q(value):
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

    @staticmethod
    def validate_li(value):
        return _validate_li(value)

    @staticmethod
    def validate_lt(value):
        """
        Resolves a list of license types to a list of licenses.
        Example: commercial -> ['BY', 'BY-SA', 'BY-ND', 'CC0', 'PDM']
        """
        return _validate_lt(value)

    @staticmethod
    def validate_page(value):
        return _validate_page(value)

    @staticmethod
    def validate_pagesize(value):
        if 1 <= value <= 500:
            return value
        else:
            return 20

    @staticmethod
    def validate_provider(input_providers):
        allowed_providers = list(get_providers('image').keys())

        for input_provider in input_providers.split(','):
            if input_provider not in allowed_providers:
                raise serializers.ValidationError(
                    "Provider \'{}\' does not exist.".format(input_providers)
                )
        return input_providers.lower()

    @staticmethod
    def validate_extension(value):
        return value.lower()

    def validate(self, data):
        advanced_search = 'creator' in data or 'title' in data or 'tags' in data
        if 'q' in data and advanced_search:
            raise serializers.ValidationError(
                "You cannot use `q` in combination with advanced search "
                "parameters `title`, `tags`, or `creator`."
            )
        elif 'q' not in data and not advanced_search:
            raise serializers.ValidationError(
                "You must use either the `q` parameter or an advanced search"
                "parameter such as `title`, `tags`, or `creator`."
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
    fields_matched = serializers.ListField(
        required=False,
        help_text="List the fields that matched the query for this result."
    )
    height = serializers.IntegerField(
        required=False,
        help_text="The height of the image in pixels. Not always available."
    )
    width = serializers.IntegerField(
        required=False,
        help_text="The width of the image in pixels. Not always available."
    )


class RelatedImagesResultsSerializer(serializers.Serializer):
    result_count = serializers.IntegerField(),
    results = ImageSerializer(many=True)


class ImageSearchResultsSerializer(serializers.Serializer):
    """ The full image search response. """
    result_count = serializers.IntegerField()
    page_count = serializers.IntegerField()
    results = ImageSerializer(many=True)


class ValidationErrorSerializer(serializers.Serializer):
    """ Returned if invalid query parameters are passed. """
    validation_error = serializers.JSONField()

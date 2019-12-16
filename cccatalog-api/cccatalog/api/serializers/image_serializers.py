import cccatalog.api.licenses as license_helpers
from rest_framework import serializers
from cccatalog.api.licenses import LICENSE_GROUPS, get_license_url
from urllib.parse import urlparse
from collections import namedtuple
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
        if _type not in license_helpers.LICENSE_GROUPS:
            raise serializers.ValidationError(
                "License type \'{}\' does not exist.".format(_type)
            )
        license_groups.append(license_helpers.LICENSE_GROUPS[_type])
    intersected = set.intersection(*license_groups)
    cleaned = {_license.lower() for _license in intersected}

    return ','.join(list(cleaned))


def _validate_enum(enum_name, valid_values: set, given_values: str):
    """
    :param valid_values: Allowed values for an enum
    :param given_values: A comma separated list of values.
    :return: whether the input is valid
    """
    input_values = [x.lower() for x in given_values.split(',')]
    for value in input_values:
        if value not in valid_values:
            raise serializers.ValidationError(
                f'Invalid {enum_name}: {value}.'
                f' Available options: {valid_values}'
            )
    return given_values.lower()


def _validate_li(value):
    licenses = [x.upper() for x in value.split(',')]
    for _license in licenses:
        if _license not in license_helpers.LICENSE_GROUPS['all']:
            raise serializers.ValidationError(
                "License \'{}\' does not exist.".format(_license)
            )
    return value.lower()


class ImageSearchQueryStringSerializer(serializers.Serializer):
    """ Parse and validate search query string parameters. """
    DeprecatedParam = namedtuple('DeprecatedParam', ['original', 'successor'])
    deprecated_params = [
        DeprecatedParam('li', 'license'),
        DeprecatedParam('lt', 'license_type'),
        DeprecatedParam('pagesize', 'page_size'),
        DeprecatedParam('provider', 'source')
    ]

    q = serializers.CharField(
        label="query",
        help_text="A query string that should not exceed 200 characters in "
                  "length",
        required=False,
    )
    license = serializers.CharField(
        label="licenses",
        help_text="A comma-separated list of licenses. Example: `by,cc0`."
                  " Valid inputs: `{}`"
                  .format(list(license_helpers.LICENSE_GROUPS['all'])),
        required=False,
    )
    license_type = serializers.CharField(
        label="license type",
        help_text="A list of license types. "
                  "Valid inputs: `{}`"
                  .format((list(license_helpers.LICENSE_GROUPS.keys()))),
        required=False,
    )
    page = serializers.IntegerField(
        label="page number",
        help_text="The page number to retrieve.",
        default=1
    )
    page_size = serializers.IntegerField(
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
    source = serializers.CharField(
        label="provider",
        help_text="A comma separated list of data sources to search. Valid "
                  "inputs:"
                  " `{}`".format(list(get_providers('image').keys())),
        required=False
    )
    extension = serializers.CharField(
        label="extension",
        help_text="A comma separated list of desired file extensions.",
        required=False
    )
    categories = serializers.CharField(
        label="categories",
        help_text="A comma separated list of categories; available categories "
                  "include `illustration`, `photograph`, and "
                  "`digitized_artwork`.",
        required=False
    )
    aspect_ratio = serializers.CharField(
        label='aspect_ratio',
        help_text="A comma separated list of aspect ratios; available aspect "
                  "ratios include `tall`, `wide`, and `square`.",
        required=False
    )
    size = serializers.CharField(
        label='size',
        help_text="A comma separated list of image sizes; available sizes"
                  "include `small`, `medium`, or `large`.",
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
    def validate_license(value):
        return _validate_li(value)

    @staticmethod
    def validate_license_type(value):
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

    @staticmethod
    def validate_categories(value):
        valid_categories = {
            'illustration',
            'digitized_artwork',
            'photograph'
        }
        _validate_enum('category', valid_categories, value)
        return value.lower()

    @staticmethod
    def validate_aspect_ratio(value):
        valid_ratios = {'tall', 'wide', 'square'}
        _validate_enum('aspect ratio', valid_ratios, value)
        return value.lower()

    def validate(self, data):
        for deprecated in self.deprecated_params:
            param, successor = deprecated
            if param in self.initial_data:
                raise serializers.ValidationError(
                    f"Parameter '{param}' is deprecated in this release of"
                    f" the API. Use '{successor}' instead."
                )
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


def _add_protocol(url: str):
    """
    Some fields in the database contain incomplete URLs, leading to unexpected
    behavior in downstream consumers. This helper verifies that we always return
    fully formed URLs in such situations.
    """
    parsed = urlparse(url)
    if parsed.scheme == '':
        return 'https://' + url
    else:
        return url


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
    source = serializers.CharField(required=False, source='provider')
    license = serializers.SerializerMethodField()
    license_version = serializers.CharField(required=False)
    license_url = serializers.SerializerMethodField()
    foreign_landing_url = serializers.URLField(required=False)
    detail_url = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name='image-detail',
        lookup_field='identifier',
        help_text="A direct link to the detail view of this image."
    )
    related_url = serializers.HyperlinkedIdentityField(
        view_name='related-images',
        lookup_field='identifier',
        read_only=True,
        help_text="A link to an endpoint that provides similar images."
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
    attribution = serializers.CharField(
        required=False,
        help_text="The Creative Commons attribution of the work. Use this to "
                  "give credit to creators to their works and fulfill "
                  "legal attribution requirements."
    )

    def get_license(self, obj):
        return obj.license.lower()

    def get_license_url(self, obj):
        return license_helpers.get_license_url(obj.license, obj.license_version)

    def validate_url(self, value):
        return _add_protocol(value)

    def validate_creator_url(self, value):
        return _add_protocol(value)

    def validate_foreign_landing_url(self, value):
        return _add_protocol(value)


class ImageSearchResultsSerializer(serializers.Serializer):
    """ The full image search response. """
    result_count = serializers.IntegerField()
    page_count = serializers.IntegerField()
    page_size = serializers.IntegerField()
    results = ImageSerializer(many=True)


class ValidationErrorSerializer(serializers.Serializer):
    """ Returned if invalid query parameters are passed. """
    validation_error = serializers.JSONField()


class WatermarkQueryStringSerializer(serializers.Serializer):
    embed_metadata = serializers.BooleanField(
        help_text="Whether to embed ccREL metadata via XMP.",
        default=True
    )
    watermark = serializers.BooleanField(
        help_text="Whether to draw a frame around the image with attribution"
                  " text at the bottom.",
        default=True
    )

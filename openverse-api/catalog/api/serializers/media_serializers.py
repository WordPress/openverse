from collections import namedtuple
from urllib.parse import urlparse

from rest_framework import serializers

import catalog.api.licenses as license_helpers


def _validate_enum(enum_name, valid_values: set, given_values: str):
    """
    Validate whether the given values are all members of the given enum.

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


def _validate_lt(value):
    license_types = [x.lower() for x in value.split(',')]
    license_groups = []
    for _type in license_types:
        if _type not in license_helpers.LICENSE_GROUPS:
            raise serializers.ValidationError(
                f"License type '{_type}' does not exist."
            )
        license_groups.append(license_helpers.LICENSE_GROUPS[_type])
    intersected = set.intersection(*license_groups)
    cleaned = {_license.lower() for _license in intersected}

    return ','.join(list(cleaned))


def _validate_li(value):
    licenses = [x.upper() for x in value.split(',')]
    for _license in licenses:
        if _license not in license_helpers.LICENSE_GROUPS['all']:
            raise serializers.ValidationError(
                f"License '{_license}' does not exist."
            )
    return value.lower()


def _validate_page(value):
    if value < 1:
        return 1
    else:
        return value


def _add_protocol(url: str):
    """
    Some fields in the database contain incomplete URLs, leading to unexpected
    behavior in downstream consumers. This helper verifies that we always return
    fully formed URLs in such situations.
    """
    parsed = urlparse(url)
    if parsed.scheme == '':
        return f'https://{url}'
    else:
        return url


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


class MediaSearchQueryStringSerializer(serializers.Serializer):
    """
    This serializer parses and validates search query string parameters.
    """

    DeprecatedParam = namedtuple('DeprecatedParam', ['original', 'successor'])
    deprecated_params = [
        DeprecatedParam('li', 'license'),
        DeprecatedParam('lt', 'license_type'),
        DeprecatedParam('pagesize', 'page_size'),
        DeprecatedParam('provider', 'source')
    ]
    fields_names = [
        'q',
        'license',
        'license_type',
        'creator',
        'tags',
        'title',
        'filter_dead',
        'extension',
        'mature',
        'qa',
    ]
    """
    Keep the fields names in sync with the actual fields below as this list is
    used to generate Swagger documentation.
    """

    q = serializers.CharField(
        label="query",
        help_text="A query string that should not exceed 200 characters in "
                  "length",
        required=False,
    )
    license = serializers.CharField(
        label="licenses",
        help_text="A comma-separated list of licenses. Example: `by,cc0`. "
                  "Valid inputs: "
                  f"`{list(license_helpers.LICENSE_GROUPS['all'])}`",
        required=False,
    )
    license_type = serializers.CharField(
        label="license type",
        help_text="A list of license types. "
                  "Valid inputs: "
                  f"`{list(license_helpers.LICENSE_GROUPS.keys())}`",
        required=False,
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
    extension = serializers.CharField(
        label="extension",
        help_text="A comma separated list of desired file extensions.",
        required=False
    )
    mature = serializers.BooleanField(
        label='mature',
        default=False,
        required=False,
        help_text="Whether to include content for mature audiences."
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

    def validate_creator(self, value):
        return self.validate_q(value)

    def validate_tags(self, value):
        return self.validate_q(value)

    def validate_title(self, value):
        return self.validate_q(value)

    @staticmethod
    def validate_extension(value):
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


class MediaSerializer(serializers.Serializer):
    """
    This serializer serializes a single media file. The class should be
    inherited by all individual media serializers.
    """

    fields_names = [
        'id',
        'title',
        'foreign_landing_url',
        'creator',
        'creator_url',
        'url',
        'license',
        'license_version',
        'license_url',
        'provider',
        'source',
        'tags',
        'fields_matched',
        'attribution',
    ]
    """
    Keep the fields names in sync with the actual fields below as this list is
    used to generate Swagger documentation.
    """

    requires_context = True

    # Fields corresponding to IdentifierMixin
    id = serializers.CharField(
        required=True,
        help_text="Our unique identifier for an open-licensed work.",
        source='identifier'
    )

    # Fields corresponding to MediaMixin
    title = serializers.CharField(
        help_text="The name of the media.",
        required=False
    )
    foreign_landing_url = serializers.URLField(
        required=False,
        help_text="A foreign landing link for the image."
    )

    creator = serializers.CharField(
        help_text="The name of the media creator.",
        required=False,
        allow_blank=True
    )
    creator_url = serializers.URLField(
        required=False,
        help_text="A direct link to the media creator."
    )

    # Fields corresponding to FileMixin
    url = serializers.URLField(
        help_text="The actual URL to the media file."
    )

    # Fields corresponding to AbstractMedia
    license = serializers.SerializerMethodField(
        help_text="The name of license for the media."
    )
    license_version = serializers.CharField(
        required=False,
        help_text="The type of license for the media."
    )
    license_url = serializers.SerializerMethodField(
        help_text="A direct link to the media license."
    )

    provider = serializers.CharField(
        required=False,
        help_text="The content provider."
    )
    source = serializers.CharField(
        required=False,
        help_text="The source of the data, meaning a particular dataset."
    )

    tags = TagSerializer(
        required=False,
        many=True,
        help_text="Tags with detailed metadata, such as accuracy."
    )

    # Additional fields
    fields_matched = serializers.ListField(
        required=False,
        help_text="List the fields that matched the query for this result."
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
        if hasattr(obj, 'meta_data'):
            return license_helpers.get_license_url(
                obj.license, obj.license_version, obj.meta_data
            )
        elif hasattr(obj, 'license_url') and obj.license_url is not None:
            return obj.license_url
        else:
            return license_helpers.get_license_url(
                obj.license, obj.license_version, None
            )

    def validate_url(self, value):
        return _add_protocol(value)

    def validate_creator_url(self, value):
        return _add_protocol(value)

    def validate_foreign_landing_url(self, value):
        return _add_protocol(value)


class MediaSearchResultsSerializer(serializers.Serializer):
    """
    This serializer serializes the full media search response. The class should
    be inherited by all individual media serializers.
    """

    result_count = serializers.IntegerField(
        help_text="The total number of items returned by search result."
    )
    page_count = serializers.IntegerField(
        help_text="The total number of pages returned by search result."
    )
    page_size = serializers.IntegerField(
        help_text="The number of items per page."
    )
    page = serializers.IntegerField(
        help_text="The current page number returned in the response."
    )


class ProxiedImageSerializer(serializers.Serializer):
    """
    We want to show 3rd party content securely and under our own native URLs, so
    we route some images through our own proxy. We use this same endpoint to
    generate thumbnails for content.
    """
    full_size = serializers.BooleanField(
        default=False,
        help_text="If set, do not thumbnail the image."
    )

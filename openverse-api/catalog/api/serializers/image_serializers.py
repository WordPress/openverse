from django.urls import reverse
from rest_framework import serializers

from catalog.api.controllers.search_controller import get_sources
from catalog.api.models import ImageReport
from catalog.api.serializers.media_serializers import (
    _add_protocol,
    _validate_enum,
    MediaSearchQueryStringSerializer,
    MediaSearchResultsSerializer,
    MediaSerializer,
)


class ImageSearchQueryStringSerializer(MediaSearchQueryStringSerializer):
    """ Parse and validate search query string parameters. """
    """
    Keep the fields names in sync with the actual fields below as this list is
    used to generate Swagger documentation.
    """
    fields_names = [
        *MediaSearchQueryStringSerializer.fields_names,
        'source',
        'categories',
        'aspect_ratio',
        'size',
    ]

    source = serializers.CharField(
        label="provider",
        help_text="A comma separated list of data sources to search. Valid "
                  "inputs: "
                  f"`{list(get_sources('image').keys())}`",
        required=False
    )
    # Ref: ingestion_server/ingestion_server/categorize.py#Category
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
                  " include `small`, `medium`, or `large`.",
        required=False
    )

    @staticmethod
    def validate_source(input_sources):
        allowed_sources = list(get_sources('image').keys())
        input_sources = input_sources.split(',')
        input_sources = [x for x in input_sources if x in allowed_sources]
        input_sources = ','.join(input_sources)
        return input_sources.lower()

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


class ImageSerializer(MediaSerializer):
    """ A single image. Used in search results."""

    """
    Keep the fields names in sync with the actual fields below as this list is
    used to generate Swagger documentation.
    """
    fields_names = [
        *MediaSerializer.fields_names,
        'thumbnail',
        'height',
        'width',
        'detail_url',
        'related_url',
    ]

    thumbnail = serializers.SerializerMethodField(
        help_text="A direct link to the miniature image."
    )
    height = serializers.IntegerField(
        required=False,
        help_text="The height of the image in pixels. Not always available."
    )
    width = serializers.IntegerField(
        required=False,
        help_text="The width of the image in pixels. Not always available."
    )

    # Hyperlinks
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

    def get_thumbnail(self, obj):
        request = self.context['request']
        host = request.get_host()
        path = reverse('thumbs', kwargs={'identifier': obj.identifier})
        return f'https://{host}{path}'


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


class ImageSearchResultsSerializer(MediaSearchResultsSerializer):
    """ The full image search response. """
    results = ImageSerializer(
        many=True,
        help_text="An array of images and their details such as `title`, `id`, "
                  "`creator`, `creator_url`, `url`, `thumbnail`, `provider`, "
                  "`source`, `license`, `license_version`, `license_url`, "
                  "`foreign_landing_url`, `detail_url`, `related_url`, "
                  "and `fields_matched `."
    )


class OembedResponseSerializer(serializers.Serializer):
    """ The embedded content from a specified image URL. """
    version = serializers.IntegerField(
        help_text="The image version."
    )
    type = serializers.CharField(
        help_text="Type of data."
    )
    width = serializers.IntegerField(
        help_text="The width of the image in pixels."
    )
    height = serializers.IntegerField(
        help_text="The height of the image in pixels."
    )
    title = serializers.CharField(
        help_text="The name of image."
    )
    author_name = serializers.CharField(
        help_text="The name of author for image."
    )
    author_url = serializers.URLField(
        help_text="A direct link to the author."
    )
    license_url = serializers.URLField(
        help_text="A direct link to the license for image."
    )


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


class ReportImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageReport
        fields = ('reason', 'identifier', 'description')

    def create(self, validated_data):
        if validated_data['reason'] == "other" and \
            ('description' not in validated_data or len(
                validated_data['description'])) < 20:
            raise serializers.ValidationError(
                "Description must be at least be 20 characters long"
            )
        return ImageReport.objects.create(**validated_data)


class OembedSerializer(serializers.Serializer):
    """ Parse and validate Oembed parameters. """
    url = serializers.URLField(
        help_text="The link to an image."
    )

    def validate_url(self, value):
        return _add_protocol(value)

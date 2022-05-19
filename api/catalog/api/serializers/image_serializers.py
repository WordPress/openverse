from rest_framework import serializers

from catalog.api.constants.field_order import field_position_map
from catalog.api.constants.field_values import (
    ASPECT_RATIOS,
    IMAGE_CATEGORIES,
    IMAGE_SIZES,
)
from catalog.api.docs.media_docs import fields_to_md
from catalog.api.models import Image, ImageReport
from catalog.api.serializers.base import BaseModelSerializer
from catalog.api.serializers.fields import EnumCharField
from catalog.api.serializers.media_serializers import (
    MediaReportRequestSerializer,
    MediaSearchRequestSerializer,
    MediaSearchSerializer,
    MediaSerializer,
    get_hyperlinks_serializer,
    get_search_request_source_serializer,
)
from catalog.api.utils.url import add_protocol


#######################
# Request serializers #
#######################


ImageSearchRequestSourceSerializer = get_search_request_source_serializer("image")


class ImageSearchRequestSerializer(
    ImageSearchRequestSourceSerializer,
    MediaSearchRequestSerializer,
):
    """Parse and validate search query string parameters."""

    fields_names = [
        *MediaSearchRequestSerializer.fields_names,
        *ImageSearchRequestSourceSerializer.field_names,
        "category",
        "aspect_ratio",
        "size",
    ]
    """
    Keep the fields names in sync with the actual fields below as this list is
    used to generate Swagger documentation.
    """

    # Ref: ingestion_server/ingestion_server/categorize.py#Category
    category = EnumCharField(
        plural="categories",
        enum_class=IMAGE_CATEGORIES,
        required=False,
    )
    aspect_ratio = EnumCharField(
        plural="aspect ratios",
        enum_class=ASPECT_RATIOS,
        required=False,
    )
    size = EnumCharField(
        plural="image sizes",
        enum_class=IMAGE_SIZES,
        required=False,
    )


class ImageReportRequestSerializer(MediaReportRequestSerializer):
    class Meta(MediaReportRequestSerializer.Meta):
        model = ImageReport


########################
# Response serializers #
########################

ImageHyperlinksSerializer = get_hyperlinks_serializer("image")


class ImageSerializer(ImageHyperlinksSerializer, MediaSerializer):
    """A single image. Used in search results."""

    class Meta:
        model = Image
        fields = sorted(  # keep this list ordered logically
            [
                *MediaSerializer.Meta.fields,
                *ImageHyperlinksSerializer.field_names,
                "height",
                "width",
            ],
            key=lambda val: field_position_map.get(val, 999),
        )
        """
        Keep the fields names in sync with the actual fields below as this list is
        used to generate Swagger documentation.
        """


class ImageSearchSerializer(MediaSearchSerializer):
    """
    The full image search response.
    This serializer is purely representational and not actually used to
    serialize the response.
    """

    results = ImageSerializer(
        many=True,
        help_text=(
            "An array of images and their details such as "
            f"{fields_to_md(ImageSerializer.Meta.fields)}."
        ),
    )


##########################
# Additional serializers #
##########################


class OembedRequestSerializer(serializers.Serializer):
    """Parse and validate Oembed parameters."""

    url = serializers.CharField(
        help_text="The link to an image.",
    )

    @staticmethod
    def validate_url(value):
        return add_protocol(value)


class OembedSerializer(BaseModelSerializer):
    """
    The embedded content from a specified image URL. This is essentially an
    ``ImageSerializer`` with some changes to match the oEmbed spec: https://oembed.com.
    """

    version = serializers.ReadOnlyField(
        help_text="The oEmbed version number. This must be 1.0.",
        default="1.0",
    )
    type = serializers.ReadOnlyField(
        help_text="The resource type. This must be 'photo' for images.",
        default="photo",
    )
    width = serializers.SerializerMethodField(
        help_text="The width of the image in pixels."
    )
    height = serializers.SerializerMethodField(
        help_text="The height of the image in pixels."
    )
    author_name = serializers.CharField(
        help_text="The name of the media creator.",  # ``copied from ``Image``
        source="creator",
    )
    author_url = serializers.URLField(
        help_text="A direct link to the media creator.",  # copied from ``Image``
        source="creator_url",
    )

    class Meta:
        model = Image
        fields = [
            "version",
            "type",
            "width",
            "height",
            "title",
            "author_name",
            "author_url",
            "license_url",
        ]

    def get_width(self, obj) -> int:
        return self.context.get("width", obj.width)

    def get_height(self, obj) -> int:
        return self.context.get("height", obj.height)


class WatermarkRequestSerializer(serializers.Serializer):
    embed_metadata = serializers.BooleanField(
        help_text="Whether to embed ccREL metadata via XMP.", default=True
    )
    watermark = serializers.BooleanField(
        help_text="Whether to draw a frame around the image with attribution"
        " text at the bottom.",
        default=True,
    )

from typing import Literal
from uuid import UUID

from django.core.exceptions import ValidationError
from rest_framework import serializers

from api.constants.field_order import field_position_map
from api.constants.field_values import ASPECT_RATIOS, IMAGE_CATEGORIES, IMAGE_SIZES
from api.constants.media_types import IMAGE_TYPE
from api.models import Image, ImageReport
from api.serializers.base import BaseModelSerializer
from api.serializers.fields import EnumCharField
from api.serializers.media_serializers import (
    MediaReportRequestSerializer,
    MediaSearchRequestSerializer,
    MediaSerializer,
    get_hyperlinks_serializer,
    get_search_request_source_serializer,
)


#######################
# Request serializers #
#######################


ImageSearchRequestSourceSerializer = get_search_request_source_serializer("image")


class ImageSearchRequestSerializer(
    ImageSearchRequestSourceSerializer,
    MediaSearchRequestSerializer,
):
    """Parse and validate search query string parameters."""

    field_names = [
        *MediaSearchRequestSerializer.field_names,
        *ImageSearchRequestSourceSerializer.field_names,
        "category",
        "aspect_ratio",
        "size",
    ]
    """
    Keep the fields names in sync with the actual fields below as this list is
    used to generate Swagger documentation.
    """

    # Ref: api/search/constants/field_values.py
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

    def validate_internal__index(self, value):
        index = super().validate_internal__index(value)
        if index is None:
            return None
        if not index.startswith(IMAGE_TYPE):
            raise serializers.ValidationError(f"Invalid index name `{value}`.")
        return index


class ImageReportRequestSerializer(MediaReportRequestSerializer):
    identifier = serializers.SlugRelatedField(
        slug_field="identifier",
        queryset=Image.objects.all(),
        source="media_obj",
    )

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

    needs_db = True  # for the 'height' and 'width' fields


##########################
# Additional serializers #
##########################


class OembedRequestSerializer(serializers.Serializer):
    """Parse and validate oEmbed parameters."""

    url = serializers.URLField(
        allow_blank=False,
        help_text="The link to an image present in Openverse.",
    )

    def to_internal_value(self, data):
        data = super().to_internal_value(data)

        url = data["url"]
        if url.endswith("/"):
            url = url[:-1]
        identifier = url.rsplit("/", 1)[1]

        try:
            uuid = UUID(identifier)
        except ValueError:
            raise serializers.ValidationError(
                {"Could not parse identifier from URL.": data["url"]}
            )

        try:
            image = Image.objects.get(identifier=uuid)
        except (Image.DoesNotExist, ValidationError):
            raise serializers.ValidationError(
                {"Could not find image from the provided URL": data["url"]}
            )

        data["image"] = image
        return data


class OembedSerializer(BaseModelSerializer):
    """
    The embedded content from a specified image URL.

    This is essentially an ``ImageSerializer`` with some changes to match the oEmbed
    spec: https://oembed.com.
    """

    version = serializers.SerializerMethodField(
        help_text="The oEmbed version number, always set to 1.0.",
    )
    type = serializers.SerializerMethodField(
        help_text="The resource type, always set to 'photo' for images.",
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

    @staticmethod
    def get_type(*_) -> Literal["photo"]:
        return "photo"

    @staticmethod
    def get_version(*_) -> Literal["1.0"]:
        return "1.0"

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

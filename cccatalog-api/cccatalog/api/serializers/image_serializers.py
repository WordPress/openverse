from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from cccatalog.api.models import Image
from cccatalog.api.serializers.search_serializers import ImageSerializer


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

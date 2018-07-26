from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from cccatalog.api.models import Image
from cccatalog.api.serializers.search_serializers import ImageSerializer


class ImageDetailSerializer(ModelSerializer, ImageSerializer):
    """ A single image with some additional fields, such as view count. Unlike
    ImageSerializer, the detail view comes from the database rather than
    Elasticsearch."""
    view_count = serializers.IntegerField(required=False)

    class Meta:
        model = Image
        fields = ('title', 'identifier', 'creator', 'creator_url', 'tags_list',
                  'url', 'thumbnail', 'provider', 'source', 'license',
                  'license_version', 'foreign_landing_url', 'meta_data',
                  'view_count')
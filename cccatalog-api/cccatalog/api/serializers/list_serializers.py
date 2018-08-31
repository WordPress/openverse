from rest_framework import serializers
from cccatalog.api.models import ImageList
from cccatalog.api.serializers.image_serializers import ImageDetailSerializer
import secrets


class ImageListBaseSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('images',)

    def validate_images(self, image_keys):
        if len(image_keys) > 500:
            raise serializers.ValidationError(
                "Only up to 500 images can be added to a list."
            )
        return image_keys


class ImageListCreateSerializer(ImageListBaseSerializer):
    """
    Responsible for parsing POST JSON body and persisting to the database.
    """
    lookup_field = 'id'
    id = serializers.ReadOnlyField()
    auth = serializers.ReadOnlyField()

    class Meta:
        model = ImageList
        fields = ('id', 'title', 'images', 'auth')

    def save(self):
        title = self.validated_data['title']
        images = self.validated_data['images']
        auth = secrets.token_urlsafe(48)
        image_list = ImageList(title=title, auth=auth)
        image_list.save()
        image_list.images.add(*images)

        return image_list


class ImageListResponseSerializer(serializers.Serializer):
    """
    Return a list of fully resolved images.
    """
    lookup_field = 'slug'
    id = serializers.ReadOnlyField()
    images = ImageDetailSerializer(many=True)


class ImageListUpdateSerializer(ImageListBaseSerializer):
    lookup_field = 'id'

    class Meta:
        model = ImageList
        fields = ('images',)

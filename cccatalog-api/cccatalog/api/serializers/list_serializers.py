from rest_framework import serializers
from cccatalog.api.models import ImageList
from cccatalog.api.serializers.image_serializers import ImageDetailSerializer


class ImageListCreateSerializer(serializers.ModelSerializer):
    """
    Responsible for parsing POST JSON body and persisting to the database.
    """
    lookup_field = 'id'
    id = serializers.ReadOnlyField()

    class Meta:
        model = ImageList
        fields = ('id', 'title', 'images')

    def validate_images(self, image_keys):
        if len(image_keys) > 500:
            raise serializers.ValidationError(
                "Only up to 500 images can be added to a list."
            )
        return image_keys

    def save(self):
        title = self.validated_data['title']
        images = self.validated_data['images']
        image_list = ImageList(title=title)
        image_list.save()
        _id = image_list.slug

        for image in images:
            image_list.images.add(image)

        return _id


class ImageListResponseSerializer(serializers.Serializer):
    """
    Return a list of fully resolved images.
    """
    lookup_field = 'slug'
    id = serializers.ReadOnlyField()
    images = ImageDetailSerializer(many=True)

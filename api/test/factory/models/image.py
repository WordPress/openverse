from test.factory.models.media import MediaFactory

from catalog.api.models.image import Image


class ImageFactory(MediaFactory):
    class Meta:
        model = Image

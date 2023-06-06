from test.factory.models.media import MediaFactory

import factory
from factory.django import DjangoModelFactory

from api.models.image import Image, MatureImage


class MatureImageFactory(DjangoModelFactory):
    class Meta:
        model = MatureImage

    media_obj = factory.SubFactory("test.factory.models.image.ImageFactory")


class ImageFactory(MediaFactory):
    _mature_factory = MatureImageFactory

    class Meta:
        model = Image

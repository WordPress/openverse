import factory
from factory.django import DjangoModelFactory

from api.models.image import Image, ImageReport, SensitiveImage
from test.factory.models.media import MediaFactory, MediaReportFactory


class SensitiveImageFactory(DjangoModelFactory):
    class Meta:
        model = SensitiveImage

    media_obj = factory.SubFactory("test.factory.models.image.ImageFactory")


class ImageFactory(MediaFactory):
    _sensitive_factory = SensitiveImageFactory

    class Meta:
        model = Image


class ImageReportFactory(MediaReportFactory):
    class Meta:
        model = ImageReport

    media_obj = factory.SubFactory(ImageFactory)

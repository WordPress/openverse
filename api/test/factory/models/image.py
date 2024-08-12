import factory
from factory.django import DjangoModelFactory

from api.models.image import DeletedImage, Image, ImageReport, SensitiveImage
from test.factory.faker import Faker
from test.factory.models.media import MediaFactory, MediaReportFactory


class SensitiveImageFactory(DjangoModelFactory):
    class Meta:
        model = SensitiveImage

    media_obj = factory.SubFactory("test.factory.models.image.ImageFactory")


class DeletedImageFactory(DjangoModelFactory):
    class Meta:
        model = DeletedImage

    media_obj = factory.SubFactory("test.factory.models.image.ImageFactory")


class ImageFactory(MediaFactory):
    _sensitive_factory = SensitiveImageFactory

    class Meta:
        model = Image

    width = Faker("random_element", elements=(100, 1200, 2500))
    height = Faker("random_element", elements=(100, 1200, 2500))


class ImageReportFactory(MediaReportFactory):
    class Meta:
        model = ImageReport

    media_obj = factory.SubFactory(ImageFactory)

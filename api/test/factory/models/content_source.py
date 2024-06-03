from factory.django import DjangoModelFactory

from api.models import ContentSource


class ContentSourceFactory(DjangoModelFactory):
    class Meta:
        model = ContentSource

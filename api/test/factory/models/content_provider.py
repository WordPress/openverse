from factory.django import DjangoModelFactory

from api.models import ContentProvider


class ContentProviderFactory(DjangoModelFactory):
    class Meta:
        model = ContentProvider

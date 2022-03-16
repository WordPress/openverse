from test.factory.faker import Faker

import factory
from catalog.api.models.oauth import ThrottledApplication
from factory.django import DjangoModelFactory
from oauth2_provider.models import AccessToken


class ThrottledApplicationFactory(DjangoModelFactory):
    class Meta:
        model = ThrottledApplication

    client_type = Faker(
        "random_choice_field", choices=ThrottledApplication.CLIENT_TYPES
    )
    authorization_grant_type = Faker(
        "random_choice_field", choices=ThrottledApplication.GRANT_TYPES
    )


class AccessTokenFactory(DjangoModelFactory):
    class Meta:
        model = AccessToken

    token = Faker("uuid4")
    expires = Faker("date_time_between", start_date="+1y", end_date="+2y")
    application = factory.SubFactory(ThrottledApplicationFactory)

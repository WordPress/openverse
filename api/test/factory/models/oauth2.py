from django.utils import timezone

import factory
from factory.django import DjangoModelFactory
from oauth2_provider.models import AccessToken

from api.models.oauth import (
    OAuth2Registration,
    OAuth2Verification,
    ThrottledApplication,
)
from test.factory.faker import Faker


class ThrottledApplicationFactory(DjangoModelFactory):
    class Meta:
        model = ThrottledApplication

    name = Faker("md5")
    client_type = Faker(
        "random_choice_field", choices=ThrottledApplication.CLIENT_TYPES
    )
    authorization_grant_type = Faker(
        "random_choice_field", choices=ThrottledApplication.GRANT_TYPES
    )


class OAuth2RegistrationFactory(DjangoModelFactory):
    class Meta:
        model = OAuth2Registration

    name = Faker("md5")
    description = Faker("catch_phrase")
    email = Faker("email")

    @factory.post_generation
    def application(obj, create, extracted, **kwargs):
        # Only create the application if creating, and either
        # `application=True` or some `application__*` kwargs were passed
        if not (create and (extracted or kwargs)):
            return

        return ThrottledApplicationFactory.create(
            name=obj.name,
            verified=kwargs.get("verified", False),
        )


class OAuth2VerificationFactory(DjangoModelFactory):
    class Meta:
        model = OAuth2Verification

    associated_application = factory.SubFactory(ThrottledApplicationFactory)
    email = Faker("email")
    code = Faker("md5")


class AccessTokenFactory(DjangoModelFactory):
    class Meta:
        model = AccessToken

    token = Faker("uuid4")
    expires = Faker(
        "date_time_between",
        start_date="+1y",
        end_date="+2y",
        tzinfo=timezone.get_current_timezone(),
    )
    application = factory.SubFactory(ThrottledApplicationFactory)

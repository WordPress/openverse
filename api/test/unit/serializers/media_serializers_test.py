import uuid
from test.factory.models.oauth2 import AccessTokenFactory
from unittest.mock import MagicMock

from django.conf import settings
from rest_framework.exceptions import NotAuthenticated, ValidationError
from rest_framework.test import force_authenticate
from rest_framework.views import APIView

import pytest

from catalog.api.serializers.audio_serializers import AudioSerializer
from catalog.api.serializers.image_serializers import ImageSerializer
from catalog.api.serializers.media_serializers import MediaSearchRequestSerializer


@pytest.fixture
def access_token():
    token = AccessTokenFactory.create()
    token.application.verified = True
    token.application.save()
    return token


@pytest.fixture
def hit():
    hit = MagicMock(
        identifier=uuid.uuid4(),
        license="cc0",
        license_version="1.0",
    )
    return hit


@pytest.fixture
def authed_request(access_token, request_factory):
    request = request_factory.get("/")

    force_authenticate(request, token=access_token.token)

    return APIView().initialize_request(request)


@pytest.fixture
def anon_request(request_factory):
    return APIView().initialize_request(request_factory.get("/"))


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("page_size", "authenticated"),
    (
        pytest.param(-1, False, marks=pytest.mark.raises(exception=ValidationError)),
        pytest.param(0, False, marks=pytest.mark.raises(exception=ValidationError)),
        (1, False),
        (settings.MAX_ANONYMOUS_PAGE_SIZE, False),
        pytest.param(
            settings.MAX_ANONYMOUS_PAGE_SIZE + 1,
            False,
            marks=pytest.mark.raises(exception=NotAuthenticated),
        ),
        pytest.param(
            settings.MAX_AUTHED_PAGE_SIZE,
            False,
            marks=pytest.mark.raises(exception=NotAuthenticated),
        ),
        pytest.param(-1, True, marks=pytest.mark.raises(exception=ValidationError)),
        pytest.param(0, True, marks=pytest.mark.raises(exception=ValidationError)),
        (1, True),
        (settings.MAX_ANONYMOUS_PAGE_SIZE + 1, True),
        (settings.MAX_AUTHED_PAGE_SIZE, True),
        pytest.param(
            settings.MAX_AUTHED_PAGE_SIZE + 1,
            True,
            marks=pytest.mark.raises(exception=ValidationError),
        ),
    ),
)
def test_page_size_validation(page_size, authenticated, anon_request, authed_request):
    request = authed_request if authenticated else anon_request
    serializer = MediaSearchRequestSerializer(
        context={"request": request}, data={"page_size": page_size}
    )
    assert serializer.is_valid(raise_exception=True)


@pytest.mark.parametrize(
    "serializer_class",
    [
        AudioSerializer,
        ImageSerializer,
    ],
)
def test_media_serializer_adds_license_url_if_missing(
    anon_request, hit, serializer_class
):
    # Note that this behaviour is inherited from the parent `MediaSerializer` class, but
    # it cannot be tested without a concrete model to test with.

    del hit.license_url  # without the ``del``, the property is dynamically generated
    repr = serializer_class(hit, context={"request": anon_request}).data
    assert repr["license_url"] == "https://creativecommons.org/publicdomain/zero/1.0/"


@pytest.mark.parametrize(
    ("data", "result"),
    (
        ({"mature": True}, {"unstable__include_sensitive_results": True}),
        (
            {"unstable__include_sensitive_results": True},
            {"unstable__include_sensitive_results": True},
        ),
        ({"mature": False}, {"unstable__include_sensitive_results": False}),
        (
            {"unstable__include_sensitive_results": False},
            {"unstable__include_sensitive_results": False},
        ),
    ),
)
def test_search_request_serializer_include_sensitive_results_validation_well_formed_request(
    data: dict, result
):
    serializer = MediaSearchRequestSerializer(data=data)
    assert serializer.is_valid()
    # The expected value should be mapped from the field actually
    # passed in data
    _, expected_value = data.popitem()
    assert serializer.validated_data["include_sensitive_results"] == expected_value


@pytest.mark.parametrize(
    "data",
    (
        {"mature": m, "unstable__include_sensitive_results": i}
        for m in (True, False)
        for i in (True, False)
    ),
)
def test_search_request_serializer_include_sensitive_results_malformed_request(data):
    serializer = MediaSearchRequestSerializer(data=data)
    assert not serializer.is_valid()

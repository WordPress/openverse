import uuid
from unittest.mock import MagicMock

from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

import pytest

from catalog.api.serializers.audio_serializers import AudioSerializer
from catalog.api.serializers.image_serializers import ImageSerializer


@pytest.fixture
def req():
    factory = APIRequestFactory()
    request = factory.get("/")
    request = Request(request)
    return request


@pytest.fixture
def hit():
    hit = MagicMock(
        identifier=uuid.uuid4(),
        license="cc0",
        license_version="1.0",
    )
    return hit


@pytest.mark.parametrize(
    "serializer_class",
    [
        AudioSerializer,
        ImageSerializer,
    ],
)
def test_media_serializer_adds_license_url_if_missing(req, hit, serializer_class):
    # Note that this behaviour is inherited from the parent `MediaSerializer` class, but
    # it cannot be tested without a concrete model to test with.

    del hit.license_url  # without the ``del``, the property is dynamically generated
    repr = serializer_class(hit, context={"request": req}).data
    assert repr["license_url"] == "https://creativecommons.org/publicdomain/zero/1.0/"

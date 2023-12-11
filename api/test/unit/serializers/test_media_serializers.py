import logging
import random
import uuid
from test.factory.models.oauth2 import AccessTokenFactory
from unittest.mock import MagicMock, patch

from django.conf import settings
from rest_framework.exceptions import NotAuthenticated, ValidationError
from rest_framework.test import force_authenticate
from rest_framework.views import APIView

import pytest

from api.constants import sensitivity
from api.serializers.audio_serializers import AudioSearchRequestSerializer
from api.serializers.image_serializers import ImageSearchRequestSerializer
from api.serializers.media_serializers import MediaSearchRequestSerializer


@pytest.fixture
def access_token():
    token = AccessTokenFactory.create()
    token.application.verified = True
    token.application.save()
    return token


@pytest.fixture
def hit():
    hit = MagicMock(
        identifier=str(uuid.uuid4()),
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


def test_media_serializer_adds_license_url_if_missing(
    anon_request, hit, media_type_config
):
    # Note that this behaviour is inherited from the parent `MediaSerializer` class, but
    # it cannot be tested without a concrete model to test with.
    serializer_class = media_type_config.model_serializer
    del hit.license_url  # without the ``del``, the property is dynamically generated
    repr = serializer_class(hit, context={"request": anon_request}).data
    assert repr["license_url"] == "https://creativecommons.org/publicdomain/zero/1.0/"


@pytest.mark.parametrize(
    "has_sensitive_text",
    (True, False),
    ids=lambda x: "has_sensitive_text" if x else "no_sensitive_text",
)
@pytest.mark.parametrize(
    "has_confirmed_report",
    (True, False),
    ids=lambda x: "has_confirmed_report" if x else "no_confirmed_report",
)
@pytest.mark.django_db
def test_media_serializer_sensitivity(
    has_sensitive_text,
    has_confirmed_report,
    media_type_config,
    anon_request,
):
    model, hit = media_type_config.model_factory.create(
        sensitive_text=has_sensitive_text,
        mature_reported=has_confirmed_report,
        with_hit=True,
    )
    logging.info(f"Created model: {model}, {model.mature}\nhit: {hit}, {hit.mature}")

    other_result_ids = [str(uuid.uuid4()) for _ in range(6)]
    context = {
        "request": anon_request,
        "all_result_identifiers": {hit.identifier} | set(other_result_ids),
        "sensitive_text_result_identifiers": set(random.choices(other_result_ids, k=3)),
    }

    if has_sensitive_text:
        context["sensitive_text_result_identifiers"] |= {hit.identifier}

    serializer = media_type_config.model_serializer(model, context=context)

    expected_sensitivity = set()
    if has_sensitive_text:
        expected_sensitivity.add(sensitivity.TEXT)
    if has_confirmed_report:
        expected_sensitivity.add(sensitivity.USER_REPORTED)

    logging.info(f"Serializer data: {serializer.data}")
    logging.info(
        f"Expected sensitivity: {expected_sensitivity}\nActual sensitivity: "
        f"{serializer.data['unstable__sensitivity']}"
    )

    assert set(serializer.data["unstable__sensitivity"]) == expected_sensitivity


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


@pytest.mark.django_db
@patch("django.conf.settings.ES")
@pytest.mark.parametrize(
    "authenticated",
    (
        True,
        False,
    ),
)
def test_index_is_only_set_if_authenticated(
    mock_es, authenticated, anon_request, authed_request
):
    mock_es.indices.exists.return_value = True

    request = authed_request if authenticated else anon_request
    serializer = ImageSearchRequestSerializer(
        data={"internal__index": "image-some-index"}, context={"request": request}
    )
    assert serializer.is_valid()
    assert serializer.validated_data.get("index") == (
        "image-some-index" if authenticated else None
    )

    if authenticated:
        # If authenticated, we should have checked that the index exists.
        mock_es.indices.exists.assert_called_with("image-some-index")
    else:
        # If not authenticated, the validator quickly returns ``None``.
        mock_es.indices.exists.assert_not_called()


@pytest.mark.django_db
@patch("django.conf.settings.ES")
@pytest.mark.parametrize(
    "index, is_valid",
    (("image-index-that-exists", True), ("image-index-that-does-not-exist", False)),
)
def test_index_is_only_set_if_valid(mock_es, index, is_valid, authed_request):
    mock_es.indices.exists = lambda index: "exists" in index

    serializer = ImageSearchRequestSerializer(
        data={"internal__index": index}, context={"request": authed_request}
    )
    assert serializer.is_valid() == is_valid
    assert serializer.validated_data.get("index") == (index if is_valid else None)


@pytest.mark.django_db
@patch("django.conf.settings.ES")
@pytest.mark.parametrize(
    "serializer_class, index, is_valid",
    (
        (AudioSearchRequestSerializer, "audio-other", True),
        (ImageSearchRequestSerializer, "image-other", True),
        (AudioSearchRequestSerializer, "image-other", False),
        (ImageSearchRequestSerializer, "audio-other", False),
    ),
)
def test_index_is_only_set_if_matches_media_type(
    mock_es, serializer_class, index, is_valid, authed_request
):
    mock_es.indices.exists.return_value = True

    serializer = serializer_class(
        data={"internal__index": index}, context={"request": authed_request}
    )
    assert serializer.is_valid() == is_valid
    assert serializer.validated_data.get("index") == (index if is_valid else None)


@pytest.mark.django_db
def test_report_serializer_maps_sensitive_reason_to_mature(media_type_config):
    media = media_type_config.model_factory.create()
    serializer = media_type_config.report_serializer(
        data={
            "identifier": media.identifier,
            "reason": "sensitive",
            "description": "Boop beep this is sensitive, whoa!",
        }
    )

    serializer.is_valid(raise_exception=True)

    assert serializer.validated_data["reason"] == "mature"


@pytest.mark.django_db
def test_report_serializer_accepts_mature_reason(media_type_config):
    media = media_type_config.model_factory.create()
    serializer = media_type_config.report_serializer(
        data={
            "identifier": media.identifier,
            "reason": "mature",
            "description": "Boop beep this is sensitive, whoa!",
        }
    )

    serializer.is_valid(raise_exception=True)

    assert serializer.validated_data["reason"] == "mature"

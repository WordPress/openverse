import uuid

from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

import pytest

from catalog.api.models.audio import Audio
from catalog.api.serializers.audio_serializers import AudioSerializer


@pytest.fixture
@pytest.mark.django_db
def audio_fixture():
    audio = Audio(
        identifier=uuid.uuid4(),
    )
    audio.save()
    return audio


@pytest.mark.django_db
def test_audio_serializer_omit_peaks_by_default(audio_fixture):
    factory = APIRequestFactory()
    request = factory.get(f"audio/{audio_fixture.identifier}")
    request = Request(request)
    mock_ctx = {"request": request}

    audio_serializer = AudioSerializer(instance=audio_fixture, context=mock_ctx)
    assert "peaks" not in audio_serializer.data


@pytest.mark.django_db
@pytest.mark.parametrize("include_peaks", [True, False])
def test_audio_serializer_with_peaks_param(audio_fixture, include_peaks):
    factory = APIRequestFactory()
    request = factory.get(f"audio/{audio_fixture.identifier}/?peaks={include_peaks}")
    request = Request(request)
    mock_ctx = {"request": request, "validated_data": {"peaks": include_peaks}}

    audio_serializer = AudioSerializer(instance=audio_fixture, context=mock_ctx)
    assert ("peaks" in audio_serializer.data) is include_peaks

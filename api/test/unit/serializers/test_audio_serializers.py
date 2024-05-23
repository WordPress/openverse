import uuid

import pytest

from api.models.audio import Audio
from api.serializers.audio_serializers import AudioSerializer


@pytest.fixture
@pytest.mark.django_db
def audio_fixture():
    audio = Audio(
        identifier=uuid.uuid4(),
        license="cc0",
    )
    audio.save()
    return audio


@pytest.mark.django_db
def test_audio_serializer_omit_peaks_by_default(audio_fixture, anon_request):
    mock_ctx = {"request": anon_request}

    audio_serializer = AudioSerializer(instance=audio_fixture, context=mock_ctx)
    assert "peaks" not in audio_serializer.data


@pytest.mark.django_db
@pytest.mark.parametrize("include_peaks", [True, False])
def test_audio_serializer_with_peaks_param(audio_fixture, anon_request, include_peaks):
    mock_ctx = {"request": anon_request, "validated_data": {"peaks": include_peaks}}

    audio_serializer = AudioSerializer(instance=audio_fixture, context=mock_ctx)
    assert ("peaks" in audio_serializer.data) is include_peaks


# https://github.com/WordPress/openverse/issues/3930
@pytest.mark.django_db
def test_audio_serializer_with_non_required_alt_audio_fields_missing(anon_request):
    alt_files = [
        {"bit_rate": 128, "filetype": "mp3", "url": "https://example.com/audio.mp3"}
    ]
    audio = Audio(
        identifier=uuid.uuid4(),
        license="cc0",
        alt_files=alt_files,
    )
    audio.save()
    mock_ctx = {"request": anon_request}

    audio_serializer = AudioSerializer(instance=audio, context=mock_ctx)

    assert len(audio_serializer.data.get("alt_files")) == 1
    assert audio_serializer.data.get("alt_files")[0] == alt_files[0]

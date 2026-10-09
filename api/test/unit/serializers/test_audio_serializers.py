import uuid

import pytest

from api.models.audio import Audio, AudioSet
from api.serializers.audio_serializers import AudioSerializer, AudioSetSerializer


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


# Entity-encoded markup must be stripped the same way as literal markup.
ENCODED_MARKUP = "&lt;iframe&gt;X&lt;/iframe&gt;"


def test_audio_set_serializer_strips_markup_from_title_and_creator():
    audio_set = AudioSet(title=ENCODED_MARKUP, creator=ENCODED_MARKUP)

    output = AudioSetSerializer(audio_set).data

    assert output["title"] == "X"
    assert output["creator"] == "X"


def test_audio_set_serializer_drops_urls_with_unsafe_schemes():
    audio_set = AudioSet(
        creator_url="javascript:void(0)",
        foreign_landing_url="javascript:void(0)",
        url="javascript:void(0)",
    )

    output = AudioSetSerializer(audio_set).data

    assert output["creator_url"] is None
    assert output["foreign_landing_url"] is None
    assert output["url"] is None

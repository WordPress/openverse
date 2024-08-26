import logging

import pytest

from common.licenses import LicenseInfo
from common.storage import audio
from tests.dags.common.storage import test_media


logger = logging.getLogger(__name__)

PD_LICENSE_INFO = LicenseInfo(
    "zero", "1.0", "https://creativecommons.org/publicdomain/zero/1.0/", None
)
BY_LICENSE_INFO = LicenseInfo(
    "by", "4.0", "https://creativecommons.org/licenses/by/4.0/", None
)

mock_audio_args = {
    "foreign_landing_url": "https://landing_page.com",
    "url": "https://audiourl.com",
    "license_info": BY_LICENSE_INFO,
    "foreign_identifier": "foreign_id",
    "thumbnail_url": "https://thumbnail.com",
    "filetype": "ogg",
    "filesize": 1000,
    "duration": 200,
    "creator": "tyler",
    "creator_url": "https://creatorurl.com",
    "title": "agreatsong",
    "meta_data": {},
    "raw_tags": {},
    "watermarked": None,
    "bit_rate": None,
    "sample_rate": None,
    "category": None,
    "genres": [],
    "audio_set": {},
    "set_position": None,
    "alt_files": [],
    "source": "testing_source",
    "ingestion_type": "provider_api",
    "audio_set_foreign_identifier": None,
}


@pytest.fixture
def setup_env(monkeypatch):
    monkeypatch.setenv("OUTPUT_DIR", "/tmp")


def test_AudioStore_includes_provider_in_output_file_string():
    audio_store = audio.AudioStore("test_provider")
    assert isinstance(audio_store.output_path, str)
    assert "test_provider" in audio_store.output_path


def test_AudioStore_add_item_adds_realistic_audio_to_buffer():
    license_info = PD_LICENSE_INFO
    audio_store = audio.AudioStore(provider="testing_provider")
    audio_store.add_item(
        foreign_identifier="01",
        foreign_landing_url="https://audios.org/audio01",
        url="https://audios.org/audio01.mp3",
        license_info=license_info,
        ingestion_type="provider_api",
    )
    assert len(audio_store._media_buffer) == 1


def test_AudioStore_add_item_adds_multiple_audios_to_buffer():
    audio_store = audio.AudioStore(provider="testing_provider")
    audio_store.add_item(
        foreign_identifier="01",
        foreign_landing_url="https://audios.org/audio01",
        url="https://audios.org/audio01.mp3",
        license_info=PD_LICENSE_INFO,
    )
    audio_store.add_item(
        foreign_identifier="02",
        foreign_landing_url="https://audios.org/audio02",
        url="https://audios.org/audio02.mp3",
        license_info=PD_LICENSE_INFO,
    )
    audio_store.add_item(
        foreign_identifier="03",
        foreign_landing_url="https://audios.org/audio03",
        url="https://audios.org/audio03.mp3",
        license_info=PD_LICENSE_INFO,
    )
    audio_store.add_item(
        foreign_identifier="04",
        foreign_landing_url="https://audios.org/audio04",
        url="https://audios.org/audio04.mp3",
        license_info=PD_LICENSE_INFO,
    )
    assert len(audio_store._media_buffer) == 4


def test_AudioStore_add_item_flushes_buffer(tmpdir):
    audio_store = audio.AudioStore(
        provider="testing_provider",
        buffer_length=3,
    )
    audio_store.add_item(
        foreign_identifier="01",
        foreign_landing_url="https://audios.org/audio01",
        url="https://audios.org/audio01.mp3",
        license_info=PD_LICENSE_INFO,
    )
    audio_store.add_item(
        foreign_identifier="02",
        foreign_landing_url="https://audios.org/audio02",
        url="https://audios.org/audio02.mp3",
        license_info=PD_LICENSE_INFO,
    )
    audio_store.add_item(
        foreign_identifier="03",
        foreign_landing_url="https://audios.org/audio03",
        url="https://audios.org/audio03.mp3",
        license_info=PD_LICENSE_INFO,
    )
    audio_store.add_item(
        foreign_identifier="04",
        foreign_landing_url="https://audios.org/audio04",
        url="https://audios.org/audio04.mp3",
        license_info=PD_LICENSE_INFO,
    )
    assert len(audio_store._media_buffer) == 1
    with open(audio_store.output_path) as f:
        lines = f.read().split("\n")
    assert len(lines) == 4  # recall the last '\n' will create an empty line.


def test_AudioStore_commit_writes_nothing_if_no_lines_in_buffer():
    audio_store = audio.AudioStore(output_dir="/path/does/not/exist")
    audio_store.commit()


def test_AudioStore_produces_correct_total_audios():
    audio_store = audio.AudioStore(provider="testing_provider")
    audio_store.add_item(
        foreign_identifier="01",
        foreign_landing_url="https://audios.org/audio01",
        url="https://audios.org/audio01.mp3",
        license_info=PD_LICENSE_INFO,
    )
    audio_store.add_item(
        foreign_identifier="02",
        foreign_landing_url="https://audios.org/audio02",
        url="https://audios.org/audio02.mp3",
        license_info=PD_LICENSE_INFO,
    )
    audio_store.add_item(
        foreign_identifier="03",
        foreign_landing_url="https://audios.org/audio03",
        url="https://audios.org/audio03.mp3",
        license_info=PD_LICENSE_INFO,
    )
    assert audio_store.total_items == 3


@pytest.mark.parametrize(
    "filetype, url, expected_filetype",
    [
        # The value provided prevails over the url extension
        ("ogg", "http://example.com/audio", "ogg"),
        ("ogg", "http://example.com/audio.wav", "ogg"),
        # The filetype is guessed from the URL extension
        (None, "http://example.com/audio.mp3", "mp3"),
        (None, "http://example.com/audio.WAV", "wav"),
        (None, "http://example.com/audio.mid", "mid"),
        # Unifies filetypes
        ("midi", "http://example.com/audio.mid", "mid"),
        (None, "http://example.com/audio.midi", "mid"),
    ],
)
def test_AudioStore_validate_filetype(filetype, url, expected_filetype):
    audio_store = audio.MockAudioStore("test_provider")
    actual_filetype = audio_store._validate_filetype(filetype, url)
    assert actual_filetype == expected_filetype


@test_media.INT_MAX_PARAMETERIZATION
def test_AudioStore_get_audio_validates_duration(value, expected):
    audio_store = audio.AudioStore("test_provider")
    audio_args = mock_audio_args.copy()
    audio_args["duration"] = value
    actual_audio = audio_store._get_audio(
        **audio_args,
    )

    assert actual_audio.duration == expected


@pytest.fixture
def default_audio_args():
    return dict(
        foreign_identifier="foreign_id",
        foreign_landing_url="https://landing_page.org",
        url="https://audiourl.org",
        thumbnail_url="https://thumbnail.com",
        filetype=None,
        filesize=None,
        audio_set=None,
        set_position=1,
        license_="by",
        license_version="4.0",
        creator="tyler",
        creator_url="https://creatorurl.com",
        title="agreatsong",
        meta_data={"description": "cat song"},
        tags={"name": "tag1", "provider": "testing"},
        watermarked=None,
        duration=100,
        bit_rate=None,
        sample_rate=None,
        category="music",
        genres=["rock", "pop"],
        alt_files=None,
        provider="testing_provider",
        source="testing_source",
        ingestion_type="provider_api",
        audio_set_foreign_identifier=None,
    )


def test_create_tsv_row_creates_alt_files(
    default_audio_args,
):
    audio_store = audio.AudioStore()
    audio_args = default_audio_args.copy()
    alt_files = [
        {
            "url": "https://alternative.com/audio.mp3",
            "filesize": 123,
            "bit_rate": 41000,
            "sample_rate": "16000",
        }
    ]
    audio_args["alt_files"] = alt_files
    test_audio = audio.Audio(**audio_args)

    actual_row = audio_store._create_tsv_row(test_audio)
    expected_row = (
        "\t".join(
            [
                "foreign_id",
                "https://landing_page.org",
                "https://audiourl.org",
                "https://thumbnail.com",
                "\\N",
                "\\N",
                "by",
                "4.0",
                "tyler",
                "https://creatorurl.com",
                "agreatsong",
                '{"description": "cat song"}',
                '{"name": "tag1", "provider": "testing"}',
                "music",
                "\\N",
                "testing_provider",
                "testing_source",
                "provider_api",
                "100",
                "\\N",
                "\\N",
                '{"rock", "pop"}',
                "\\N",
                "1",
                '[{"url": '
                '"https://alternative.com/audio.mp3", "filesize": "123", "bit_rate": "41000", '
                '"sample_rate": "16000"}]',
                "\\N",
            ]
        )
        + "\n"
    )
    assert actual_row == expected_row


def test_create_tsv_row_creates_audio_set(
    default_audio_args,
):
    audio_store = audio.AudioStore()
    audio_args = default_audio_args.copy()
    audio_set_data = {
        "audio_set": "test_audio_set",
        "set_url": "test.com",
        "set_position": 1,
        "set_thumbnail": "thumbnail.jpg",
    }
    audio_args["audio_set"] = audio_set_data
    audio_args["audio_set_foreign_identifier"] = "12345"
    test_audio = audio.Audio(**audio_args)

    def mock_url_validator(value):
        # This avoids needing the internet for testing.
        return value

    actual_row = audio_store._create_tsv_row(test_audio)
    expected_row = (
        "\t".join(
            [
                "foreign_id",
                "https://landing_page.org",
                "https://audiourl.org",
                "https://thumbnail.com",
                "\\N",
                "\\N",
                "by",
                "4.0",
                "tyler",
                "https://creatorurl.com",
                "agreatsong",
                '{"description": "cat song"}',
                '{"name": "tag1", "provider": "testing"}',
                "music",
                "\\N",
                "testing_provider",
                "testing_source",
                "provider_api",
                "100",
                "\\N",
                "\\N",
                '{"rock", "pop"}',
                '{"audio_set": "test_audio_set", "set_url": "test.com", '
                '"set_position": "1", "set_thumbnail": "thumbnail.jpg"}',
                "1",
                "\\N",
                "12345",
            ]
        )
        + "\n"
    )
    assert actual_row == expected_row


def test_create_tsv_row_non_none_if_req_fields(
    default_audio_args,
):
    audio_store = audio.AudioStore()
    test_audio = audio.Audio(**default_audio_args)
    actual_row = audio_store._create_tsv_row(test_audio)
    assert actual_row is not None


def test_create_tsv_row_none_if_no_foreign_landing_url(
    default_audio_args,
):
    audio_store = audio.AudioStore()
    audio_args = default_audio_args
    audio_args["foreign_landing_url"] = None
    test_audio = audio.Audio(**audio_args)
    expect_row = None
    actual_row = audio_store._create_tsv_row(test_audio)
    assert expect_row == actual_row


def test_create_tsv_row_none_if_no_license(
    default_audio_args,
):
    audio_store = audio.AudioStore()
    audio_args = default_audio_args
    audio_args["license_"] = None
    test_audio = audio.Audio(**audio_args)
    expect_row = None
    actual_row = audio_store._create_tsv_row(test_audio)
    assert expect_row == actual_row


def test_create_tsv_row_none_if_no_license_version(
    default_audio_args,
):
    audio_store = audio.AudioStore()
    audio_args = default_audio_args
    audio_args["license_version"] = None
    test_audio = audio.Audio(**audio_args)
    expect_row = None
    actual_row = audio_store._create_tsv_row(test_audio)
    assert expect_row == actual_row


def test_create_tsv_row_returns_none_if_missing_audio_url(
    default_audio_args,
):
    audio_store = audio.AudioStore()
    audio_args = default_audio_args
    audio_args["url"] = None
    test_audio = audio.Audio(**audio_args)
    expect_row = None
    actual_row = audio_store._create_tsv_row(test_audio)
    assert expect_row == actual_row


def test_create_tsv_row_handles_empty_dict_and_tags(
    default_audio_args,
):
    audio_store = audio.AudioStore()
    meta_data = {}
    tags = []
    audio_args = default_audio_args
    audio_args["meta_data"] = meta_data
    audio_args["tags"] = tags
    test_audio = audio.Audio(**audio_args)

    actual_row = audio_store._create_tsv_row(test_audio).split("\t")
    actual_meta_data, actual_tags = None, None
    for i, field in enumerate(audio.Audio._fields):
        if field == "meta_data":
            actual_meta_data = actual_row[i]
        elif field == "tags":
            actual_tags = actual_row[i]
    assert actual_meta_data is not None and actual_tags is not None
    expect_meta_data, expect_tags = "\\N", "\\N"
    assert expect_meta_data == actual_meta_data
    assert expect_tags == actual_tags


def test_create_tsv_row_properly_places_entries(monkeypatch):
    audio_store = audio.AudioStore()
    req_args_dict = {
        "foreign_landing_url": "https://landing_page.com",
        "url": "https://audiourl.com",
        "license_": "testlicense",
        "license_version": "1.0",
    }
    args_dict = {
        "foreign_identifier": "foreign_id",
        "thumbnail_url": "https://thumbnail.com",
        "filetype": "mp3",
        "duration": 200,
        "filesize": None,
        "creator": "tyler",
        "creator_url": "https://creatorurl.com",
        "title": "agreatsong",
        "meta_data": {"description": "a song about cat"},
        "tags": [{"name": "tag1", "provider": "testing"}],
        "watermarked": None,
        "bit_rate": 16000,
        "sample_rate": 44100,
        "category": "music",
        "genres": ["pop", "rock"],
        "audio_set": {
            "audio_set": "album",
            "set_position": 1,
            "set_url": "https://album.com/",
            "set_thumbnail": "https://album.com/thumbnail.jpg",
        },
        "set_position": 1,
        "alt_files": None,
        "provider": "testing_provider",
        "source": "testing_source",
        "ingestion_type": "provider_api",
        "audio_set_foreign_identifier": "12345",
    }
    args_dict.update(req_args_dict)

    test_audio = audio.Audio(**args_dict)
    actual_row = audio_store._create_tsv_row(test_audio)
    expect_row = (
        "\t".join(
            [
                "foreign_id",
                "https://landing_page.com",
                "https://audiourl.com",
                "https://thumbnail.com",
                "mp3",
                "\\N",
                "testlicense",
                "1.0",
                "tyler",
                "https://creatorurl.com",
                "agreatsong",
                '{"description": "a song about cat"}',
                '[{"name": "tag1", "provider": "testing"}]',
                "music",
                "\\N",
                "testing_provider",
                "testing_source",
                "provider_api",
                "200",
                "16000",
                "44100",
                '{"pop", "rock"}',
                '{"audio_set": "album", "set_position": "1", "set_url": "https://album.com/", '
                '"set_thumbnail": "https://album.com/thumbnail.jpg"}',
                "1",
                "\\N",
                "12345",
            ]
        )
        + "\n"
    )
    assert expect_row == actual_row

from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import HTTPError

from catalog.tests.dags.providers.provider_api_scripts.resources.json_load import (
    make_resource_json_func,
)
from common.licenses.licenses import LicenseInfo
from providers.provider_api_scripts.freesound import FreesoundDataIngester


fsd = FreesoundDataIngester()
AUDIO_FILE_SIZE = 16359


_get_resource_json = make_resource_json_func("freesound")


@pytest.fixture(autouse=True)
def freesound_module():
    old_get_set = fsd._get_set_info
    fsd._get_set_info = lambda x: ("foo", x)
    yield
    fsd._get_set_info = old_get_set


@pytest.fixture
def file_size_patch():
    with patch.object(fsd, "_get_audio_file_size") as get_file_size_mock:
        get_file_size_mock.return_value = AUDIO_FILE_SIZE
        yield


@pytest.fixture
def audio_data():
    yield _get_resource_json("audio_data_example.json")


def test_get_audio_pages_returns_correctly_with_no_data():
    actual_result = fsd.get_batch_data({})
    assert actual_result is None


def test_get_audio_pages_returns_correctly_with_empty_list():
    expect_result = []
    actual_result = fsd.get_batch_data({"results": [None, None, None]})
    assert actual_result == expect_result


@pytest.mark.parametrize(
    "exception_type",
    [
        # These are fine
        *FreesoundDataIngester.flaky_exceptions,
        # This should raise immediately
        pytest.param(ValueError, marks=pytest.mark.raises(exception=ValueError)),
    ],
)
def test_get_audio_file_size_retries_and_does_not_raise(exception_type, audio_data):
    expected_result = None
    # Patch the sleep function so it doesn't take long
    with patch.object(fsd.delayed_requester, "head") as head_patch, patch("time.sleep"):
        head_patch.side_effect = exception_type("whoops")
        actual_result = fsd.get_record_data(audio_data)

        assert head_patch.call_count == 3
        assert actual_result == expected_result


def test_get_audio_file_size_returns_None_when_preview_url_404s(audio_data):
    with patch.object(fsd.delayed_requester, "head") as head_patch:
        # Returns None when 404
        head_patch.return_value = None

        actual_result = fsd.get_record_data(audio_data)
        assert head_patch.call_count == 1
        assert actual_result is None


def test_get_query_params_increments_page_number():
    first_qp = fsd.get_next_query_params(None)
    second_qp = fsd.get_next_query_params(first_qp)
    first_page = first_qp.pop("page")
    second_page = second_qp.pop("page")
    # Should be the same beyond that
    assert first_qp == second_qp
    assert second_page == first_page + 1


def test_get_items(file_size_patch):
    first_response = _get_resource_json("page.json")
    expected_audio_count = 6
    actual_audio_count = fsd.process_batch(first_response)
    assert actual_audio_count == expected_audio_count


def test_handles_failure_to_get_set_info():
    fsd = FreesoundDataIngester()
    # Patch the sleep function so it doesn't take long
    with patch.object(fsd.delayed_requester, "get") as get_mock, patch("time.sleep"):
        error_response = MagicMock()
        error_response.status_code = 404
        get_mock.side_effect = HTTPError(response=error_response)

        actual_id, actual_name, actual_url = fsd._get_audio_set_info(
            {"pack": "https://freesound.org/apiv2/packs/35596/"}
        )

        assert get_mock.call_count == 4
        assert actual_url == "https://freesound.org/apiv2/packs/35596/"
        assert actual_id is None
        assert actual_name is None


def test_get_audio_files_handles_example_audio_data(audio_data, file_size_patch):
    actual = fsd._get_audio_files(audio_data)
    expected = (
        {
            "url": "https://freesound.org/data/previews/415/415362_6044691-hq.mp3",
            "bit_rate": 128000,
            "filesize": AUDIO_FILE_SIZE,
            "filetype": "mp3",
        },
        [
            {
                "bit_rate": 1381000,
                "filesize": 107592,
                "filetype": "wav",
                "sample_rate": 44100,
                "url": "https://freesound.org/apiv2/sounds/415362/download/",
            }
        ],
    )
    assert actual == expected


def test_get_audio_files_returns_none_when_missing_previews(audio_data):
    audio_data.pop("previews", None)
    actual = fsd._get_audio_files(audio_data)
    assert actual == (None, None)


def test_get_audio_files_returns_none_when_missing_preferred_preview(audio_data):
    audio_data["previews"].pop(fsd.preferred_preview)
    actual = fsd._get_audio_files(audio_data)
    assert actual == (None, None)


def test_get_audio_files_returns_none_when_unable_to_get_filesize(audio_data):
    # Mimics a 404 when attempting to get filesize information from the preview url
    with patch.object(fsd.delayed_requester, "head") as head_patch:
        head_patch.return_value = None

        actual = fsd._get_audio_files(audio_data)
        assert actual == (None, None)


@pytest.mark.parametrize(
    "missing_fields",
    [
        ("id",),
        ("url", "download"),
        ("license",),
    ],
)
def test_get_record_data_returns_none_when_missing_data(missing_fields, audio_data):
    for field in missing_fields:
        audio_data.pop(field, None)
    actual = fsd.get_record_data(audio_data)
    assert actual is None


@pytest.mark.parametrize(
    "missing_fields",
    [
        ("id",),
        ("url", "download"),
        ("license",),
    ],
)
def test_get_record_data_returns_none_when_data_falsy(missing_fields, audio_data):
    for field in missing_fields:
        audio_data[field] = ""
    actual = fsd.get_record_data(audio_data)
    assert actual is None


def test_get_audio_set_info(audio_data):
    set_foreign_id, audio_set, set_url = fsd._get_audio_set_info(audio_data)
    expected_audio_set_info = (
        "foo",
        "https://freesound.org/apiv2/packs/23434/",
        "https://freesound.org/apiv2/packs/23434/",
    )
    assert (set_foreign_id, audio_set, set_url) == expected_audio_set_info


@pytest.mark.parametrize(
    "creator_data, expected_creator, expected_creator_url",
    [
        (
            {"username": "owly-bee"},
            "owly-bee",
            "https://freesound.org/people/owly-bee/",
        ),
        (
            {"username": "Dingle Brumbus"},
            "Dingle Brumbus",
            "https://freesound.org/people/Dingle%20Brumbus/",
        ),
        ({}, None, None),
    ],
)
def test_get_creator_data(creator_data, expected_creator, expected_creator_url):
    actual_creator, actual_creator_url = fsd._get_creator_data(creator_data)
    assert actual_creator == expected_creator
    assert actual_creator_url == expected_creator_url


def test_extract_audio_data_handles_example_dict(audio_data, file_size_patch):
    actual_audio_info = fsd.get_record_data(audio_data)
    expected_audio_info = {
        "alt_files": [
            {
                "bit_rate": 1381000,
                "filesize": 107592,
                "filetype": "wav",
                "sample_rate": 44100,
                "url": "https://freesound.org/apiv2/sounds/415362/download/",
            },
        ],
        "audio_set": "https://freesound.org/apiv2/packs/23434/",
        "url": "https://freesound.org/data/previews/415/415362_6044691-hq.mp3",
        "bit_rate": 128000,
        "creator": "owly-bee",
        "creator_url": "https://freesound.org/people/owly-bee/",
        "duration": 608,
        "filesize": AUDIO_FILE_SIZE,
        "filetype": "mp3",
        "foreign_identifier": 415362,
        "foreign_landing_url": "https://freesound.org/people/owly-bee/sounds/415362/",
        "license_info": LicenseInfo(
            license="by",
            version="3.0",
            url="https://creativecommons.org/licenses/by/3.0/",
            raw_url="http://creativecommons.org/licenses/by/3.0/",
        ),
        "meta_data": {
            "description": "A disinterested noise in a somewhat low tone.",
            "download": "https://freesound.org/apiv2/sounds/415362/download/",
            "num_downloads": 164,
        },
        "raw_tags": ["eh", "disinterest", "low", "uh", "voice", "uncaring"],
        "audio_set_foreign_identifier": "foo",
        "set_url": "https://freesound.org/apiv2/packs/23434/",
        "title": "Ehh disinterested.wav",
    }
    assert actual_audio_info == expected_audio_info


def test_get_tags(audio_data, file_size_patch):
    item_data = fsd.get_record_data(audio_data)
    actual_tags = item_data["raw_tags"]
    expected_tags = ["eh", "disinterest", "low", "uh", "voice", "uncaring"]
    assert expected_tags == actual_tags

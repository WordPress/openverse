import json
from pathlib import Path
from unittest.mock import patch

import pytest
from common.licenses.licenses import LicenseInfo
from providers.provider_api_scripts import freesound
from requests.exceptions import SSLError


RESOURCES = Path(__file__).parent.resolve() / "resources/freesound"


@pytest.fixture(autouse=True)
def freesound_module():
    old_get_set = freesound._get_set_info
    freesound._get_set_info = lambda x: ("foo", x)
    yield
    freesound._get_set_info = old_get_set


@pytest.fixture
def audio_data():
    AUDIO_DATA_EXAMPLE = RESOURCES / "audio_data_example.json"
    with open(AUDIO_DATA_EXAMPLE) as f:
        yield json.load(f)


def test_get_audio_pages_returns_correctly_with_none_json():
    expect_result = None
    with patch.object(
        freesound.delayed_requester, "get_response_json", return_value=None
    ):
        actual_result = freesound._get_batch_json()
    assert actual_result == expect_result


def test_get_audio_pages_returns_correctly_with_no_results():
    expect_result = None
    with patch.object(
        freesound.delayed_requester, "get_response_json", return_value={}
    ):
        actual_result = freesound._get_batch_json()
    assert actual_result == expect_result


def test_get_audio_file_size_retries_and_does_not_raise(audio_data):
    expected_result = None
    with patch("requests.head") as head_patch:
        head_patch.side_effect = SSLError("whoops")
        actual_result = freesound._extract_audio_data(audio_data)

        assert head_patch.call_count == 3
        assert actual_result == expected_result


def test_get_query_params_adds_page_number():
    actual_qp = freesound._get_query_params(page_number=2)
    assert actual_qp["page"] == str(2)


def test_get_query_params_leaves_other_keys():
    actual_qp = freesound._get_query_params(
        page_number=200, default_query_params={"test": "value"}
    )
    assert actual_qp["test"] == "value"
    assert len(actual_qp.keys()) == 3


def test_get_items():
    with open(RESOURCES / "page.json") as f:
        first_response = json.load(f)
    with patch.object(freesound, "_get_batch_json", side_effect=[first_response, []]):
        expected_audio_count = 6
        actual_audio_count = freesound._get_items(
            license_name="Attribution", date="all"
        )
        assert expected_audio_count == actual_audio_count


@pytest.mark.parametrize("has_nones", [False, True])
def test_process_item_batch_handles_example_batch(has_nones, audio_data):
    items_batch = [audio_data]
    if has_nones:
        items_batch = [None, None, audio_data, None]
    with patch.object(freesound.audio_store, "add_item", return_value=1) as mock_add:
        freesound._process_item_batch(items_batch)
        mock_add.assert_called_once()
        _, actual_call_args = mock_add.call_args_list[0]
        expected_call_args = {
            "alt_files": [
                {
                    "bit_rate": 1381000,
                    "filesize": 107592,
                    "filetype": "wav",
                    "sample_rate": 44100,
                    "url": "https://freesound.org/apiv2/sounds/415362/download/",
                }
            ],
            "audio_set": "https://freesound.org/apiv2/packs/23434/",
            "audio_url": "https://freesound.org/data/previews/415/415362_6044691-hq.mp3",
            "bit_rate": 128000,
            "category": "sound",
            "creator": "owly-bee",
            "creator_url": "https://freesound.org/people/owly-bee/",
            "duration": 608,
            "filesize": 16359,
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
            "set_foreign_id": "foo",
            "set_url": "https://freesound.org/apiv2/packs/23434/",
            "title": "Ehh disinterested.wav",
        }
        assert actual_call_args == expected_call_args


def test_extract_audio_data_returns_none_when_no_foreign_id(audio_data):
    audio_data.pop("id", None)
    actual_audio_info = freesound._extract_audio_data(audio_data)
    expected_audio_info = None
    assert actual_audio_info is expected_audio_info


def test_extract_audio_data_returns_none_when_no_audio_url(audio_data):
    audio_data.pop("url", None)
    audio_data.pop("download", None)
    actual_audio_info = freesound._extract_audio_data(audio_data)
    assert actual_audio_info is None


def test_extract_audio_data_returns_none_when_no_license(audio_data):
    audio_data.pop("license", None)
    actual_audio_info = freesound._extract_audio_data(audio_data)
    assert actual_audio_info is None


def test_get_audio_set_info(audio_data):
    set_foreign_id, audio_set, set_url = freesound._get_audio_set_info(audio_data)
    expected_audio_set_info = (
        "foo",
        "https://freesound.org/apiv2/packs/23434/",
        "https://freesound.org/apiv2/packs/23434/",
    )
    assert (set_foreign_id, audio_set, set_url) == expected_audio_set_info


def test_get_creator_data(audio_data):
    actual_creator, actual_creator_url = freesound._get_creator_data(audio_data)
    expected_creator = "owly-bee"
    expected_creator_url = "https://freesound.org/people/owly-bee/"

    assert actual_creator == expected_creator
    assert actual_creator_url == expected_creator_url


def test_get_creator_data_returns_none_when_no_artist(audio_data):
    audio_data.pop("username", None)
    actual_creator, actual_creator_url = freesound._get_creator_data(audio_data)

    assert actual_creator is None
    assert actual_creator_url is None


def test_extract_audio_data_handles_example_dict(audio_data):
    actual_audio_info = freesound._extract_audio_data(audio_data)
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
        "audio_url": "https://freesound.org/data/previews/415/415362_6044691-hq.mp3",
        "bit_rate": 128000,
        "category": "sound",
        "creator": "owly-bee",
        "creator_url": "https://freesound.org/people/owly-bee/",
        "duration": 608,
        "filesize": 16359,
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
        "set_foreign_id": "foo",
        "set_url": "https://freesound.org/apiv2/packs/23434/",
        "title": "Ehh disinterested.wav",
    }
    assert actual_audio_info == expected_audio_info


def test_get_tags(audio_data):
    item_data = freesound._extract_audio_data(audio_data)
    actual_tags = item_data["raw_tags"]
    expected_tags = ["eh", "disinterest", "low", "uh", "voice", "uncaring"]
    assert expected_tags == actual_tags

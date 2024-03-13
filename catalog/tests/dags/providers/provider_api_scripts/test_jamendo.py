from unittest.mock import patch

import pytest

from catalog.tests.dags.providers.provider_api_scripts.resources.json_load import (
    make_resource_json_func,
)
from common.licenses import LicenseInfo
from providers.provider_api_scripts.jamendo import JamendoDataIngester


_get_resource_json = make_resource_json_func("jamendo")


@pytest.fixture(autouse=True)
def rewrite_redirected_url():
    with (
        patch(
            "providers.provider_api_scripts.jamendo.rewrite_redirected_url"
        ) as class_mock,
        patch("common.urls.rewrite_redirected_url") as module_mock,
    ):
        # Prevent calling out to Jamendo & speed up tests
        # We need to patch it in both namespaces because `rewrite_redirected_url` is used
        # directly in the JamendoDataIngester, as well as by `get_license_info`.
        class_mock.side_effect = lambda x: x
        module_mock.side_effect = lambda x: x
        yield


jamendo = JamendoDataIngester()


@pytest.mark.parametrize(
    "url, param, expected",
    [
        ("", "", ""),
        ("https://example.com?a=1&b=2", "a", "https://example.com?b=2"),
        ("https://example.com?a=1", "a", "https://example.com"),
        ("https://example.com/?a=1", "a", "https://example.com/"),
        ("https://example.com?a=1&a=2&b=3", "a", "https://example.com?b=3"),
        ("https://example.com?a=1&a=2", "a", "https://example.com"),
        ("https://example.com?a=1&b=2", "notexist", "https://example.com?a=1&b=2"),
    ],
)
def test_remove_param_from_url(url, param, expected):
    actual = jamendo._remove_param_from_url(url, param)
    assert actual == expected


@pytest.mark.parametrize("json", [None, {}])  # No results
def test_get_batch_data_returns_correctly(json):
    assert jamendo.get_batch_data(json) is None


def test_get_next_query_params_adds_offset():
    actual_qp = jamendo.get_next_query_params({"offset": 0})
    assert actual_qp["offset"] == 200


def test_get_next_query_params_leaves_other_keys():
    actual_qp = jamendo.get_next_query_params({"offset": 200, "test": "value"})
    assert actual_qp["test"] == "value"
    assert len(actual_qp.keys()) == 2


def test_get_record_data():
    item_data = _get_resource_json("audio_data_example.json")
    actual = jamendo.get_record_data(item_data)
    expected = {
        "audio_set": "Opera I",
        "url": "https://mp3d.jamendo.com/?trackid=732&format=mp32",
        "category": "music",
        "creator": "Haeresis",
        "creator_url": "https://www.jamendo.com/artist/92/haeresis",
        "duration": 144000,
        "filetype": "mp32",
        "foreign_identifier": "732",
        "foreign_landing_url": "https://www.jamendo.com/track/732",
        "genres": [],
        "license_info": LicenseInfo(
            license="by-nc",
            version="2.0",
            url="https://creativecommons.org/licenses/by-nc/2.0/",
            raw_url="http://creativecommons.org/licenses/by-nc/2.0/",
        ),
        "meta_data": {
            "downloads": 0,
            "listens": 5616,
            "playlists": 0,
            "release_date": "2005-04-12",
            "audiodownload_allowed": True,
        },
        "raw_tags": {"instrumental", "speed_medium"},
        "audio_set_foreign_identifier": "119",
        "set_position": 6,
        "set_thumbnail": "https://usercontent.jamendo.com/?type=album&id=119&width=200",
        "set_url": "https://www.jamendo.com/album/119/opera-i",
        "thumbnail_url": "https://usercontent.jamendo.com/?type=album&id=119&width=200&trackid=732",
        "title": "Thoughtful",
    }
    assert actual == expected


@pytest.mark.parametrize(
    "required_field",
    [
        pytest.param("id", id="id-foreign_identifier"),
        pytest.param("shareurl", id="shareurl-foreign_landing_url"),
        pytest.param("audio", id="audio-audio_url"),
        pytest.param("license_ccurl", id="license_ccurl-license_info"),
    ],
)
def test_get_record_data_returns_none_when_required_data_is_null(required_field):
    audio_data = _get_resource_json("audio_data_example.json")
    audio_data.pop(required_field, None)
    assert jamendo.get_record_data(audio_data) is None


@pytest.mark.parametrize(
    "required_field",
    [
        # TODO: uncomment when the stricter checks for required parameters are merged
        # pytest.param("id", id="id-foreign_identifier"),
        # pytest.param("shareurl", id="shareurl-foreign_landing_url"),
        # pytest.param("audio", id="audio-audio_url"),
        pytest.param("license_ccurl", id="license_ccurl-license_info"),
    ],
)
def test_get_record_data_returns_none_when_required_data_is_falsy(required_field):
    audio_data = _get_resource_json("audio_data_example.json")
    audio_data[required_field] = ""
    assert jamendo.get_record_data(audio_data) is None


def test_get_record_data_handles_no_creator_url():
    audio_data = _get_resource_json("audio_data_example.json")
    audio_data.pop("artist_idstr", None)
    expected_creator = "Haeresis"

    actual_data = jamendo.get_record_data(audio_data)
    assert actual_data.get("creator") == expected_creator
    assert actual_data.get("creator_url") is None


def test_get_record_data_handles_no_artist():
    audio_data = _get_resource_json("audio_data_example.json")
    audio_data.pop("artist_name", None)
    actual_data = jamendo.get_record_data(audio_data)

    assert actual_data.get("creator") is None
    assert actual_data.get("creator_url") is None


def test_get_tags():
    item_data = {
        "musicinfo": {
            "vocalinstrumental": "vocal",
            "gender": "male",
            "speed": "medium",
            "tags": {
                "genres": ["pop", "rock"],
                "instruments": [],
                "vartags": ["engage", "vocal"],
            },
        }
    }
    expected_tags = {"vocal", "male", "speed_medium", "engage"}
    actual_tags = jamendo._get_tags(item_data)
    assert expected_tags == actual_tags


@pytest.mark.parametrize(
    "url, expected",
    [
        (None, None),
        ("", ""),
        (
            "https://usercontent.jamendo.com?type=album&id=100007&width=300",
            "https://usercontent.jamendo.com/?type=album&id=100007&width=300",
        ),
        (
            "https://usercontent.jamendo.com/some-other-page/subpage?type=album&id=100007&width=300",
            "https://usercontent.jamendo.com/some-other-page/subpage/?type=album&id=100007&width=300",
        ),
    ],
)
def test_add_trailing_slash(url, expected):
    actual = jamendo._add_trailing_slash(url)
    assert actual == expected


@pytest.mark.parametrize(
    "thumbnail_url, expected",
    [
        (
            "https://usercontent.jamendo.com/?type=album&id=100007&width=300&trackid=100007",
            "https://usercontent.jamendo.com/?type=album&id=100007&width=300",
        ),
        (
            "https://usercontent.jamendo.com/?type=album&id=100007&width=300",
            "https://usercontent.jamendo.com/?type=album&id=100007&width=300",
        ),
        (None, None),
        ("", None),
    ],
)
def test_remove_track_id_handles_data(thumbnail_url, expected):
    actual = jamendo._remove_trackid(thumbnail_url)
    assert actual == expected

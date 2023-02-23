import json
import os

import pytest
from common.licenses import LicenseInfo
from providers.provider_api_scripts.flickr import FlickrDataIngester


RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources/flickr")

FROZEN_DATE = "2020-04-01"
flickr = FlickrDataIngester(date=FROZEN_DATE)
test_license_info = LicenseInfo(
    "by-nc-sa",
    "2.0",
    "https://creativecommons.org/licenses/by-nc-sa/2.0/",
    None,
)


def _get_resource_json(json_name):
    with open(os.path.join(RESOURCES, json_name)) as f:
        resource_json = json.load(f)
    return resource_json


def test_get_next_query_params():
    expected_params = {
        "min_upload_date": "1516060900",
        "max_upload_date": "1516060800",
        "page": 0,
        "api_key": "not_set",
        "license": "1,2,3,4,5,6,9,10",
        "per_page": 500,
        "method": "flickr.photos.search",
        "media": "photos",
        "safe_search": 1,  # Restrict to 'safe'
        "extras": (
            "description,license,date_upload,date_taken,owner_name,tags,o_dims,"
            "url_t,url_s,url_m,url_l,views,content_type"
        ),
        "format": "json",
        "nojsoncallback": 1,
    }
    # Set the api key
    flickr.api_key = "not_set"

    # First request
    first_params = flickr.get_next_query_params(
        None, start_ts="1516060900", end_ts="1516060800"
    )
    assert first_params == expected_params

    # Updated page on second request
    second_params = flickr.get_next_query_params(
        first_params, start_ts="1516060900", end_ts="1516060800"
    )
    assert second_params == {**expected_params, "page": 1}


def test_get_media_type():
    assert flickr.get_media_type({}) == "image"


def test_get_record_count_from_response():
    response_json = _get_resource_json("flickr_example_pretty.json")
    count = flickr.get_record_count_from_response(response_json)

    assert count == 30


@pytest.mark.parametrize(
    "response_json, expected_response",
    [
        # Realistic full response
        (
            _get_resource_json("flickr_example_pretty.json"),
            _get_resource_json("flickr_example_photo_list.json"),
        ),
        # Partial response (has `photos` but no `photo`)
        (
            {
                "photos": {"page": 1, "pages": 1, "perpage": 500, "total": "30"},
                "stat": "ok",
            },
            None,
        ),
        # Empty photos list
        ({"stat": "ok", "photos": {}}, None),
        # No photos list
        ({"stat": "ok", "abc": "def"}, None),
        # Not Ok stat
        ({"stat": "notok", "abc": "def"}, None),
        # None
        (None, None),
    ],
)
def test_get_batch_data(response_json, expected_response):
    actual_response = flickr.get_batch_data(response_json)
    assert actual_response == expected_response


def test_get_record_data():
    image_data = _get_resource_json("image_data_complete_example.json")
    actual_data = flickr.get_record_data(image_data)

    expect_meta_data = {
        "pub_date": "1581318235",
        "date_taken": "2020-02-10 09:38:16",
        "views": "70",
        "description": (
            "We had spectacular underwater scenery with great visibility "
            "today despite the big seas and winds at Lord Howe Island."
        ),
    }

    expected_data = {
        "foreign_landing_url": "https://www.flickr.com/photos/71925535@N03/49514824541",
        "image_url": (
            "https://live.staticflickr.com/65535/49514824541_35d1b4f8db" "_b.jpg"
        ),
        "license_info": test_license_info,
        "foreign_identifier": "49514824541",
        "width": 1024,
        "height": 683,
        "creator": "Marine Explorer",
        "creator_url": "https://www.flickr.com/photos/71925535@N03",
        "title": "Surveying Ruperts Reef @reeflifesurvey #lapofaus #marineexplorer",
        "meta_data": expect_meta_data,
        "raw_tags": [
            "australia",
            "marine",
            "marineexplorer",
            "nature",
            "scuba",
            "underwater",
        ],
        "source": flickr.provider_string,
        "category": "photograph",
    }
    assert actual_data == expected_data


def test_get_record_data_returns_none_when_missing_owner():
    image_data = _get_resource_json("image_data_complete_example.json")
    image_data.pop("owner")

    actual_data = flickr.get_record_data(image_data)
    assert actual_data is None


def test_get_record_data_returns_none_when_missing_foreign_id():
    image_data = _get_resource_json("image_data_complete_example.json")
    image_data.pop("id")

    actual_data = flickr.get_record_data(image_data)
    assert actual_data is None


@pytest.mark.parametrize(
    "args",
    [
        # No trailing slashes
        ["https://aurl.com", "path", "morepath", "lastpath"],
        # Slashes
        ["https://aurl.com/", "/path/", "/morepath/", "lastpath"],
    ],
)
def test_url_join_no_trailing_slashes(args):
    expect_url = "https://aurl.com/path/morepath/lastpath"
    actual_url = flickr._url_join(*args)
    assert expect_url == actual_url


@pytest.mark.parametrize(
    "image_data, expected_size",
    [
        # No image detected
        (_get_resource_json("image_data_no_image_url.json"), None),
        # Large size available
        (_get_resource_json("image_data_with_large_url_available.json"), "l"),
        # Large not available, but medium is
        (_get_resource_json("image_data_with_med_url_available.json"), "m"),
        # Falls back to small when large and medium not available
        (_get_resource_json("image_data_with_small_url_available.json"), "s"),
    ],
)
def test_get_largest_image_size(image_data, expected_size):
    actual_size = flickr._get_largest_image_size(image_data)
    assert actual_size == expected_size


@pytest.mark.parametrize(
    "license_id, expected_license_info",
    [
        # integer id
        (1, test_license_info),
        # string id
        ("1", test_license_info),
        # id that does not map to anything in the LICENSE_INFO list
        (99999999999, None),
    ],
)
def test_get_license(license_id, expected_license_info):
    actual_license_info = flickr._get_license_info({"license": license_id})
    assert actual_license_info == expected_license_info


@pytest.mark.parametrize(
    "image_data, expected_meta_data",
    [
        # Happy path
        (
            _get_resource_json("image_data_full_meta_data_example.json"),
            {
                "pub_date": "1571326372",
                "date_taken": "2019-09-07 16:26:44",
                "description": "OLYMPUS DIGITAL CAMERA",
                "views": "9",
            },
        ),
        # Partial meta data dict, does not include None fields
        (
            _get_resource_json("image_data_partial_meta_data_info.json"),
            {"pub_date": "1571326372", "date_taken": "2019-09-07 16:26:44"},
        ),
        # Empty meta data dict, no data available
        (_get_resource_json("image_data_no_meta_data_info.json"), {}),
        # Meta data containing html description that should be stripped
        (
            _get_resource_json("image_data_html_description.json"),
            _get_resource_json("expect_meta_data_from_html_description.json"),
        ),
        # Meta data contains whitespace in the description that should be stripped
        (
            _get_resource_json("image_data_whitespace_description.json"),
            _get_resource_json("expect_meta_data_from_whitespace_description.json"),
        ),
    ],
)
def test_create_meta_data(image_data, expected_meta_data):
    actual_meta_data = flickr._create_meta_data_dict(image_data)
    assert actual_meta_data == expected_meta_data


@pytest.mark.parametrize(
    "image_data, expected_tags_list",
    [
        # Happy path, handles whitespace
        (
            _get_resource_json("image_data_varying_tags_whitespace.json"),
            ["tag1", "tag2", "tag3"],
        ),
        # Sorts tags
        (_get_resource_json("image_data_unsorted_tags.json"), ["tag1", "tag2", "tag3"]),
        # Truncates long tags
        (
            _get_resource_json("image_data_long_tags_string.json"),
            ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6"],
        ),
        # Returns None when no tags key
        ({"id": "aslkjb"}, None),
        # Returns None when empty tags
        ({"id": "aslkjb", "tags": ""}, None),
    ],
)
def test_create_tags_list(image_data, expected_tags_list):
    actual_tags_list = flickr._create_tags_list(image_data, max_tag_string_length=37)
    assert actual_tags_list == expected_tags_list


def test_get_record_data_with_sub_provider():
    image_data = _get_resource_json("image_data_sub_provider_example.json")
    actual_data = flickr.get_record_data(image_data)

    expect_meta_data = {
        "pub_date": "1590799192",
        "date_taken": "2020-05-29 13:50:27",
        "views": "28597",
        "description": (
            "A gopher tortoise is seen making its way towards its burrow near"
            " Launch Complex 39A as preparations continue for NASA SpaceX "
            "Demo-2 mission"
        ),
    }

    expected_data = {
        "foreign_landing_url": (
            "https://www.flickr.com/photos/35067687@N04/49950595947"
        ),
        "image_url": (
            "https://live.staticflickr.com/65535/49950595947_65a3560ddc" "_b.jpg"
        ),
        "license_info": test_license_info,
        "foreign_identifier": "49950595947",
        "width": 1024,
        "height": 683,
        "creator": "NASA HQ PHOTO",
        "creator_url": "https://www.flickr.com/photos/35067687@N04",
        "title": "SpaceX Demo-2 Preflight (NHQ202005290001)",
        "meta_data": expect_meta_data,
        "raw_tags": [
            "capecanaveral",
            "commercialcrewprogram",
            "gophertortoise",
            "kennedyspacecenter",
            "nasa",
            "spacex",
        ],
        "source": "nasa",
        "category": None,
    }
    assert actual_data == expected_data

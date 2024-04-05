from datetime import datetime
from unittest import mock

import pytest

from catalog.tests.dags.providers.provider_api_scripts.resources.json_load import (
    make_resource_json_func,
)
from common.licenses import LicenseInfo
from providers.provider_api_scripts.flickr import FlickrDataIngester


FROZEN_DATE = "2020-04-01"
flickr = FlickrDataIngester(date=FROZEN_DATE)
test_license_info = LicenseInfo(
    "by-nc-sa",
    "2.0",
    "https://creativecommons.org/licenses/by-nc-sa/2.0/",
    None,
)


_get_resource_json = make_resource_json_func("flickr")


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


@pytest.mark.parametrize(
    "process_large_batch, page_number, expected_response, expected_large_batches",
    [
        # process_large_batch is False: always return None and add batch to the list
        (False, 1, None, 1),
        (False, 20, None, 1),
        # process_large_batch is True: never add batch to the list
        # Fewer than max_unique_records have been processed
        (True, 1, _get_resource_json("flickr_example_photo_list.json"), 0),
        (True, 10, _get_resource_json("flickr_example_photo_list.json"), 0),
        # More than max_unique_records have been processed
        (True, 11, None, 0),
        (True, 20, None, 0),
    ],
)
def test_get_batch_data_when_detected_count_exceeds_max_unique_records(
    process_large_batch, page_number, expected_response, expected_large_batches
):
    # Hard code the batch_limit and max_unique_records for the test
    ingester = FlickrDataIngester(date=FROZEN_DATE)
    # This means you should be able to get 100/10 = 10 pages of results before
    # you exceed the max_unique_records.
    ingester.batch_limit = 10
    ingester.max_unique_records = 100
    ingester.process_large_batch = process_large_batch

    response_json = _get_resource_json("flickr_example_pretty.json")
    response_json["photos"]["page"] = page_number
    response_json["photos"]["total"] = 200  # More than max unique records

    actual_response = ingester.get_batch_data(response_json)
    assert actual_response == expected_response

    assert len(ingester.large_batches) == expected_large_batches


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
        "url": ("https://live.staticflickr.com/65535/49514824541_35d1b4f8db" "_b.jpg"),
        "license_info": test_license_info,
        "foreign_identifier": "49514824541",
        "width": 1024,
        "height": 683,
        "creator": "Marine Explorer",
        "creator_url": "https://www.flickr.com/photos/71925535@N03",
        "title": "Surveying Ruperts Reef @reeflifesurvey #lapofaus #marineexplorer",
        "meta_data": expect_meta_data,
        "raw_tags": [
            "scuba",
            "nature",
            "marine",
            "underwater",
            "australia",
            "marineexplorer",
        ],
        "source": flickr.provider_string,
        "category": "photograph",
    }
    assert actual_data == expected_data


@pytest.mark.parametrize(
    "missing_params",
    [
        pytest.param(["owner"], id="owner-foreign_landing_url"),
        pytest.param(["license"], id="license"),
        pytest.param(["url_l", "url_m", "url_s"], id="url_x-url"),
        pytest.param(["id"], id="id-foreign_identifier"),
    ],
)
def test_get_record_data_returns_none_when_missing_required_params(missing_params):
    image_data = _get_resource_json("image_data_complete_example.json")
    for param in missing_params:
        image_data.pop(param)

    actual_data = flickr.get_record_data(image_data)
    assert actual_data is None


@pytest.mark.parametrize(
    "falsy_params",
    [
        pytest.param(["owner"], id="owner-foreign_landing_url"),
        pytest.param(["license"], id="license"),
        pytest.param(["url_l", "url_m", "url_s"], id="url_x-url"),
        pytest.param(["id"], id="id-foreign_identifier"),
    ],
)
def test_get_record_data_returns_none_when_required_params_falsy(falsy_params):
    image_data = _get_resource_json("image_data_complete_example.json")
    for param in falsy_params:
        image_data[param] = ""

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
            {"tags": "tag1 tag2   tag3  tag3 "},
            ["tag1", "tag2", "tag3", "tag3"],
        ),
        # Truncates long tags
        (
            {"tags": "tag1 tag2   tag3  tag3 tag4 tag5 tag6 tag7"},
            ["tag1", "tag2", "tag3", "tag3", "tag4", "tag5", "tag6"],
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
        "url": ("https://live.staticflickr.com/65535/49950595947_65a3560ddc" "_b.jpg"),
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
            "spacex",
            "nasa",
            "kennedyspacecenter",
        ],
        "source": "nasa",
        "category": None,
    }
    assert actual_data == expected_data


def test_ingest_records():
    # Test a 'normal' run where no large batches are detected during ingestion.
    with (
        mock.patch(
            "providers.provider_api_scripts.time_delineated_provider_data_ingester.TimeDelineatedProviderDataIngester.ingest_records"
        ),
        mock.patch(
            "providers.provider_api_scripts.time_delineated_provider_data_ingester.TimeDelineatedProviderDataIngester.ingest_records_for_timestamp_pair"
        ) as ingest_for_pair_mock,
    ):
        flickr.ingest_records()
        # No additional calls to ingest_records_for_timestamp_pair were made
        assert not ingest_for_pair_mock.called


def test_ingest_records_when_large_batches_detected():
    ingester = FlickrDataIngester(date=FROZEN_DATE)
    with (
        mock.patch(
            "providers.provider_api_scripts.time_delineated_provider_data_ingester.TimeDelineatedProviderDataIngester.ingest_records"
        ),
        mock.patch(
            "providers.provider_api_scripts.time_delineated_provider_data_ingester.TimeDelineatedProviderDataIngester.ingest_records_for_timestamp_pair"
        ) as ingest_for_pair_mock,
    ):
        # Set large_batches to include one timestamp pair
        mock_start = datetime(2020, 1, 1, 1, 0, 0)
        mock_end = datetime(2020, 1, 1, 2, 0, 0)
        ingester.large_batches = [
            (mock_start, mock_end),
        ]

        ingester.ingest_records()
        # An additional call made to ingest_records_for_timestamp_pair for each license type
        assert ingest_for_pair_mock.call_count == 8

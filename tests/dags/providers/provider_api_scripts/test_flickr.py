import json
import os
from unittest.mock import MagicMock, patch

from common.licenses import LicenseInfo
from providers.provider_api_scripts import flickr
from requests import Response, codes


RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources/flickr")


def _get_resource_json(json_name):
    with open(os.path.join(RESOURCES, json_name)) as f:
        resource_json = json.load(f)
    return resource_json


def test_derive_timestamp_pair_list_with_undivided_day():
    # Note that the timestamps are derived as if input was in UTC.
    actual_pair_list = flickr._derive_timestamp_pair_list("2018-01-15", day_division=1)
    expect_pair_list = [("1515974400", "1516060800")]
    assert expect_pair_list == actual_pair_list


def test_derive_timestamp_pair_list_with_three_divided_day():
    actual_pair_list = flickr._derive_timestamp_pair_list("2018-01-15", day_division=3)
    expect_pair_list = [
        ("1515974400", "1516003200"),
        ("1516003200", "1516032000"),
        ("1516032000", "1516060800"),
    ]
    assert expect_pair_list == actual_pair_list


def test_derive_timestamp_pair_list_with_sub_hourly_day_divisions():
    actual_pair_list = flickr._derive_timestamp_pair_list("2018-01-15", day_division=40)
    expect_pair_list = [
        ("1515974400", "1515976560"),
        ("1515976560", "1515978720"),
        ("1515978720", "1515980880"),
        ("1515980880", "1515983040"),
        ("1515983040", "1515985200"),
        ("1515985200", "1515987360"),
        ("1515987360", "1515989520"),
        ("1515989520", "1515991680"),
        ("1515991680", "1515993840"),
        ("1515993840", "1515996000"),
        ("1515996000", "1515998160"),
        ("1515998160", "1516000320"),
        ("1516000320", "1516002480"),
        ("1516002480", "1516004640"),
        ("1516004640", "1516006800"),
        ("1516006800", "1516008960"),
        ("1516008960", "1516011120"),
        ("1516011120", "1516013280"),
        ("1516013280", "1516015440"),
        ("1516015440", "1516017600"),
        ("1516017600", "1516019760"),
        ("1516019760", "1516021920"),
        ("1516021920", "1516024080"),
        ("1516024080", "1516026240"),
        ("1516026240", "1516028400"),
        ("1516028400", "1516030560"),
        ("1516030560", "1516032720"),
        ("1516032720", "1516034880"),
        ("1516034880", "1516037040"),
        ("1516037040", "1516039200"),
        ("1516039200", "1516041360"),
        ("1516041360", "1516043520"),
        ("1516043520", "1516045680"),
        ("1516045680", "1516047840"),
        ("1516047840", "1516050000"),
        ("1516050000", "1516052160"),
        ("1516052160", "1516054320"),
        ("1516054320", "1516056480"),
        ("1516056480", "1516058640"),
        ("1516058640", "1516060800"),
    ]
    assert expect_pair_list == actual_pair_list


def test_derive_timestamp_pair_list_fall_back_to_48_day_divisions():
    fallback_pair_list = flickr._derive_timestamp_pair_list(
        "2018-01-15", day_division=49
    )
    correct_pair_list = flickr._derive_timestamp_pair_list(
        "2018-01-15", day_division=48
    )
    assert fallback_pair_list == correct_pair_list


def test_process_interval_skips_bad_pages():
    with patch.object(
        flickr, "_get_image_list", return_value=(None, 5)
    ) as mock_get_image_list:
        flickr._process_interval("1234", "5678", "test")

    assert mock_get_image_list.call_count == 5
    assert mock_get_image_list.called_with("1234", "5678", "test", 5)


def test_get_image_list_retries_with_none_response():
    with patch.object(
        flickr.delayed_requester, "get", return_value=Response()
    ) as mock_get:
        flickr._get_image_list("1234", "5678", "test", 4, max_tries=3)

    assert mock_get.call_count == 3


def test_get_image_list_retries_with_non_ok_response():
    response_json = _get_resource_json("flickr_example_pretty.json")
    r = Response()
    r.status_code = 504
    r.json = MagicMock(return_value=response_json)
    with patch.object(flickr.delayed_requester, "get", return_value=r) as mock_get:
        flickr._get_image_list("1234", "5678", "test", 4, max_tries=3)

    assert mock_get.call_count == 3


def test_get_image_list_with_partial_response():
    response_json = _get_resource_json("total_pages_but_no_image_list.json")
    r = Response()
    r.status_code = 200
    r.json = MagicMock(return_value=response_json)
    with patch.object(flickr.delayed_requester, "get", return_value=r) as mock_get:
        image_list, total_pages = flickr._get_image_list(
            "1234", "5678", "test", 4, max_tries=3
        )

    assert mock_get.call_count == 3


def test_get_image_list_with_realistic_response():
    response_json = _get_resource_json("flickr_example_pretty.json")
    r = Response()
    r.status_code = 200
    r.json = MagicMock(return_value=response_json)
    with patch.object(flickr.delayed_requester, "get", return_value=r) as mock_get:
        image_list, total_pages = flickr._get_image_list(
            "1234", "5678", "test", 4, max_tries=3
        )
    expect_image_list = _get_resource_json("flickr_example_photo_list.json")

    assert mock_get.call_count == 1
    assert image_list == expect_image_list
    assert total_pages == 1


# This test will fail if default constants change.
def test_build_query_param_dict_default():
    cur_time = "12345"
    nxt_time = "12346"
    flickr_api_key = "notset"
    actual_query_param_dict = flickr._build_query_param_dict(
        cur_time, nxt_time, 3, "test", api_key=flickr_api_key
    )
    expect_query_param_dict = {
        "method": "flickr.photos.search",
        "media": "photos",
        "safe_search": 1,
        "extras": (
            "description,license,date_upload,date_taken,owner_name,tags,"
            "o_dims,url_t,url_s,url_m,url_l,views,content_type"
        ),
        "format": "json",
        "nojsoncallback": 1,
        "min_test_date": cur_time,
        "max_test_date": nxt_time,
        "page": 3,
        "api_key": flickr_api_key,
        "license": "1,2,3,4,5,6,9,10",
        "per_page": 500,
    }
    assert actual_query_param_dict == expect_query_param_dict


def test_build_query_param_dict_with_givens():
    cur_time = "12345"
    nxt_time = "12346"
    flickr_api_key = "notset"
    actual_query_param_dict = flickr._build_query_param_dict(
        cur_time,
        nxt_time,
        3,
        "test",
        api_key=flickr_api_key,
        license_info={
            "1": ("by-nc-sa", "2.0"),
            "2": ("by-nc", "2.0"),
        },
        limit=10,
        default_query_param={
            "method": "flickr.photos.search",
            "media": "photos",
            "extras": "url_t,url_s,url_m,url_l,views",
            "nojsoncallback": 1,
        },
    )
    expect_query_param_dict = {
        "method": "flickr.photos.search",
        "media": "photos",
        "extras": "url_t,url_s,url_m,url_l,views",
        "nojsoncallback": 1,
        "min_test_date": cur_time,
        "max_test_date": nxt_time,
        "page": 3,
        "api_key": flickr_api_key,
        "license": "1,2",
        "per_page": 10,
    }
    assert actual_query_param_dict == expect_query_param_dict


def test_extract_image_list_from_json_handles_realistic_input():
    test_dict = _get_resource_json("flickr_example_pretty.json")
    expect_image_list = _get_resource_json("flickr_example_photo_list.json")
    expect_total_pages = 1
    actual_image_list, actual_total_pages = flickr._extract_image_list_from_json(
        test_dict
    )
    assert actual_image_list == expect_image_list
    assert actual_total_pages == expect_total_pages


def test_extract_image_list_from_json_handles_missing_photo_list():
    test_dict = {"stat": "ok", "photos": {}}
    assert flickr._extract_image_list_from_json(test_dict)[0] is None


def test_extract_image_list_from_json_handles_missing_photos():
    test_dict = {"stat": "ok", "abc": "def"}
    assert flickr._extract_image_list_from_json(test_dict) == (None, None)


def test_extract_image_list_from_json_returns_nones_given_non_ok_stat():
    test_dict = {"stat": "notok", "abc": "def"}
    assert flickr._extract_image_list_from_json(test_dict) == (None, None)


def test_extract_image_list_from_json_returns_nones_given_none_json():
    assert flickr._extract_image_list_from_json(None) == (None, None)


def test_process_image_data_with_real_example():
    image_data = _get_resource_json("image_data_complete_example.json")
    with patch.object(
        flickr, "_get_file_properties", return_value=(371862, "jpg")
    ), patch.object(flickr.image_store, "add_item", return_value=100) as mock_add_item:
        total_images = flickr._process_image_data(image_data)

    expect_meta_data = {
        "pub_date": "1581318235",
        "date_taken": "2020-02-10 09:38:16",
        "views": "70",
        "description": (
            "We had spectacular underwater scenery with great visibility "
            "today despite the big seas and winds at Lord Howe Island."
        ),
    }

    mock_add_item.assert_called_once_with(
        foreign_landing_url=("https://www.flickr.com/photos/71925535@N03/49514824541"),
        image_url=(
            "https://live.staticflickr.com/65535/49514824541_35d1b4f8db" "_b.jpg"
        ),
        thumbnail_url=(
            "https://live.staticflickr.com/65535/49514824541_35d1b4f8db" "_m.jpg"
        ),
        license_info=LicenseInfo(
            "by-nc-sa",
            "2.0",
            "https://creativecommons.org/licenses/by-nc-sa/2.0/",
            None,
        ),
        foreign_identifier="49514824541",
        width=1024,
        height=683,
        filesize=371862,
        filetype="jpg",
        creator="Marine Explorer",
        creator_url="https://www.flickr.com/photos/71925535@N03",
        title=("Surveying Ruperts Reef @reeflifesurvey #lapofaus " "#marineexplorer"),
        meta_data=expect_meta_data,
        raw_tags=[
            "australia",
            "marine",
            "marineexplorer",
            "nature",
            "scuba",
            "underwater",
        ],
        source=flickr.PROVIDER,
        category="photograph",
    )
    assert total_images == 100


def test_build_creator_url_nones_missing_owner():
    image_data = _get_resource_json("image_data_long_tags_string.json")
    actual_url = flickr._build_creator_url(
        image_data, photo_url_base="https://photo.com"
    )
    assert actual_url is None


def test_build_creator_url_finds_owner():
    image_data = _get_resource_json("image_data_complete_example.json")
    actual_url = flickr._build_creator_url(
        image_data, photo_url_base="https://photo.com"
    )
    expect_url = "https://photo.com/71925535@N03"
    assert actual_url == expect_url


def test_build_foreign_landing_url():
    actual_url = flickr._build_foreign_landing_url("https://creator.com", "foreignid")
    expect_url = "https://creator.com/foreignid"
    assert actual_url == expect_url


def test_build_foreign_landing_url_nones_with_falsy_foreign_id():
    actual_url = flickr._build_foreign_landing_url("https://creator.com", False)
    assert actual_url is None


def test_build_foreign_landing_url_nones_with_falsy_creator_url():
    assert flickr._build_foreign_landing_url("", "abcde") is None


def test_url_join_no_trailing_slashes():
    expect_url = "https://aurl.com/path/morepath/lastpath"
    actual_url = flickr._url_join("https://aurl.com", "path", "morepath", "lastpath")
    assert expect_url == actual_url


def test_url_join_with_slashes():
    expect_url = "https://aurl.com/path/morepath/lastpath"
    actual_url = flickr._url_join(
        "https://aurl.com/", "/path/", "/morepath/", "lastpath"
    )
    assert expect_url == actual_url


def test_get_image_url_returns_Nonetype_tuple_if_no_image():
    data = _get_resource_json("image_data_no_image_url.json")
    actual_tuple = flickr._get_image_url(data)
    expect_tuple = (None, None, None)
    assert expect_tuple == actual_tuple


def test_get_image_url_returns_large_tuple_when_avail():
    image_data = _get_resource_json("image_data_with_large_url_available.json")
    actual_tuple = flickr._get_image_url(image_data)
    expect_tuple = ("https://live.staticflickr.com/456_b.jpg", 768, 1024)
    assert expect_tuple == actual_tuple


def test_get_image_url_returns_medium_tuple_when_large_not_avail():
    data = _get_resource_json("image_data_with_med_url_available.json")
    actual_tuple = flickr._get_image_url(data)
    expect_tuple = ("https://live.staticflickr.com/456.jpg", 375, 500)
    assert expect_tuple == actual_tuple


def test_get_image_url_falls_to_small_tuple():
    data = _get_resource_json("image_data_with_small_url_available.json")
    actual_tuple = flickr._get_image_url(data)
    expect_tuple = ("https://live.staticflickr.com/456_m.jpg", 180, 240)
    assert expect_tuple == actual_tuple


def test_get_license_with_int_license_id():
    license_info = {
        "1": ("by-nc-sa", "2.0"),
        "2": ("by-nc", "2.0"),
    }
    actual_license, actual_license_version = flickr._get_license(
        2, license_info=license_info
    )
    expect_license, expect_license_version = "by-nc", "2.0"
    assert expect_license == actual_license
    assert expect_license_version == actual_license_version


def test_get_license_with_str_license_id():
    license_info = {
        "1": ("by-nc-sa", "2.0"),
        "2": ("by-nc", "2.0"),
    }
    actual_license, actual_license_version = flickr._get_license(
        "2", license_info=license_info
    )
    expect_license, expect_license_version = "by-nc", "2.0"
    assert expect_license == actual_license
    assert expect_license_version == actual_license_version


def test_get_license_with_missing_license_id():
    license_info = {
        "1": ("by-nc-sa", "2.0"),
        "2": ("by-nc", "2.0"),
    }
    actual_license, actual_license_version = flickr._get_license(
        12, license_info=license_info
    )
    assert actual_license is None
    assert actual_license_version is None


def test_create_meta_data_fills_meta_data_dict():
    data = _get_resource_json("image_data_full_meta_data_example.json")
    actual_dict = flickr._create_meta_data_dict(data)
    expect_dict = {
        "pub_date": "1571326372",
        "date_taken": "2019-09-07 16:26:44",
        "description": "OLYMPUS DIGITAL CAMERA",
        "views": "9",
    }
    assert expect_dict == actual_dict


def test_create_meta_data_fills_partial_meta_data_dict():
    data = _get_resource_json("image_data_partial_meta_data_info.json")
    actual_dict = flickr._create_meta_data_dict(data)
    expect_dict = {"pub_date": "1571326372", "date_taken": "2019-09-07 16:26:44"}
    assert expect_dict == actual_dict


def test_create_meta_data_makes_empty_meta_data_dict():
    data = _get_resource_json("image_data_no_meta_data_info.json")
    actual_dict = flickr._create_meta_data_dict(data)
    expect_dict = {}
    assert expect_dict == actual_dict


def test_create_meta_data_dict_strips_html():
    data = _get_resource_json("image_data_html_description.json")
    actual_dict = flickr._create_meta_data_dict(data)
    expect_dict = _get_resource_json("expect_meta_data_from_html_description.json")
    assert expect_dict == actual_dict


def test_create_meta_data_handles_whitespace_description():
    data = _get_resource_json("image_data_whitespace_description.json")
    actual_dict = flickr._create_meta_data_dict(data)
    expect_dict = _get_resource_json(
        "expect_meta_data_from_whitespace_description.json"
    )
    assert expect_dict == actual_dict


def test_create_tags_list_makes_tags_list():
    data = _get_resource_json("image_data_varying_tags_whitespace.json")
    actual_tags_list = flickr._create_tags_list(data)
    expect_tags_list = ["tag1", "tag2", "tag3"]
    assert len(actual_tags_list) == len(expect_tags_list)
    assert all([element in actual_tags_list for element in expect_tags_list])


def test_create_tags_list_sorts_tags():
    data = _get_resource_json("image_data_unsorted_tags.json")
    actual_tags_list = flickr._create_tags_list(data)
    expect_tags_list = ["tag1", "tag2", "tag3"]
    assert len(actual_tags_list) == len(expect_tags_list)
    assert all([element in actual_tags_list for element in expect_tags_list])


def test_create_tags_list_truncates_long_tags():
    data = _get_resource_json("image_data_long_tags_string.json")
    actual_tags_list = flickr._create_tags_list(data, max_tag_string_length=37)
    expect_tags_list = ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6"]
    assert len(actual_tags_list) == len(expect_tags_list)
    assert all([element in actual_tags_list for element in expect_tags_list])


def test_create_tags_list_returns_falsy_no_tag_key():
    data = {"id": "aslkjb"}
    tags_list = flickr._create_tags_list(data)
    assert not tags_list


def test_create_tags_list_returns_falsy_empty_tags():
    data = {"id": "aslkjb", "tags": ""}
    tags_list = flickr._create_tags_list(data)
    assert not tags_list


def test_process_image_data_with_sub_provider():
    image_data = _get_resource_json("image_data_sub_provider_example.json")
    with patch.object(
        flickr, "_get_file_properties", return_value=(218414, "jpg")
    ), patch.object(flickr.image_store, "add_item", return_value=100) as mock_add_item:
        total_images = flickr._process_image_data(image_data)

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

    mock_add_item.assert_called_once_with(
        foreign_landing_url=("https://www.flickr.com/photos/35067687@N04/49950595947"),
        image_url=(
            "https://live.staticflickr.com/65535/49950595947_65a3560ddc" "_b.jpg"
        ),
        thumbnail_url=(
            "https://live.staticflickr.com/65535/49950595947_65a3560ddc" "_m.jpg"
        ),
        license_info=(
            LicenseInfo(
                "by-nc-sa",
                "2.0",
                "https://creativecommons.org/licenses/by-nc-sa/2.0/",
                None,
            )
        ),
        foreign_identifier="49950595947",
        width=1024,
        height=683,
        filesize=218414,
        filetype="jpg",
        creator="NASA HQ PHOTO",
        creator_url="https://www.flickr.com/photos/35067687@N04",
        title="SpaceX Demo-2 Preflight (NHQ202005290001)",
        meta_data=expect_meta_data,
        raw_tags=[
            "capecanaveral",
            "commercialcrewprogram",
            "gophertortoise",
            "kennedyspacecenter",
            "nasa",
            "spacex",
        ],
        source="nasa",
        category=None,
    )
    assert total_images == 100


def test_get_file_properties_returns_no_filesize_from_no_response():
    url = "https://flickr.com/image.jpg"
    with patch.object(flickr.delayed_requester, "get", return_value=None):
        actual_filesize, _ = flickr._get_file_properties(url)
    assert actual_filesize is None


def test_get_file_properties_returns_both_values():
    url = "https://flickr.com/image.jpg"
    headers = {"X-TTDB-L": "123456"}

    def get_mock_headers(name, default):
        return headers[name]

    mock_response = Response()
    mock_response.status_code = codes.ok
    mock_response.headers = MagicMock()
    mock_response.headers.get.side_effect = get_mock_headers

    # filesize and filetype
    expect_props = (123456, "jpg")

    with patch.object(flickr.delayed_requester, "get", return_value=mock_response):
        actual_props = flickr._get_file_properties(url)

    assert actual_props == expect_props

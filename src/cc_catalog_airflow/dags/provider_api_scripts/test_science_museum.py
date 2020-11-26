import os
import json
import logging
import requests
from unittest.mock import MagicMock, patch
from collections import namedtuple
from common.storage.image import MockImageStore

import science_museum as sm

LicenseInfo = namedtuple(
    'LicenseInfo',
    ['license', 'version', 'url']
)
_license_info = ('by-nc-sa', '4.0', 'https://creativecommons.org/licenses/by-nc-sa/4.0/')
license_info = LicenseInfo(*_license_info)
sm.image_store = MockImageStore(
                    provider=sm.PROVIDER,
                    license_info=license_info
                    )


RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'tests/resources/sciencemuseum'
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.DEBUG
)


def _get_resource_json(json_name):
    with open(os.path.join(RESOURCES, json_name)) as f:
        resource_json = json.load(f)
    return resource_json


def test_get_query_param_default():
    actual_param = sm._get_query_param()
    expected_param = {
        "has_image": 1,
        "image_license": "CC",
        "page[size]": 100,
        "page[number]": 0,
        "date[from]": 0,
        "date[to]": 1500
    }

    assert actual_param == expected_param


def test_get_query_param_offset_page_number():
    actual_param = sm._get_query_param(
        page_number=10,
        from_year=1500,
        to_year=2000)
    expected_param = {
        "has_image": 1,
        "image_license": "CC",
        "page[size]": 100,
        "page[number]": 10,
        "date[from]": 1500,
        "date[to]": 2000
    }

    assert actual_param == expected_param


def test_page_record_empty():
    with patch.object(
            sm,
            '_get_batch_objects',
            return_value=[]) as mock_call:
        with patch.object(
                sm,
                '_handle_object_data',
                return_value=None) as mock_handle:
            sm._page_records(
                from_year=0,
                to_year=1500
            )

    assert mock_call.call_count == 1
    assert mock_handle.call_count == 0


def test_page_record_failure():
    with patch.object(
            sm,
            '_get_batch_objects',
            return_value=None) as mock_call:
        with patch.object(
                sm,
                '_handle_object_data',
                return_value=None) as mock_handle:
            sm._page_records(
                from_year=0,
                to_year=1500
            )

    assert mock_call.call_count == 1
    assert mock_handle.call_count == 0


def test_get_batch_object_success():
    query_param = {
        "has_image": 1,
        "image_license": "CC",
        "page[size]": 1,
        "page[number]": 1,
        "date[from]": 0,
        "date[to]": 1500
    }
    response = _get_resource_json("response_success.json")
    r = requests.Response()
    r.status_code = 200
    r.json = MagicMock(return_value=response)
    with patch.object(
            sm.delay_request,
            'get',
            return_value=r) as mock_call:
        actual_response = sm._get_batch_objects(
            query_param=query_param
        )

    expected_response = response.get("data")

    assert mock_call.call_count == 1
    assert actual_response == expected_response


def test_get_batch_object_failure():
    query_param = {
        "has_image": 1,
        "image_license": "CC",
        "page[size]": 1,
        "page[number]": 51,
        "date[from]": 0,
        "date[to]": 1500
    }
    response = _get_resource_json("response_failure.json")
    r = requests.Response()
    r.status_code = 400
    r.json = MagicMock(return_value=response)
    with patch.object(
            sm.delay_request,
            'get',
            return_value=r) as mock_call:
        actual_response = sm._get_batch_objects(
            query_param=query_param
        )

    assert mock_call.call_count == 3
    assert actual_response is None


def test_get_batch_object_no_response():
    query_param = {
        "has_image": 1,
        "image_license": "CC",
        "page[size]": 1,
        "page[number]": 1,
        "date[from]": 0,
        "date[to]": 1500
    }
    response = None
    with patch.object(
            sm.delay_request,
            'get',
            return_value=response) as mock_call:
        actual_response = sm._get_batch_objects(
            query_param=query_param
        )

    assert mock_call.call_count == 3
    assert actual_response is None


def test_creator_info_success():
    obj_attr = _get_resource_json("object_attr.json")
    actual_creator = sm._get_creator_info(obj_attr)
    expected_creator = "W D and H O Wills Limited"

    assert actual_creator == expected_creator


def test_creator_info_fail():
    obj_attr = {}
    actual_creator = sm._get_creator_info(obj_attr)
    expected_creator = None

    assert actual_creator == expected_creator


def test_image_info_large():
    large_image = _get_resource_json("large_image.json")
    actual_image, actual_height, actual_width = sm._get_image_info(
        large_image
    )
    expected_image = (
        "https://coimages.sciencemuseumgroup.org.uk/images/3/563/"
        "large_1999_0299_0001__0002_.jpg")
    expected_height = 1022
    expected_width = 1536

    assert actual_image == expected_image
    assert actual_height == expected_height
    assert actual_width == expected_width


def test_image_info_medium():
    medium_image = _get_resource_json("medium_image.json")
    actual_image, actual_height, actual_width = sm._get_image_info(
        medium_image
    )

    expected_image = (
        "https://coimages.sciencemuseumgroup.org.uk/images/3/563/"
        "medium_1999_0299_0001__0002_.jpg")
    expected_height = 576
    expected_width = 866

    assert actual_image == expected_image
    assert actual_height == expected_height
    assert actual_width == expected_width


def test_image_info_failure():
    actual_image, actual_height, actual_width = sm._get_image_info({})

    assert actual_image is None
    assert actual_height is None
    assert actual_width is None


def test_thumbnail_large():
    thumbnail_large = _get_resource_json("thumbnail_large.json")
    actual_image = sm._get_thumbnail_url(thumbnail_large)

    expected_image = (
        "https://coimages.sciencemuseumgroup.org.uk/images/3/563/"
        "large_thumbnail_1999_0299_0001__0002_.jpg")

    assert actual_image == expected_image


def test_thumbnail_medium():
    thumbnail_medium = _get_resource_json("thumbnail_medium.json")
    actual_image = sm._get_thumbnail_url(thumbnail_medium)

    expected_image = (
        "https://coimages.sciencemuseumgroup.org.uk/images/3/563/"
        "medium_thumbnail_1999_0299_0001__0002_.jpg")

    assert actual_image == expected_image


def test_thumbnail_small():
    thumbnail_small = _get_resource_json("thumbnail_small.json")
    actual_image = sm._get_thumbnail_url(thumbnail_small)

    expected_image = (
        "https://coimages.sciencemuseumgroup.org.uk/images/3/563/"
        "small_thumbnail_1999_0299_0001__0002_.jpg")

    assert actual_image == expected_image


def test_thumbnail_failure():
    thumbmail = {}
    actual_image = sm._get_thumbnail_url(thumbmail)

    assert actual_image is None


def test_check_relative_url():
    rel_url = "3/563/large_thumbnail_1999_0299_0001__0002_.jpg"
    actual_url = sm.check_url(rel_url)
    expected_url = (
        "https://coimages.sciencemuseumgroup.org.uk/images/3/563/"
        "large_thumbnail_1999_0299_0001__0002_.jpg")

    assert actual_url == expected_url


def test_check_complete_url():
    url = (
        "https://coimages.sciencemuseumgroup.org.uk/images/3/563/"
        "large_thumbnail_1999_0299_0001__0002_.jpg")
    actual_url = sm.check_url(url)
    expected_url = url

    assert actual_url == expected_url


def test_check_url_none():
    url = None
    actual_url = sm.check_url(url)

    assert actual_url is None


def test_get_dimensions():
    measurements = _get_resource_json("measurements.json")
    actual_height, actual_width = sm._get_dimensions(measurements)
    expected_height, expected_width = (1022, 1536)

    assert actual_height == expected_height
    assert actual_width == expected_width


def test_get_dimensions_none():
    measurements = None
    actual_height, actual_width = sm._get_dimensions(measurements)

    assert actual_height is None
    assert actual_width is None


def test_get_license():
    source = _get_resource_json("license_source.json")
    actual_license_version = sm._get_license_version(source)
    expected_license_version = "CC-BY-NC-SA 4.0"

    assert actual_license_version == expected_license_version


def test_get_license_none_type1():
    source = None
    actual_license_version = sm._get_license_version(source)

    assert actual_license_version is None


def test_get_license_none_type2():
    source = {}
    actual_license_version = sm._get_license_version(source)

    assert actual_license_version is None


def test_get_license_none_type3():
    source = _get_resource_json("no_license.json")
    actual_license_version = sm._get_license_version(source)

    assert actual_license_version is None


def test_get_metadata():
    obj_attr = _get_resource_json("object_attr.json")
    actual_metadata = sm._get_metadata(obj_attr)
    expected_metadata = _get_resource_json("metadata.json")

    assert actual_metadata == expected_metadata


def test_handle_obj_data():
    object_data = _get_resource_json("objects_data.json")
    actual_image_count = sm._handle_object_data(object_data)

    assert actual_image_count == 2


def test_handle_obj_data_none():
    object_data = []
    actual_image_count = sm._handle_object_data(object_data)

    assert actual_image_count == 0

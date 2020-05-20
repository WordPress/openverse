import os
import json
import logging
import requests
from unittest.mock import MagicMock, patch

import science_museum as sm

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
        "has_image" : 1,
        "image_license" : "CC",
        "page[size]" : 100,
        "page[number]" : 1
    }

    assert actual_param == expected_param


def test_get_query_param_offset():
    actual_param = sm._get_query_param(page_number=10)
    expected_param = {
        "has_image" : 1,
        "image_license" : "CC",
        "page[size]" : 100,
        "page[number]" : 10
    }

    assert actual_param == expected_param


def test_get_batch_object_success():
    query_param = {
    "has_image" : 1,
	"image_license" : "CC",
	"page[size]" : 1,
	"page[number]" : 1
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
    "has_image" : 1,
	"image_license" : "CC",
	"page[size]" : 1,
	"page[number]" : 51
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
    
    expected_response = None

    assert mock_call.call_count == 3
    assert actual_response == expected_response


def test_get_batch_object_error():
    query_param = {
    "has_image" : 1,
	"image_license" : "CC",
	"page[size]" : 1,
	"page[number]" : 1
    }   
    response = None
    with patch.object(
        sm.delay_request,
        'get',
        return_value=response) as mock_call:
        actual_response = sm._get_batch_objects(
            query_param=query_param
        )
    
    expected_response = None

    assert mock_call.call_count == 3
    assert actual_response == expected_response


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
    expected_image = "https://coimages.sciencemuseumgroup.org.uk/images/3/563/large_1999_0299_0001__0002_.jpg"
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

    expected_image = "https://coimages.sciencemuseumgroup.org.uk/images/3/563/medium_1999_0299_0001__0002_.jpg"
    expected_height = 576
    expected_width = 866

    assert actual_image == expected_image
    assert actual_height == expected_height
    assert actual_width == expected_width


def test_image_info_failure():
    actual_image, actual_height, actual_width = sm._get_image_info({})

    assert actual_image == None
    assert actual_height == None
    assert actual_width == None


def test_thumbnail_large():
    thumbnail_large = _get_resource_json("thumbnail_large.json")
    actual_image = sm._get_thumbnail_url(thumbnail_large)

    expected_image = "https://coimages.sciencemuseumgroup.org.uk/images/3/563/large_thumbnail_1999_0299_0001__0002_.jpg"

    assert actual_image == expected_image


def test_thumbnail_medium():
    thumbnail_medium = _get_resource_json("thumbnail_medium.json")
    actual_image = sm._get_thumbnail_url(thumbnail_medium)

    expected_image = "https://coimages.sciencemuseumgroup.org.uk/images/3/563/medium_thumbnail_1999_0299_0001__0002_.jpg"

    assert actual_image == expected_image


def test_thumbnail_small():
    thumbnail_small = _get_resource_json("thumbnail_small.json")
    actual_image = sm._get_thumbnail_url(thumbnail_small)

    expected_image = "https://coimages.sciencemuseumgroup.org.uk/images/3/563/small_thumbnail_1999_0299_0001__0002_.jpg"   

    assert actual_image == expected_image


def test_thumbnail_failure():
    thumbmail = {}
    actual_image = sm._get_thumbnail_url(thumbmail)

    assert actual_image == None

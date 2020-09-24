import logging
import json
import requests
import os
from unittest.mock import patch, MagicMock

import pytest

import cleveland_museum_of_art as clm

RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'tests/resources/clevelandmuseum'
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.DEBUG
)


def _get_resource_json(json_name):
    with open(os.path.join(RESOURCES, json_name)) as f:
        resource_json = json.load(f)
    return resource_json


def test_build_query_param_default():
    actual_param = clm._build_query_param()
    expected_param = {
        "cc": "1",
        "has_image": "1",
        "limit": 1000,
        "skip": 0
    }
    assert actual_param == expected_param


def test_build_query_param_with_givens():
    actual_param = clm._build_query_param(offset=1000)
    expected_param = {
        "cc": "1",
        "has_image": "1",
        "limit": 1000,
        "skip": 1000
    }
    assert actual_param == expected_param


def test_get_image_type_web():
    image_data = _get_resource_json('image_type_web.json')
    actual_url, actual_key = clm._get_image_type(image_data)
    expected_url = (
        "https://openaccess-cdn.clevelandart.org/1335.1917/1335.1917_web.jpg")
    expected_key = "web"

    assert actual_url == expected_url
    assert actual_key == expected_key


def test_get_image_type_print():
    image_data = _get_resource_json('image_type_print.json')
    actual_url, actual_key = clm._get_image_type(image_data)
    expected_url = (
        "https://openaccess-cdn.clevelandart.org/"
        "1335.1917/1335.1917_print.jpg")
    expected_key = "print"

    assert actual_url == expected_url
    assert actual_key == expected_key


def test_get_image_type_full():
    image_data = _get_resource_json('image_type_full.json')
    actual_url, actual_key = clm._get_image_type(image_data)
    expected_url = (
        "https://openaccess-cdn.clevelandart.org/"
        "1335.1917/1335.1917_full.tif")
    expected_key = "full"

    assert actual_url == expected_url
    assert actual_key == expected_key


def test_get_image_type_none():
    image_data = _get_resource_json("image_type_none.json")
    actual_url, actual_key = clm._get_image_type(image_data)
    expected_url = None
    expected_key = None

    assert actual_url == expected_url
    assert actual_key == expected_key


def test_get_metadata():
    data = _get_resource_json('complete_data.json')
    actual_metadata = clm._get_metadata(data)
    expected_metadata = _get_resource_json("expect_metadata.json")
    assert actual_metadata == expected_metadata


def test_get_response_success():
    query_param = {"cc": 1,
                   "has_image": 1,
                   "limit": 1,
                   "skip": 30000}
    response_json = _get_resource_json('response_success.json')
    r = requests.Response()
    r.status_code = 200
    r.json = MagicMock(return_value=response_json)
    with patch.object(clm.delay_request,
                      'get',
                      return_value=r) as mock_get:

        response_json, total_images = clm._get_response(query_param)
    expected_response = _get_resource_json('response_success.json')

    assert mock_get.call_count == 1
    assert response_json == expected_response
    assert total_images == 1


def test_get_response_no_data():
    query_param = {"cc": 1,
                   "has_image": 1,
                   "limit": 1,
                   "skip": 33000}
    response_json = _get_resource_json('response_no_data.json')
    r = requests.Response()
    r.status_code = 200
    r.json = MagicMock(return_value=response_json)
    with patch.object(clm.delay_request,
                      'get',
                      return_value=r) as mock_get:

        response_json, total_images = clm._get_response(query_param)
    expected_response = _get_resource_json('response_no_data.json')

    assert mock_get.call_count == 1
    assert response_json == expected_response
    assert total_images == 0


def test_get_response_failure():
    query_param = {"cc": 1,
                   "has_image": 1,
                   "limit": 1,
                   "skip": -1}
    r = requests.Response()
    r.status_code = 500
    r.json = None
    with patch.object(clm.delay_request,
                      'get',
                      return_value=r) as mock_get:

        response_json, total_images = clm._get_response(query_param)

    assert mock_get.call_count == 3


@pytest.mark.skip(reason='This test calls the internet via ImageStore')
def test_handle_response():
    response_json = _get_resource_json('handle_response_data.json')
    data = response_json['data']
    actual_total_images = clm._handle_response(data)
    expected_total_images = 100

    assert actual_total_images == expected_total_images

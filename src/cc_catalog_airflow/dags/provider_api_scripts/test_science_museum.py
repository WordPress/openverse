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

import os
import json
import logging
import requests
from unittest.mock import MagicMock, patch

import museum_victoria as mv

RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'tests/resources/museumvictoria'
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
    actual_param = mv._get_query_params()
    expected_param = {
        "has_image": "yes",
        "perpage": 100,
        "imagelicence": "cc by",
        "page": 0
    }

    assert actual_param == expected_param


def test_get_query_param_offset():
    actual_param = mv._get_query_params(
        license_type="public domain",
        page=10
    )

    expected_param = {
        "has_image": "yes",
        "perpage": 100,
        "imagelicence": "public domain",
        "page": 10
    }

    assert actual_param == expected_param


def test_get_batch_objects_success():
    query_param = {
        "has_image": "yes",
        "perpage": 100,
        "imagelicence": "cc+by",
        "page": 0
    }

    response_success = _get_resource_json('response_success.json')
    r = requests.Response()
    r.status_code = 200
    r.json = MagicMock(return_value=response_success)

    with patch.object(
            mv.delay_request,
            'get',
            return_value=r) as mock_call:
        actual_response = mv._get_batch_objects(params=query_param)
    
    expected_response = response_success

    assert actual_response == expected_response
    assert mock_call.call_count == 1


def test_get_batch_objects_empty():
    query_param = {
        "has_image": "yes",
        "perpage": 1,
        "imagelicence": "cc by",
        "page": 1000
    }
    response_empty = json.loads("[]")
    with patch.object(
            mv.delay_request,
            'get',
            return_value=response_empty) as mock_call:
        actual_response = mv._get_batch_objects(params=query_param)
    
    expected_param = []

    assert mock_call.call_count == 3
    assert actual_response is None


def test_get_batch_objects_error():
    query_param = {
        "has_image": "yes",
        "perpage": 1,
        "imagelicence": "cc by",
        "page": 0
    }

    r = requests.Response()
    r.status_code = 404

    with patch.object(
            mv.delay_request,
            'get',
            return_value=r) as mock_call:
        actual_response = mv._get_batch_objects(query_param)
    
    assert actual_response is None
    assert mock_call.call_count == 3

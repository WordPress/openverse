import os
import json
import logging
import requests
from unittest.mock import MagicMock, patch

import nypl as np

RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'tests/resources/nypl'
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
    actual_param = np._get_query_param()
    expected_param = {
        "q": "CC_0",
        "field": "use_rtxt_s",
        "page": 1,
        "per_page": 500
    }

    assert actual_param == expected_param


def test_get_query_param_offset():
    actual_param = np._get_query_param(page=10)
    expected_param = {
        "q": "CC_0",
        "field": "use_rtxt_s",
        "page": 10,
        "per_page": 500
    }

    assert actual_param == expected_param


def test_request_handler_search_success():
    query_param = {
        "q": "CC_0",
        "field": "use_rtxt_s",
        "page": 12,
        "per_page": 1
    }

    response_search_success = _get_resource_json("response_search_success.json")
    r = requests.Response()
    r.status_code = 200
    r.json = MagicMock(return_value=response_search_success)
    with patch.object(
            np.delay_request,
            'get',
            return_value=r) as mock_call:
        actual_response = np._request_handler(params=query_param)

    expected_response = response_search_success.get(
        "nyplAPI", {}
        ).get(
            "response"
            )

    assert actual_response == expected_response
    assert mock_call.call_count == 1


def test_request_handler_search_failure():
    response_itemdetails_success = _get_resource_json(
        "response_itemdetails_success.json"
    )
    r = requests.Response()
    r.status_code = 200
    r.json = MagicMock(return_value=response_itemdetails_success)
    with patch.object(
            np.delay_request,
            'get',
            return_value=r) as mock_call:
        actual_response = np._request_handler(
                endpoint=np.METADATA_ENDPOINT
                + "0cabe3d0-3d50-0134-a8e0-00505686a51c",
                request_type="itemdetails"
            )
    
    expected_response = response_itemdetails_success.get(
        "nyplAPI", {}
    ).get("response")

    assert actual_response == expected_response
    assert mock_call.call_count == 1

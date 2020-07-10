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

    response_search_success = _get_resource_json(
        "response_search_success.json"
        )
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


def test_get_images_success():
    images = _get_resource_json("images.json")
    actual_image_url, \
        actual_thumbnail = np._get_images(images)

    assert actual_image_url == "http://images.nypl.org/index.php?id=56738462&t=g&suffix=0cabe3d0-3d50-0134-a8e0-00505686a51c.001"
    assert actual_thumbnail == "http://images.nypl.org/index.php?id=56738462&t=w&suffix=0cabe3d0-3d50-0134-a8e0-00505686a51c.001"


def test_get_image_failure():
    images = []
    actual_image_url, \
        actual_thumbnail = np._get_images(images)

    assert actual_image_url is None
    assert actual_thumbnail is None


def test_get_title_success():
    titleinfo = _get_resource_json("title_info_success.json")
    actual_title = np._get_title(titleinfo)
    expected_title = "1900 census enumeration districts, Manhattan and Bronx"

    assert actual_title == expected_title


def test_get_title_failure():
    titleinfo = []
    actual_title = np._get_title(titleinfo)

    assert actual_title is None


def test_get_creators_success():
    creatorinfo = _get_resource_json("creator_info_success.json")
    actual_creator = np._get_creators(creatorinfo)
    expected_creator = "Hillman, Barbara|Ohman, August R.|New York Public Library. Local History and Genealogy Division"

    assert actual_creator == expected_creator


def test_get_creators_failure():
    creatorinfo = []
    actual_creator = np._get_creators(creatorinfo)

    assert actual_creator == []

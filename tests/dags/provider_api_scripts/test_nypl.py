import json
import logging
import os
from unittest.mock import MagicMock, patch

import provider_api_scripts.nypl as np
import requests


RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources/nypl")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.DEBUG
)


def _get_resource_json(json_name):
    with open(os.path.join(RESOURCES, json_name)) as f:
        resource_json = json.load(f)
    return resource_json


def test_get_query_param_default():
    actual_param = np._get_query_param()
    expected_param = {"q": "CC_0", "field": "use_rtxt_s", "page": 1, "per_page": 500}

    assert actual_param == expected_param


def test_get_query_param_offset():
    actual_param = np._get_query_param(page=10)
    expected_param = {"q": "CC_0", "field": "use_rtxt_s", "page": 10, "per_page": 500}

    assert actual_param == expected_param


def test_request_handler_search_success():
    query_param = {"q": "CC_0", "field": "use_rtxt_s", "page": 12, "per_page": 1}

    response_search_success = _get_resource_json("response_search_success.json")
    r = requests.Response()
    r.status_code = 200
    r.json = MagicMock(return_value=response_search_success)
    with patch.object(np.delay_request, "get", return_value=r) as mock_call:
        actual_response = np._request_handler(params=query_param)

    expected_response = response_search_success.get("nyplAPI", {}).get("response")

    assert actual_response == expected_response
    assert mock_call.call_count == 1


def test_request_handler_itemdetail_success():
    response_itemdetails_success = _get_resource_json(
        "response_itemdetails_success.json"
    )
    r = requests.Response()
    r.status_code = 200
    r.json = MagicMock(return_value=response_itemdetails_success)
    with patch.object(np.delay_request, "get", return_value=r) as mock_call:
        actual_response = np._request_handler(
            endpoint=np.METADATA_ENDPOINT + ("0cabe3d0-3d50-0134-a8e0-00505686a51c"),
        )

    expected_response = response_itemdetails_success.get("nyplAPI", {}).get("response")

    assert actual_response == expected_response
    assert mock_call.call_count == 1


def test_request_handler_failure():
    query_param = {"q": "CC_0", "field": "use_rtxt_s", "page": 12, "per_page": 1}

    r = requests.Response()
    r.status_code = 400
    r.json = MagicMock(return_value={})
    with patch.object(np.delay_request, "get", return_value=r) as mock_call:
        actual_response = np._request_handler(params=query_param)
    assert mock_call.call_count == 3
    assert actual_response is None


def test_get_images_success():
    images = _get_resource_json("images.json")
    actual_image_url, actual_thumbnail = np._get_images(images)

    assert actual_image_url == (
        "http://images.nypl.org/index.php?id=56738462&t=g&suffix=0cabe3d0-"
        "3d50-0134-a8e0-00505686a51c.001"
    )
    assert actual_thumbnail == (
        "http://images.nypl.org/index.php?id=56738462&t=w&suffix=0cabe3d0-"
        "3d50-0134-a8e0-00505686a51c.001"
    )


def test_get_image_failure():
    images = []
    actual_image_url, actual_thumbnail = np._get_images(images)

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
    expected_creator = "Hillman, Barbara"

    assert actual_creator == expected_creator


def test_get_creators_failure():
    creatorinfo = []
    actual_creator = np._get_creators(creatorinfo)

    assert actual_creator is None


def test_get_metadata():
    item_response = _get_resource_json("response_itemdetails_success.json")
    mods = item_response.get("nyplAPI").get("response").get("mods")
    actual_metadata = np._get_metadata(mods)
    expected_metadata = _get_resource_json("metadata.json")

    assert actual_metadata == expected_metadata


def test_handle_results_success():
    search_response = _get_resource_json("response_search_success.json")
    result = search_response.get("nyplAPI").get("response").get("result")

    item_response = _get_resource_json("response_itemdetails_success.json")
    r = requests.Response()
    r.status_code = 200
    r.json = MagicMock(return_value=item_response)
    with patch.object(np.delay_request, "get", return_value=r) as mock_request:
        with patch.object(np.image_store, "add_item") as mock_item:
            np._handle_results(result)

    assert mock_item.call_count == 7
    assert mock_request.call_count == 1


def test_handle_results_failure():
    search_response = _get_resource_json("response_search_success.json")
    result = search_response.get("nyplAPI").get("response").get("result")

    item_response = None
    with patch.object(np, "_request_handler", return_value=item_response):
        with patch.object(np.image_store, "add_item") as mock_item:
            np._handle_results(result)

    assert mock_item.call_count == 0


def test_get_capture_detail_success():
    captures = _get_resource_json("capture_details.json")

    with patch.object(np.image_store, "add_item") as mock_item:
        np._get_capture_details(captures=captures)
    assert mock_item.call_count == 7


def test_get_capture_detail_failure():
    captures = []

    with patch.object(np.image_store, "add_item") as mock_item:
        np._get_capture_details(captures=captures)

    assert mock_item.call_count == 0

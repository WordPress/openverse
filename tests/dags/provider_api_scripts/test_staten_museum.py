import json
import logging
import os
from unittest.mock import MagicMock, patch

import provider_api_scripts.staten_museum as sm
import requests


RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "resources/statenmuseum"
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.DEBUG
)


def _get_resource_json(json_name):
    with open(os.path.join(RESOURCES, json_name)) as f:
        resource_json = json.load(f)
    return resource_json


def test_get_query_param_default():
    actual_param = sm._get_query_param()
    expected_param = {
        "keys": "*",
        "filters": "[has_image:true],[public_domain:true]",
        "offset": 0,
        "rows": 2000,
    }

    assert actual_param == expected_param


def test_get_query_param_offset():
    actual_param = sm._get_query_param(offset=100)
    expected_param = {
        "keys": "*",
        "filters": "[has_image:true],[public_domain:true]",
        "offset": 100,
        "rows": 2000,
    }

    assert actual_param == expected_param


def test_get_batch_items_success():
    query_param = {
        "keys": "*",
        "filters": "[has_image:true],[public_domain:true]",
        "offset": 0,
        "rows": 1,
    }
    response = _get_resource_json("response_success.json")
    r = requests.Response()
    r.status_code = 200
    r.json = MagicMock(return_value=response)
    with patch.object(sm.delay_request, "get", return_value=r) as mock_call:
        actual_response = sm._get_batch_items(query_params=query_param)

    expected_response = response.get("items")

    assert mock_call.call_count == 1
    assert actual_response == expected_response


def test_get_batch_item_failure1():
    query_param = {
        "keys": "*",
        "filters": "[has_image:true],[public_domain:true]",
        "offset": 40000,
        "rows": 2000,
    }
    response = _get_resource_json("response_failure.json")
    r = requests.Response()
    r.status_code = 200
    r.json = MagicMock(return_value=response)
    with patch.object(sm.delay_request, "get", return_value=r) as mock_call:
        actual_response = sm._get_batch_items(query_params=query_param)

    assert mock_call.call_count == 3
    assert actual_response is None


def test_get_batch_item_failure2():
    query_param = {
        "keys": "*",
        "filters": "[has_image:true],[public_domain:true]",
        "offset": 0,
        "rows": 2000,
    }
    response = None
    with patch.object(sm.delay_request, "get", return_value=response) as mock_call:
        actual_response = sm._get_batch_items(query_params=query_param)

    assert mock_call.call_count == 3
    assert actual_response is None


def test_handle_items_data_success():
    items = _get_resource_json("items_batch.json")
    with patch.object(sm.image_store, "add_item", return_value=1) as mock_add_item:
        actual_image_count = sm._handle_items_data(items)

    assert mock_add_item.call_count == 1
    assert actual_image_count == 1


def test_handle_items_data_failure():
    items = []
    with patch.object(sm.image_store, "add_item", return_value=None) as mock_add_item:
        actual_image_count = sm._handle_items_data(items)

    assert mock_add_item.call_count == 0
    assert actual_image_count == 0


def test_get_image_complete():
    item = _get_resource_json("image_data_complete.json")
    expected_images_data = _get_resource_json("expected_image_data_complete.json")

    actual_images_data = sm._get_images(item)

    assert actual_images_data == expected_images_data


def test_get_image_partial():
    item = _get_resource_json("image_data_partial.json")
    expected_images_data = _get_resource_json("expected_image_data_partial.json")

    actual_images_data = sm._get_images(item)

    assert actual_images_data == expected_images_data


def test_get_image_none():
    item = {}
    expected_images_data = []
    actual_images_data = sm._get_images(item)

    assert actual_images_data == expected_images_data


def test_get_image_url():
    image_iif_id = "https://iip.smk.dk/iiif/jp2/KKSgb6458.tif.jp2"
    actual_image_url, actual_thumbnail = sm._get_image_url(image_iif_id)

    expected_image_url = (
        "https://iip.smk.dk/iiif/jp2/KKSgb6458.tif.jp2/full/max/0/default.jpg"
    )
    expected_thumbnail = (
        "https://iip.smk.dk/iiif/jp2/KKSgb6458.tif.jp2/full/!400,/0/" "default.jpg"
    )

    assert actual_image_url == expected_image_url
    assert actual_thumbnail == expected_thumbnail


def test_get_license_info_success():
    rights = "https://creativecommons.org/share-your-work/public-domain/cc0/"
    actual_license_, actual_version = sm._get_license_info(rights)

    assert actual_license_ == "cc0"
    assert actual_version == "1.0"


def test_get_license_info_failure():
    rights = None
    actual_license_, actual_version = sm._get_license_info(rights)

    assert actual_version is None
    assert actual_license_ is None


def test_get_creator():
    production = [{"creator": "sample"}]
    actual_creator = sm._get_creator(production)

    assert actual_creator == "sample"


def test_get_creator_none():
    production = {}
    actual_creator = sm._get_creator(production)

    assert actual_creator is None


def test_get_title():
    titles = [{"title": "sample"}]
    actual_title = sm._get_title(titles)

    assert actual_title == "sample"


def test_get_title_none():
    titles = None
    actual_title = sm._get_title(titles)

    assert actual_title is None


def test_get_metadata():
    item = _get_resource_json("item.json")
    actual_metadata = sm._get_metadata(item)

    expected_metadata = {
        "created_date": "2020-03-21T10:18:17Z",
        "collection": "Gammel bestand",
        "techniques": "Kobberstik",
    }

    assert actual_metadata == expected_metadata

import json
import logging
import os
from unittest.mock import MagicMock, patch

import requests
from providers.provider_api_scripts import museum_victoria as mv


RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "resources/museumvictoria"
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.DEBUG
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
        "page": 0,
    }

    assert actual_param == expected_param


def test_get_query_param_offset():
    actual_param = mv._get_query_params(license_type="public domain", page=10)

    expected_param = {
        "has_image": "yes",
        "perpage": 100,
        "imagelicence": "public domain",
        "page": 10,
    }

    assert actual_param == expected_param


def test_get_batch_objects_success():
    query_param = {
        "has_image": "yes",
        "perpage": 100,
        "imagelicence": "cc+by",
        "page": 0,
    }

    response_success = _get_resource_json("response_success.json")
    r = requests.Response()
    r.status_code = 200
    r.json = MagicMock(return_value=response_success)

    with patch.object(mv.delay_request, "get", return_value=r) as mock_call:
        actual_response = mv._get_batch_objects(params=query_param)

    expected_response = response_success

    assert actual_response == expected_response
    assert mock_call.call_count == 1


def test_get_batch_objects_empty():
    query_param = {
        "has_image": "yes",
        "perpage": 1,
        "imagelicence": "cc by",
        "page": 1000,
    }
    response_empty = json.loads("[]")
    with patch.object(
        mv.delay_request, "get", return_value=response_empty
    ) as mock_call:
        actual_response = mv._get_batch_objects(params=query_param)

    assert mock_call.call_count == 3
    assert actual_response is None


def test_get_batch_objects_error():
    query_param = {"has_image": "yes", "perpage": 1, "imagelicence": "cc by", "page": 0}

    r = requests.Response()
    r.status_code = 404

    with patch.object(mv.delay_request, "get", return_value=r) as mock_call:
        actual_response = mv._get_batch_objects(query_param)

    assert actual_response is None
    assert mock_call.call_count == 3


def test_get_media_info_success():
    media = _get_resource_json("media_data_success.json")
    actual_image_data = mv._get_media_info(media)

    expected_image_data = _get_resource_json("image_data_success.json")

    assert actual_image_data == expected_image_data


def test_get_media_info_failure():
    media = _get_resource_json("media_data_failure.json")
    actual_image_data = mv._get_media_info(media)

    assert len(actual_image_data) == 0


def test_get_image_data_large():
    image_data = _get_resource_json("large_image_data.json")

    actual_image_url, actual_height, actual_width = mv._get_image_data(image_data)

    assert actual_image_url == (
        "https://collections.museumsvictoria.com.au/content/media/45/"
        "329745-large.jpg"
    )
    assert actual_height == 2581
    assert actual_width == 2785


def test_get_image_data_medium():
    image_data = _get_resource_json("medium_image_data.json")

    actual_image_url, actual_height, actual_width = mv._get_image_data(image_data)

    assert actual_image_url == (
        "https://collections.museumsvictoria.com.au/content/media/45/"
        "329745-medium.jpg"
    )
    assert actual_height == 1390
    assert actual_width == 1500


def test_get_image_data_small():
    image_data = _get_resource_json("small_image_data.json")

    actual_image_url, actual_height, actual_width = mv._get_image_data(image_data)

    assert actual_image_url == (
        "https://collections.museumsvictoria.com.au/content/media/45/"
        "329745-small.jpg"
    )
    assert actual_height == 500
    assert actual_width == 540


def test_get_image_data_none():
    image_data = {}

    actual_image_url, actual_height, actual_width = mv._get_image_data(image_data)

    assert actual_image_url is None
    assert actual_height is None
    assert actual_width is None


def test_get_license_url():
    media = _get_resource_json("cc_image_data.json")
    actual_license_url = mv._get_license_url(media)
    expected_license_url = "https://creativecommons.org/licenses/by/4.0"

    assert actual_license_url == expected_license_url


def test_get_license_url_failure():
    media = _get_resource_json("media_data_failure.json")
    actual_license_url = mv._get_license_url(media[0])

    assert actual_license_url is None


def test_get_metadata():
    obj = _get_resource_json("batch_objects.json")
    expected_metadata = _get_resource_json("metadata.json")
    actual_metadata = mv._get_metadata(obj[0])

    assert actual_metadata == expected_metadata


def test_get_creator():
    media = _get_resource_json("cc_image_data.json")
    actual_creator = mv._get_creator(media)

    assert actual_creator == "Photographer: Deb Tout-Smith"


def test_handle_batch_objects_success():
    batch_objects = _get_resource_json("batch_objects.json")

    with patch.object(mv.image_store, "add_item") as mock_item:
        mv._handle_batch_objects(batch_objects)
    assert mock_item.call_count == 1

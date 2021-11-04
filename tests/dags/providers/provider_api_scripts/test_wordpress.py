import json
import logging
from pathlib import Path
from unittest.mock import patch

import requests
import wordpress as wp


RESOURCES = Path(__file__).parent / "resources/wordpress"
SAMPLE_MEDIA_DATA = RESOURCES / "full_item.json"
SAMPLE_MEDIA_DETAILS = RESOURCES / "full_item_details.json"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s",
    level=logging.DEBUG,
)


def test_get_query_params_returns_defaults():
    expected_result = {
        "format": "json",
        "page": 1,
        "per_page": 100,
    }
    actual_result = wp._get_query_params()
    assert actual_result == expected_result


def test_get_query_params_returns_defaults_with_given_page():
    expected_result = {
        "format": "json",
        "page": 3,
        "per_page": 100,
    }
    actual_result = wp._get_query_params(page=3)
    assert actual_result == expected_result


def test_get_item_page_returns_correctly_with_none_response():
    expected_result = (None, 0)
    endpoint = "example.com"
    with patch.object(wp.delayed_requester, "get", return_value=None):
        actual_result = wp._get_item_page(endpoint)
    assert actual_result == expected_result


def test_get_item_page_returns_correctly_with_no_results():
    expected_result = (None, 0)
    endpoint = "example.com"
    with patch.object(wp.delayed_requester, "get", return_value=requests.Response()):
        actual_result = wp._get_item_page(endpoint)
    assert actual_result == expected_result


def test_process_resource_batch_with_non_users_resources():
    # Apply for photo categories, colors and tags too
    with open(RESOURCES / "orientations_batch.json") as f:
        batch_data = json.load(f)
    actual_result = wp._process_resource_batch("photo-orientations", batch_data)
    expected_result = {23: "landscape", 24: "portrait", 25: "square"}
    assert actual_result == expected_result


def test_process_resource_batch_with_users():
    with open(RESOURCES / "users_batch.json") as f:
        batch_data = json.load(f)
    actual_result = wp._process_resource_batch("users", batch_data)
    expected_result = {3606: {"name": "Scott Reilly", "url": "http://coffee2code.com"}}
    assert actual_result == expected_result


def test_extract_image_data_returns_none_when_media_data_none():
    actual_image_info = wp._extract_image_data(None)
    expected_image_info = None
    assert actual_image_info is expected_image_info


def test_extract_image_data_returns_none_when_no_foreign_id():
    with open(SAMPLE_MEDIA_DATA) as f:
        image_data = json.load(f)
        image_data.pop("slug", None)
    actual_image_info = wp._extract_image_data(image_data)
    expected_image_info = None
    assert actual_image_info is expected_image_info


def test_extract_image_data_returns_none_when_no_image_details():
    with open(SAMPLE_MEDIA_DATA) as f:
        image_data = json.load(f)
        image_data.pop("_links", None)
    actual_image_info = wp._extract_image_data(image_data)
    assert actual_image_info is None


def test_get_title():
    with open(SAMPLE_MEDIA_DATA) as f:
        image_data = json.load(f)
    actual_result = wp._get_title(image_data)
    expected_result = "Lupinus polyphyllus (aka Washington lupine)"
    assert actual_result == expected_result


def test_get_file_info():
    with open(SAMPLE_MEDIA_DETAILS) as f:
        image_details = json.load(f)
    actual_result = wp._get_file_info(image_details)
    expected_result = (
        "https://pd.w.org/2021/06/56560bf1d69971f38.94814132.jpg",  # image_url
        4032,  # height
        3024,  # width
        "jpg",  # filetype
    )
    assert actual_result == expected_result


def test_get_creator_data():
    with open(SAMPLE_MEDIA_DATA) as f:
        image_data = json.load(f)
    image_related_patch = {
        "users": {
            3606: {"name": "Scott Reilly", "url": "http://coffee2code.com"},
        }
    }
    with patch.object(wp, "IMAGE_RELATED_RESOURCES", image_related_patch):
        actual_creator, actual_creator_url = wp._get_creator_data(image_data)
    expected_creator = "Scott Reilly"
    expected_creator_url = "http://coffee2code.com"

    assert actual_creator == expected_creator
    assert actual_creator_url == expected_creator_url


def test_get_creator_data_handle_no_author():
    with open(SAMPLE_MEDIA_DATA) as f:
        image_data = json.load(f)
    image_data.pop("author")
    image_related_patch = {
        "users": {
            3606: {"name": "Scott Reilly", "url": "http://coffee2code.com"},
        }
    }
    with patch.object(wp, "IMAGE_RELATED_RESOURCES", image_related_patch):
        actual_creator, actual_creator_url = wp._get_creator_data(image_data)
    assert actual_creator is None
    assert actual_creator_url is None


def test_get_metadata():
    with open(SAMPLE_MEDIA_DATA) as f1, open(SAMPLE_MEDIA_DETAILS) as f2:
        image_data = json.load(f1)
        image_details = json.load(f2)
    image_related_patch = {
        "photo-colors": {15: "green", 36: "purple"},
        "photo-orientations": {24: "portrait"},
        "photo-categories": {8: "nature"},
    }
    with patch.object(wp, "IMAGE_RELATED_RESOURCES", image_related_patch):
        actual_metadata = wp._get_metadata(image_data, image_details)

    expected_metadata = {
        "aperture": "1.8",
        "camera": "Pixel 2 XL",
        "created_timestamp": "1591460495",
        "focal_length": "4.459",
        "iso": "45",
        "shutter_speed": "0.00171",
        "published_date": "2021-06-08T07:34:17",
        "categories": ["nature"],
        "colors": ["green", "purple"],
        "orientations": ["portrait"],
    }
    assert len(actual_metadata) == len(expected_metadata)
    assert actual_metadata == expected_metadata


def test_get_related_data_with_tags():
    with open(SAMPLE_MEDIA_DATA) as f:
        image_data = json.load(f)
    prefetched_tags = {"photo-tags": {35: "flower", 28: "plant"}}
    with patch.object(wp, "IMAGE_RELATED_RESOURCES", prefetched_tags):
        actual_tags = wp._get_related_data("tags", image_data)
    expected_tags = ["flower", "plant"]
    assert len(actual_tags) == len(expected_tags)
    assert sorted(expected_tags) == sorted(actual_tags)

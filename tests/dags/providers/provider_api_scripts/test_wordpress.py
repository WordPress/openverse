import json
import logging
from pathlib import Path
from unittest.mock import patch

import requests
import wordpress as wp


RESOURCES = Path(__file__).parent / "resources/wordpress"
SAMPLE_MEDIA_DATA = RESOURCES / "full_item.json"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s",
    level=logging.DEBUG,
)


def test_get_query_params_returns_defaults():
    expected_result = {"format": "json", "page": 1, "per_page": 100, "_embed": "true"}
    actual_result = wp._get_query_params()
    assert actual_result == expected_result


def test_get_query_params_returns_defaults_with_given_page():
    expected_result = {"format": "json", "page": 3, "per_page": 100, "_embed": "true"}
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


def test_extract_image_data_returns_none_when_no_foreign_id():
    with open(SAMPLE_MEDIA_DATA) as f:
        image_data = json.load(f)
        image_data.pop("slug", None)
    actual_image_info = wp._extract_image_data(image_data)
    expected_image_info = None
    assert actual_image_info is expected_image_info


def test_extract_image_data_returns_none_when_no_image_url():
    with open(SAMPLE_MEDIA_DATA) as f:
        image_data = json.load(f)
        image_data["_embedded"]["wp:featuredmedia"][0]["media_details"].pop("sizes")
    actual_image_info = wp._extract_image_data(image_data)
    assert actual_image_info is None


def test_get_title():
    with open(SAMPLE_MEDIA_DATA) as f:
        image_data = json.load(f)
    actual_result = wp._get_title(image_data)
    expected_result = "Coffee Bean with bags"
    assert actual_result == expected_result


def test_get_file_info():
    with open(SAMPLE_MEDIA_DATA) as f:
        image_details = (
            json.load(f)
            .get("_embedded")
            .get("wp:featuredmedia")[0]
            .get("media_details")
        )
    actual_result = wp._get_file_info(image_details)
    expected_result = (
        "https://pd.w.org/2022/05/203627f31f8770f03.61535278-2048x1366.jpg",  # image_url
        1366,  # height
        2048,  # width
        "jpg",  # filetype
        544284,  # filesize
    )
    assert actual_result == expected_result


def test_get_author_data_when_is_non_empty():
    with open(SAMPLE_MEDIA_DATA) as f:
        image_data = json.load(f)
    actual_author, actual_author_url = wp._get_author_data(image_data)
    expected_author = "Shusei Toda"
    expected_author_url = "https://shuseitoda.com"
    assert actual_author == expected_author
    assert actual_author_url == expected_author_url


def test_get_author_data_handle_no_author():
    with open(SAMPLE_MEDIA_DATA) as f:
        image_data = json.load(f)
    image_data["_embedded"].pop("author", None)
    actual_author, actual_author_url = wp._get_author_data(image_data)
    assert actual_author is None
    assert actual_author_url is None


def test_get_author_data_use_slug_when_name_is_empty():
    with open(SAMPLE_MEDIA_DATA) as f:
        image_data = json.load(f)
    image_data["_embedded"]["author"][0].pop("name")
    actual_author, _ = wp._get_author_data(image_data)
    expected_author = "st810amaze"
    assert actual_author == expected_author


def test_get_metadata():
    with open(SAMPLE_MEDIA_DATA) as f:
        image_data = json.load(f)
    image_details = (
        image_data.get("_embedded").get("wp:featuredmedia")[0].get("media_details")
    )
    actual_metadata, actual_tags = wp._get_metadata(image_data, image_details)
    expected_metadata = {
        "aperture": "4",
        "camera": "ILCE-7M4",
        "created_timestamp": "1652338105",
        "focal_length": "55",
        "iso": "6400",
        "shutter_speed": "0.008",
        "categories": ["food-drink"],
        "colors": ["brown", "orange"],
        "orientation": "landscape",
    }
    expected_tags = ["bean", "coffee"]
    # assert len(actual_metadata) == len(expected_metadata)
    assert actual_metadata == expected_metadata
    assert len(actual_tags) == len(expected_tags)
    assert actual_tags == expected_tags

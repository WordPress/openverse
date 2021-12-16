import json
import logging
import os
from unittest.mock import patch

from common.licenses import get_license_info
from providers.provider_api_scripts import stocksnap


RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "resources/stocksnap"
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s",
    level=logging.DEBUG,
)


def test_get_image_pages_returns_correctly_with_none_json():
    expect_result = None
    with patch.object(
        stocksnap.delayed_requester, "get_response_json", return_value=None
    ):
        actual_result = stocksnap._get_batch_json()
    assert actual_result == expect_result


def test_get_image_pages_returns_correctly_with_no_results():
    expect_result = None
    with patch.object(
        stocksnap.delayed_requester, "get_response_json", return_value={}
    ):
        actual_result = stocksnap._get_batch_json()
    assert actual_result == expect_result


def test_extract_image_data_returns_none_when_media_data_none():
    actual_image_info = stocksnap._extract_item_data(None)
    expected_image_info = None
    assert actual_image_info is expected_image_info


def test_extract_image_data_returns_none_when_no_foreign_id():
    with open(os.path.join(RESOURCES, "full_item.json")) as f:
        image_data = json.load(f)
        image_data.pop("img_id", None)
    actual_image_info = stocksnap._extract_item_data(image_data)
    expected_image_info = None
    assert actual_image_info is expected_image_info


def test_get_creator_data():
    with open(os.path.join(RESOURCES, "full_item.json")) as f:
        img_data = json.load(f)
    expected_creator = "Matt Moloney"
    expected_creator_url = "https://mjmolo.com/"

    actual_creator, actual_creator_url = stocksnap._get_creator_data(img_data)
    assert actual_creator == expected_creator
    assert actual_creator_url == expected_creator_url


def test_get_creator_data_handles_no_url():
    with open(os.path.join(RESOURCES, "full_item.json")) as f:
        img_data = json.load(f)
    img_data.pop("author_website")
    img_data.pop("author_profile")
    expected_creator = "Matt Moloney"

    actual_creator, actual_creator_url = stocksnap._get_creator_data(img_data)
    assert actual_creator == expected_creator
    assert actual_creator_url is None


def test_get_creator_data_returns_stocksnap_author_profile():
    with open(os.path.join(RESOURCES, "full_item.json")) as f:
        img_data = json.load(f)
    img_data["author_website"] = "https://stocksnap.io/"
    expected_creator = "Matt Moloney"
    expected_creator_url = "https://stocksnap.io/author/111564"

    actual_creator, actual_creator_url = stocksnap._get_creator_data(img_data)
    assert actual_creator == expected_creator
    assert actual_creator_url == expected_creator_url


def test_get_creator_data_returns_none_when_no_author():
    with open(os.path.join(RESOURCES, "full_item.json")) as f:
        img_data = json.load(f)
    img_data.pop("author_name")
    actual_creator, actual_creator_url = stocksnap._get_creator_data(img_data)
    assert actual_creator is None
    assert actual_creator_url is None


def test_extract_image_data_handles_example_dict():
    with open(os.path.join(RESOURCES, "full_item.json")) as f:
        image_data = json.load(f)

    with patch.object(stocksnap, "_get_filesize", return_value=123456):
        actual_image_info = stocksnap._extract_item_data(image_data)
    image_url = "https://cdn.stocksnap.io/img-thumbs/960w/7VAQUG1X3B.jpg"
    thumbnail_url = "https://cdn.stocksnap.io/img-thumbs/280h/7VAQUG1X3B.jpg"
    expected_image_info = {
        "title": "Female Fitness Photo",
        "creator": "Matt Moloney",
        "creator_url": "https://mjmolo.com/",
        "foreign_identifier": "7VAQUG1X3B",
        "foreign_landing_url": "https://stocksnap.io/photo/7VAQUG1X3B",
        "license_info": get_license_info(
            license_url="https://creativecommons.org/publicdomain/zero/1.0/"
        ),
        "image_url": image_url,
        "filesize": 123456,
        "filetype": "jpg",
        "height": 4000,
        "width": 6000,
        "thumbnail_url": thumbnail_url,
        "meta_data": {
            "page_views_raw": 30,
            "downloads_raw": 0,
            "favorites_raw": 0,
        },
        "raw_tags": [
            "female",
            "fitness",
            "trainer",
            "model",
            "outdoors",
            "fit",
            "workout",
            "health",
            "woman",
            "field",
            "girl",
            "pose",
            "sport",
            "athlete",
            "recreation",
            "wellness",
            "people",
            "fashion",
            "day",
            "active",
            "sports",
            "track",
            "stretch",
            "lifestyle",
            "squat",
        ],
        "category": "photograph",
    }
    assert actual_image_info == expected_image_info


def test_get_image_tags():
    item_data = {
        "keywords": [
            "sunflowers",
            "nature",
            "flower",
        ],
    }
    expected_tags = ["sunflowers", "nature", "flower"]
    actual_tags = stocksnap._get_tags(item_data)
    assert expected_tags == actual_tags

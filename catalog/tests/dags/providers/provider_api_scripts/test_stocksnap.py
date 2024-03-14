import logging
from unittest.mock import patch

import pytest

from catalog.tests.dags.providers.provider_api_scripts.resources.json_load import (
    make_resource_json_func,
)
from common.licenses import get_license_info
from common.loader import provider_details as prov
from common.storage.image import ImageStore
from providers.provider_api_scripts.stocksnap import StockSnapDataIngester


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s",
    level=logging.DEBUG,
)


stocksnap = StockSnapDataIngester()
image_store = ImageStore(provider=prov.STOCKSNAP_DEFAULT_PROVIDER)
stocksnap.media_stores = {"image": image_store}


_get_resource_json = make_resource_json_func("stocksnap")


@pytest.fixture(autouse=True)
def filesize_mock():
    with patch.object(stocksnap, "_get_filesize") as get_filesize_mock:
        yield get_filesize_mock


def test_get_media_type():
    expect_result = "image"
    actual_result = stocksnap.get_media_type(_get_resource_json("full_item.json"))
    assert expect_result == actual_result


def test_endpoint_with_initialized_page_counter():
    expect_result = "https://stocksnap.io/api/load-photos/date/desc/0"
    actual_result = stocksnap.endpoint
    assert expect_result == actual_result


def test_get_batch_data_returns_correctly_with_none_json():
    expect_result = None
    actual_result = stocksnap.get_batch_data(None)
    assert actual_result == expect_result


def test_get_batch_data_returns_correctly_with_no_results():
    expect_result = None
    actual_result = stocksnap.get_batch_data({})
    assert actual_result == expect_result


def test_get_batch_data_returns_correctly_with_full_response():
    actual_result = stocksnap.get_batch_data(_get_resource_json("full_response.json"))
    assert isinstance(actual_result, list)
    assert len(actual_result) == 40
    assert actual_result[0] == {
        "img_id": "OAJ3645ZWF",
        "tags": "flower,   blossom,   macro,   close up,   fresh,   petals,   flora,   floral,   plants,   organic,   natural,   spring,   bloom,   minimal,   background,   wallpaper,   texture,   pattern,   delicate,   detail,   botanical,  magnolia",
        "page_views": 25,
        "downloads": 5,
        "favorites": 0,
        "img_width": 6000,
        "img_height": 4000,
        "author_name": "Macro Mama",
        "author_id": 125683,
        "author_website": "https://stocksnap.io/",
        "author_profile": "https://stocksnap.io/author/125683",
        "adjustedWidth": 420,
        "page_views_raw": 25,
        "downloads_raw": 5,
        "favorites_raw": 0,
        "keywords": [
            "flower",
            "blossom",
            "macro",
            "closeup",
            "fresh",
            "petals",
            "flora",
            "floral",
            "plants",
            "organic",
            "natural",
            "spring",
            "bloom",
            "minimal",
            "background",
            "wallpaper",
            "texture",
            "pattern",
            "delicate",
            "detail",
            "botanical",
            "magnolia",
        ],
        "favorited": False,
    }


def test_process_batch(filesize_mock):
    expect_result = 40
    filesize_mock.return_value = 12345
    actual_result = stocksnap.process_batch(
        stocksnap.get_batch_data(_get_resource_json("full_response.json"))
    )
    assert expect_result == actual_result


def test_endpoint_increment():
    expect_result = ({}, "https://stocksnap.io/api/load-photos/date/desc/1")
    query_params = stocksnap.get_next_query_params(None)
    next_endpoint = stocksnap.endpoint
    actual_result = (query_params, next_endpoint)
    assert expect_result == actual_result


def test_get_record_data_returns_none_when_media_data_none():
    actual_image_info = stocksnap.get_record_data(None)
    expected_image_info = None
    assert actual_image_info is expected_image_info


def test_get_record_data_returns_none_when_no_foreign_id():
    image_data = _get_resource_json("full_item.json")
    image_data.pop("img_id", None)
    actual_image_info = stocksnap.get_record_data(image_data)
    expected_image_info = None
    assert actual_image_info is expected_image_info


def test_get_creator_data():
    img_data = _get_resource_json("full_item.json")
    expected_creator = "Matt Moloney"
    expected_creator_url = "https://mjmolo.com/"

    actual_creator, actual_creator_url = stocksnap._get_creator_data(img_data)
    assert actual_creator == expected_creator
    assert actual_creator_url == expected_creator_url


def test_get_creator_data_handles_no_url():
    img_data = _get_resource_json("full_item.json")
    img_data.pop("author_website")
    img_data.pop("author_profile")
    expected_creator = "Matt Moloney"

    actual_creator, actual_creator_url = stocksnap._get_creator_data(img_data)
    assert actual_creator == expected_creator
    assert actual_creator_url is None


def test_get_creator_data_returns_stocksnap_author_profile():
    img_data = _get_resource_json("full_item.json")
    img_data["author_website"] = "https://stocksnap.io/"
    expected_creator = "Matt Moloney"
    expected_creator_url = "https://stocksnap.io/author/111564"

    actual_creator, actual_creator_url = stocksnap._get_creator_data(img_data)
    assert actual_creator == expected_creator
    assert actual_creator_url == expected_creator_url


def test_get_creator_data_returns_none_when_no_author():
    img_data = _get_resource_json("full_item.json")
    img_data.pop("author_name")
    actual_creator, actual_creator_url = stocksnap._get_creator_data(img_data)
    assert actual_creator is None
    assert actual_creator_url is None


def test_get_record_data_handles_example_dict(filesize_mock):
    image_data = _get_resource_json("full_item.json")
    filesize_mock.return_value = 123456
    actual_image_info = stocksnap.get_record_data(image_data)
    url = "https://cdn.stocksnap.io/img-thumbs/960w/7VAQUG1X3B.jpg"
    expected_image_info = {
        "title": "Female Fitness",
        "creator": "Matt Moloney",
        "creator_url": "https://mjmolo.com/",
        "foreign_identifier": "7VAQUG1X3B",
        "foreign_landing_url": "https://stocksnap.io/photo/female-fitness-7VAQUG1X3B",
        "license_info": get_license_info(
            license_url="https://creativecommons.org/publicdomain/zero/1.0/"
        ),
        "url": url,
        "filesize": 123456,
        "filetype": "jpg",
        "height": 4000,
        "width": 6000,
        "meta_data": {
            "page_views_raw": 30,
            "downloads_raw": 0,
            "favorites_raw": 0,
        },
        "raw_tags": {
            "active",
            "athlete",
            "day",
            "fashion",
            "female",
            "field",
            "fit",
            "fitness",
            "girl",
            "health",
            "lifestyle",
            "model",
            "outdoors",
            "people",
            "pose",
            "recreation",
            "sport",
            "sports",
            "squat",
            "stretch",
            "track",
            "trainer",
            "wellness",
            "woman",
            "workout",
        },
    }
    assert actual_image_info == expected_image_info


def test_get_should_continue_first_response():
    expect_result = True
    actual_result = stocksnap.get_should_continue(
        _get_resource_json("full_response.json")
    )
    assert expect_result == actual_result


def test_get_should_continue_last_response():
    expect_result = False
    actual_result = stocksnap.get_should_continue(
        _get_resource_json("last_full_response.json")
    )
    assert expect_result == actual_result


def test_get_image_tags():
    item_data = {
        "keywords": [
            "sunflowers",
            "nature",
            "flower",
        ],
    }
    expected_tags = {"sunflowers", "nature", "flower"}
    actual_tags = stocksnap._get_tags(item_data)
    assert expected_tags == actual_tags

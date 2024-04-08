from unittest.mock import MagicMock, patch

import pytest
from tests.dags.providers.provider_api_scripts.resources.json_load import (
    make_resource_json_func,
)

from providers.provider_api_scripts.wordpress import WordPressDataIngester


_get_resource_json = make_resource_json_func("wordpress")


@pytest.fixture
def ingester() -> WordPressDataIngester:
    wp = WordPressDataIngester()
    wp.total_pages = 50
    return wp


def test_get_query_params_returns_defaults_and_sets_total_pages():
    # Create a new WordPressDataIngester which does not have `total_pages` set yet
    wp = WordPressDataIngester()

    mock_head_request = MagicMock()
    mock_head_request.headers = {"X-WP-TotalPages": 5}

    # Mock the head request to get the `total_pages`
    with patch.object(wp.delayed_requester, "head", return_value=mock_head_request):
        actual_result = wp.get_next_query_params({})

    expected_result = {"format": "json", "page": 1, "per_page": 100, "_embed": "true"}
    assert actual_result == expected_result
    assert wp.total_pages == 5


def test_get_query_params_increments_current_page(ingester):
    expected_result = {"format": "json", "page": 3, "per_page": 100, "_embed": "true"}
    actual_result = ingester.get_next_query_params({**expected_result, "page": 2})
    assert actual_result == expected_result


@pytest.mark.parametrize(
    "current_page, should_continue",
    [
        # Note that total_pages is 50
        # the current page is less than total_pages
        (10, True),
        (49, True),
        # the current page is the last page
        (50, False),
        # the current page is after the last page (Note: this should not arise)
        (51, False),
    ],
)
def test_get_should_continue_checks_total_pages(
    ingester, current_page, should_continue
):
    ingester.current_page = current_page
    assert ingester.get_should_continue({}) == should_continue


@pytest.mark.parametrize("missing_field", ["slug", "link"])
def test_get_record_data_returns_none_when_necessary_data_is_missing(
    ingester, missing_field
):
    image_data = _get_resource_json("full_item.json")
    image_data.pop(missing_field, None)
    actual_image_info = ingester.get_record_data(image_data)
    assert actual_image_info is None


@pytest.mark.parametrize("falsy_field", ["slug", "link"])
def test_get_record_data_returns_none_when_necessary_data_is_falsy(
    ingester, falsy_field
):
    image_data = _get_resource_json("full_item.json")
    image_data[falsy_field] = ""
    actual_image_info = ingester.get_record_data(image_data)
    assert actual_image_info is None


def test_get_record_data_returns_none_when_no_url(ingester):
    image_data = _get_resource_json("full_item.json")
    image_data["_embedded"]["wp:featuredmedia"][0]["media_details"].pop("sizes")
    actual_image_info = ingester.get_record_data(image_data)
    assert actual_image_info is None


def test_get_title(ingester):
    image_data = _get_resource_json("full_item.json")
    actual_result = ingester._get_title(image_data)
    expected_result = "Coffee Bean with bags"
    assert actual_result == expected_result


def test_get_file_info(ingester):
    image_details = (
        _get_resource_json("full_item.json")
        .get("_embedded")
        .get("wp:featuredmedia")[0]
        .get("media_details")
    )
    actual_result = ingester._get_file_info(image_details)
    expected_result = (
        "https://pd.w.org/2022/05/203627f31f8770f03.61535278-2048x1366.jpg",  # url
        1366,  # height
        2048,  # width
        544284,  # filesize
    )
    assert actual_result == expected_result


def test_get_author_data_when_is_non_empty(ingester):
    image_data = _get_resource_json("full_item.json")
    actual_author, actual_author_url = ingester._get_author_data(image_data)
    expected_author = "Shusei Toda"
    expected_author_url = "https://shuseitoda.com"
    assert actual_author == expected_author
    assert actual_author_url == expected_author_url


def test_get_author_data_handle_no_author(ingester):
    image_data = _get_resource_json("full_item.json")
    image_data["_embedded"].pop("author", None)
    actual_author, actual_author_url = ingester._get_author_data(image_data)
    assert actual_author is None
    assert actual_author_url is None


def test_get_author_data_use_slug_when_name_is_empty(ingester):
    image_data = _get_resource_json("full_item.json")
    image_data["_embedded"]["author"][0].pop("name")
    actual_author, _ = ingester._get_author_data(image_data)
    expected_author = "st810amaze"
    assert actual_author == expected_author


def test_get_metadata(ingester):
    image_data = _get_resource_json("full_item.json")
    image_details = (
        image_data.get("_embedded").get("wp:featuredmedia")[0].get("media_details")
    )
    actual_metadata, actual_tags = ingester._get_metadata(image_data, image_details)
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

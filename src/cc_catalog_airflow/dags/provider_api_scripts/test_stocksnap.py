import json
import logging
import os
from unittest.mock import Mock, patch

import stocksnap

RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'tests/resources/stocksnap'
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.DEBUG,
)


def test_get_image_pages_returns_correctly_with_none_json():
    expect_result = None
    with patch.object(
            stocksnap.delayed_requester,
            'get_response_json',
            return_value=None
    ):
        actual_result = stocksnap._get_batch_json()
    assert actual_result == expect_result


def test_get_image_pages_returns_correctly_with_no_results():
    expect_result = None
    with patch.object(
            stocksnap.delayed_requester,
            'get_response_json',
            return_value={}
    ):
        actual_result = stocksnap._get_batch_json()
    assert actual_result == expect_result


def test_extract_image_data_returns_none_when_media_data_none():
    actual_image_info = stocksnap._extract_item_data(None)
    expected_image_info = None
    assert actual_image_info is expected_image_info


def test_extract_image_data_returns_none_when_no_foreign_id():
    with open(os.path.join(RESOURCES, 'full_item.json')) as f:
        image_data = json.load(f)
        image_data.pop('img_id', None)
    actual_image_info = stocksnap._extract_item_data(image_data)
    expected_image_info = None
    assert actual_image_info is expected_image_info


def test_get_creator_data():
    file_name = 'foreign_landing_page_text_example.txt'
    with open(os.path.join(RESOURCES, file_name)) as f:
        image_data = f.read()
        page = stocksnap.html.document_fromstring(image_data)
    actual_creator, actual_creator_url = stocksnap._get_creator_data(page)
    expected_creator = 'Matt Bango'
    expected_creator_url = 'https://stocksnap.io/author/mattbangophotos'

    assert actual_creator == expected_creator
    assert actual_creator_url == expected_creator_url


def test_get_creator_data_handles_no_url():
    file_name = 'foreign_landing_page_text_example.txt'
    with open(os.path.join(RESOURCES, file_name)) as f:
        image_data = f.read().replace('href="/author/mattbangophotos"', "")
        page = stocksnap.html.document_fromstring(image_data)
    expected_creator = 'Matt Bango'

    actual_creator, actual_creator_url = stocksnap._get_creator_data(page)
    assert actual_creator == expected_creator
    assert actual_creator_url is None


def test_get_creator_data_returns_none_when_no_author():
    file_name = 'foreign_landing_page_text_example.txt'
    with open(os.path.join(RESOURCES, file_name)) as f:
        image_data = f.read().replace('class="author"', "")
        page = stocksnap.html.document_fromstring(image_data)
    actual_creator, actual_creator_url = stocksnap._get_creator_data(page)

    assert actual_creator is None
    assert actual_creator_url is None


@patch('stocksnap.delayed_requester.get')
def test_extract_image_data_handles_example_dict(mock_get):
    # Prepare mock request
    foreign_url = "https://stocksnap.io/photo/sunflowers-garden-YDQABWFXOZ"
    file_name = 'foreign_landing_page_text_example.txt'
    with open(os.path.join(RESOURCES, file_name)) as f:
        txt_data = f.read()
    mock_get.return_value = Mock(text=txt_data, url=foreign_url)
    # Load example image data
    with open(os.path.join(RESOURCES, 'full_item.json')) as f:
        image_data = json.load(f)
    actual_image_info = stocksnap._extract_item_data(image_data)
    # Omit license field as always is CC0
    actual_image_info.pop("license_info")
    image_url = 'https://cdn.stocksnap.io/img-thumbs/960w/YDQABWFXOZ.jpg'
    expected_image_info = {
        'title': 'Sunflowers Garden Photo',
        'creator': 'Matt Bango',
        'creator_url': 'https://stocksnap.io/author/mattbangophotos',
        'foreign_identifier': 'YDQABWFXOZ',
        'foreign_landing_url': foreign_url,
        'image_url': image_url,
        'height': 3401,
        'width': 5102,
        'thumbnail_url': image_url,
        'meta_data': {
            "page_views": 5,
            "downloads": 0,
            "favorites": 0,
        },
        'raw_tags': [
            "sunflowers",
            "garden",
            "nature",
            "flower",
            "bright",
            "green",
            "sunny",
            "yellow",
            "blooming",
            "blossom",
            "organic",
            "plant",
            "summer",
            "growth",
            "sunshine",
            "botanical",
            "beauty",
            "field",
            "floral",
            "rural",
            "background"
        ],
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
    expected_tags = ['sunflowers', 'nature', 'flower']
    actual_tags = stocksnap._get_tags(item_data)
    assert expected_tags == actual_tags

"""
End-to-end API tests for images. Can be used to verify a live deployment is
functioning as designed. Run with the `pytest -s` command from this directory.
"""

import json

import pytest
import requests

from test.constants import API_URL
from test.media_integration import (
    search,
    search_quotes,
    search_special_chars,
    search_consistency,
    detail,
)


@pytest.fixture
def image_fixture():
    response = requests.get(f'{API_URL}/v1/images?q=dog', verify=False)
    assert response.status_code == 200
    parsed = json.loads(response.text)
    return parsed


def test_search(image_fixture):
    search(image_fixture)


def test_search_quotes():
    search_quotes('images', 'dog')


def test_search_with_special_characters():
    search_special_chars('images', 'dog')


def test_search_consistency():
    n_pages = 5
    search_consistency('images', n_pages)


def test_image_detail(image_fixture):
    detail('images', image_fixture)


def test_image_stats():
    response = requests.get(f'{API_URL}/v1/images/stats', verify=False)
    parsed_response = json.loads(response.text)
    assert response.status_code == 200
    num_images = 0
    provider_count = 0
    for pair in parsed_response:
        image_count = pair['image_count']
        num_images += int(image_count)
        provider_count += 1
    assert num_images > 0
    assert provider_count > 0

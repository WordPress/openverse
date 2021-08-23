"""
End-to-end API tests for images. Can be used to verify a live deployment is
functioning as designed. Run with the `pytest -s` command from this directory.
"""

import json
from urllib.parse import urlencode
import pytest
import requests
import xml.etree.ElementTree as ET

from test.constants import API_URL
from test.media_integration import (
    search,
    search_quotes,
    search_special_chars,
    search_consistency,
    detail,
    stats,
    thumb,
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
    stats('images', 'image_count')


def test_image_thumb(image_fixture):
    thumb(image_fixture)


def test_oembed_endpoint_for_json():
    params = {
        'url': 'https://any.domain/any/path/29cb352c-60c1-41d8-bfa1-7d6f7d955f63',
        # 'format': 'json' is the default
    }
    response = requests.get(
        f'{API_URL}/v1/images/oembed?{urlencode(params)}',
        verify=False
    )
    assert response.status_code == 200
    assert response.headers['Content-Type'] == "application/json"

    parsed = response.json()
    assert parsed['width'] == 1276
    assert parsed['height'] == 1536
    assert parsed['license_url'] == 'https://creativecommons.org/licenses/by-nc-nd/4.0/'


def test_oembed_endpoint_for_xml():
    params = {
        'url': 'https://any.domain/any/path/29cb352c-60c1-41d8-bfa1-7d6f7d955f63',
        'format': 'xml'
    }
    response = requests.get(
        f'{API_URL}/v1/images/oembed?{urlencode(params)}',
        verify=False
    )
    assert response.status_code == 200
    assert response.headers['Content-Type'] == "application/xml; charset=utf-8"

    response_body_as_xml = ET.fromstring(response.content)
    xml_tree = ET.ElementTree(response_body_as_xml)
    assert xml_tree.find("width").text == '1276'
    assert xml_tree.find("height").text == '1536'
    assert xml_tree.find("license_url").text == 'https://creativecommons.org/licenses/by-nc-nd/4.0/'

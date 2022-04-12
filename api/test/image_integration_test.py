"""
End-to-end API tests for images. Can be used to verify a live deployment is
functioning as designed. Run with the `pytest -s` command from this directory.
"""

import json
import xml.etree.ElementTree as ET
from test.constants import API_URL
from test.media_integration import (
    detail,
    report,
    search,
    search_all_excluded,
    search_consistency,
    search_quotes,
    search_source_and_excluded,
    search_special_chars,
    stats,
    thumb,
    thumb_compression,
    thumb_full_size,
    thumb_webp,
)
from urllib.parse import urlencode

import pytest
import requests


identifier = "cdbd3bf6-1745-45bb-b399-61ee149cd58a"


@pytest.fixture
def image_fixture():
    response = requests.get(f"{API_URL}/v1/images?q=dog", verify=False)
    assert response.status_code == 200
    parsed = json.loads(response.text)
    return parsed


def test_search(image_fixture):
    search(image_fixture)


def test_search_all_excluded():
    search_all_excluded("images", ["flickr", "stocksnap"])


def test_search_source_and_excluded():
    search_source_and_excluded("images")


def test_search_quotes():
    search_quotes("images", "dog")


def test_search_with_special_characters():
    search_special_chars("images", "dog")


def test_search_consistency():
    n_pages = 5
    search_consistency("images", n_pages)


def test_image_detail(image_fixture):
    detail("images", image_fixture)


def test_image_stats():
    stats("images")


def test_image_thumb(image_fixture):
    thumb(image_fixture)


def test_image_thumb_compression(image_fixture):
    thumb_compression(image_fixture)


def test_image_thumb_webp(image_fixture):
    thumb_webp(image_fixture)


def test_image_thumb_full_size(image_fixture):
    thumb_full_size(image_fixture)


def test_audio_report(image_fixture):
    report("images", image_fixture)


def test_oembed_endpoint_for_json():
    params = {
        "url": f"https://any.domain/any/path/{identifier}",
        # 'format': 'json' is the default
    }
    response = requests.get(
        f"{API_URL}/v1/images/oembed?{urlencode(params)}", verify=False
    )
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"

    parsed = response.json()
    assert parsed["width"] == 1024
    assert parsed["height"] == 683
    assert parsed["license_url"] == "https://creativecommons.org/licenses/by/2.0/"


def test_oembed_endpoint_for_xml():
    params = {
        "url": f"https://any.domain/any/path/{identifier}",
        "format": "xml",
    }
    response = requests.get(
        f"{API_URL}/v1/images/oembed?{urlencode(params)}", verify=False
    )
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/xml; charset=utf-8"

    response_body_as_xml = ET.fromstring(response.content)
    xml_tree = ET.ElementTree(response_body_as_xml)
    assert xml_tree.find("width").text == "1024"
    assert xml_tree.find("height").text == "683"
    assert (
        xml_tree.find("license_url").text
        == "https://creativecommons.org/licenses/by/2.0/"
    )

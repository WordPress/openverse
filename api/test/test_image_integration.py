"""
End-to-end API tests for images.

Can be used to verify a live deployment is functioning as designed.
Run with the `pytest -s` command from this directory.
"""

import json
from test.constants import API_URL
from test.media_integration import (
    creator_collection,
    detail,
    license_filter_case_insensitivity,
    related,
    report,
    search,
    search_all_excluded,
    search_consistency,
    search_quotes,
    search_quotes_exact,
    search_source_and_excluded,
    search_special_chars,
    sensitive_search_and_detail,
    source_collection,
    stats,
    tag_collection,
    uuid_validation,
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


def test_search_quotes_exact():
    # ``dancing penguins`` returns different results when quoted vs unquoted
    search_quotes_exact("images", "dancing penguins")


def test_search_with_special_characters():
    search_special_chars("images", "dog")


def test_search_consistency():
    n_pages = 5
    search_consistency("images", n_pages)


def test_image_detail(image_fixture):
    detail("images", image_fixture)


def test_image_stats():
    stats("images")


def test_audio_report(image_fixture):
    report("images", image_fixture)


def test_oembed_endpoint_with_non_existent_image():
    params = {
        "url": "https://any.domain/any/path/00000000-0000-0000-0000-000000000000",
    }
    response = requests.get(
        f"{API_URL}/v1/images/oembed?{urlencode(params)}", verify=False
    )
    assert response.status_code == 404


def test_oembed_endpoint_with_bad_identifier():
    params = {
        "url": "https://any.domain/any/path/not-a-valid-uuid",
    }
    response = requests.get(
        f"{API_URL}/v1/images/oembed?{urlencode(params)}", verify=False
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    "url",
    [
        f"https://any.domain/any/path/{identifier}",  # no trailing slash
        f"https://any.domain/any/path/{identifier}/",  # trailing slash
        identifier,  # just identifier instead of URL
    ],
)
def test_oembed_endpoint_with_fuzzy_input(url):
    params = {"url": url}
    response = requests.get(
        f"{API_URL}/v1/images/oembed?{urlencode(params)}", verify=False
    )
    assert response.status_code == 200


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


def test_image_license_filter_case_insensitivity():
    license_filter_case_insensitivity("images")


def test_image_uuid_validation():
    uuid_validation("images", "123456789123456789123456789123456789")
    uuid_validation("images", "12345678-1234-5678-1234-1234567891234")
    uuid_validation("images", "abcd")


def test_image_tag_collection():
    tag_collection("images")


def test_image_source_collection():
    source_collection("images")


def test_image_creator_collection():
    creator_collection("images")


def test_image_related(image_fixture):
    related(image_fixture)


def test_image_sensitive_search_and_detail():
    sensitive_search_and_detail("images")

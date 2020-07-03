import logging
import requests
from unittest.mock import patch

import pytest

from common import urls

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.DEBUG)

# This avoids needing the internet for testing.
urls.tldextract.extract = urls.tldextract.TLDExtract(suffix_list_urls=None)


@pytest.fixture
def clear_tls_cache():
    urls._test_tls_for_fully_qualified_domain_name.cache_clear()


@pytest.fixture
def get_good(monkeypatch):
    def mock_get(url, timeout=60):
        return requests.Response()
    monkeypatch.setattr(urls.requests, 'get', mock_get)


@pytest.fixture
def get_bad(monkeypatch):
    def mock_get(url, timeout=60):
        raise Exception
    monkeypatch.setattr(urls.requests, 'get', mock_get)


@pytest.fixture
def mock_rewriter(monkeypatch):
    def mock_rewrite_url_string(url_string):
        return url_string
    monkeypatch.setattr(
        urls, '_rewrite_url_string', mock_rewrite_url_string
    )


def test_validate_url_string_adds_http_without_scheme(
        clear_tls_cache, get_bad
):
    url_string = 'creativecomons.org'
    actual_validated_url = urls.validate_url_string(url_string)
    expect_validated_url = 'http://creativecomons.org'
    assert actual_validated_url == expect_validated_url


def test_validate_url_string_nones_with_invalid_structure_domain(
        clear_tls_cache, get_bad
):
    url_string = 'https:/abcd'
    actual_validated_url = urls.validate_url_string(url_string)
    expect_validated_url = None
    assert actual_validated_url == expect_validated_url


def test_validate_url_string_upgrades_scheme(clear_tls_cache, get_good):
    url_string = 'http://abcd.com'
    actual_validated_url = urls.validate_url_string(url_string)
    expect_validated_url = 'https://abcd.com'
    assert actual_validated_url == expect_validated_url


def test_validate_url_string_handles_wmc_type_scheme(
        clear_tls_cache, get_good
):
    url_string = '//commons.wikimedia.org/wiki/User:potato'
    actual_validated_url = urls.validate_url_string(url_string)
    expect_validated_url = 'https://commons.wikimedia.org/wiki/User:potato'
    assert actual_validated_url == expect_validated_url


def test_validate_url_string_caches_tls_support(clear_tls_cache, monkeypatch):
    url_string = 'commons.wikimedia.org/wiki/User:potato'
    with patch.object(
            urls.requests, 'get', return_value=requests.Response()
    ) as mock_get:
        actual_validated_url_1 = urls.validate_url_string(url_string)
        actual_validated_url_2 = urls.validate_url_string(url_string)
    expect_validated_url = 'https://commons.wikimedia.org/wiki/User:potato'
    assert actual_validated_url_1 == expect_validated_url
    assert actual_validated_url_2 == expect_validated_url
    mock_get.assert_called_once()

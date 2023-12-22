import logging
from unittest.mock import patch

import pytest
import requests
from requests import RequestException

from common import urls


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.DEBUG
)

# This avoids needing the internet for testing.
urls.tldextract.extract = urls.tldextract.TLDExtract(suffix_list_urls=None)


@pytest.fixture
def clear_tls_cache():
    urls._test_domain_for_tls_support.cache_clear()


@pytest.fixture
def clear_rewriter_cache():
    urls.rewrite_redirected_url.cache_clear()


@pytest.fixture
def get_good(monkeypatch):
    def mock_get(url, timeout=60):
        return requests.Response()

    monkeypatch.setattr(urls, "requests_get", mock_get)


@pytest.fixture
def get_bad(monkeypatch):
    def mock_get(url, timeout=60):
        raise RequestException()

    monkeypatch.setattr(urls, "requests_get", mock_get)


def test_validate_url_string_adds_http_without_scheme(clear_tls_cache, get_bad):
    url_string = "creativecomons.org"
    actual_validated_url = urls.validate_url_string(url_string)
    expect_validated_url = "http://creativecomons.org"
    assert actual_validated_url == expect_validated_url


def test_validate_url_string_nones_with_invalid_structure_domain(
    clear_tls_cache, get_bad
):
    url_string = "https:/abcd"
    actual_validated_url = urls.validate_url_string(url_string)
    assert actual_validated_url is None


def test_validate_url_string_upgrades_scheme(clear_tls_cache, get_good):
    url_string = "http://abcd.com"
    actual_validated_url = urls.validate_url_string(url_string)
    expect_validated_url = "https://abcd.com"
    assert actual_validated_url == expect_validated_url


def test_validate_url_string_upgrades_ip_address(clear_tls_cache, get_good):
    url_string = "http://8.8.8.8"
    actual_validated_url = urls.validate_url_string(url_string)
    expect_validated_url = "https://8.8.8.8"
    assert actual_validated_url == expect_validated_url


def test_validate_url_string_adds_to_ip_address(clear_tls_cache, get_good):
    url_string = "8.8.8.8"
    actual_validated_url = urls.validate_url_string(url_string)
    expect_validated_url = "https://8.8.8.8"
    assert actual_validated_url == expect_validated_url


def test_validate_url_string_handles_wmc_type_scheme(clear_tls_cache, get_good):
    url_string = "//commons.wikimedia.org/wiki/User:potato"
    actual_validated_url = urls.validate_url_string(url_string)
    expect_validated_url = "https://commons.wikimedia.org/wiki/User:potato"
    assert actual_validated_url == expect_validated_url


def test_validate_url_string_caches_tls_support(clear_tls_cache, monkeypatch):
    url_string = "commons.wikimedia.org/wiki/User:potato"
    with patch.object(
        urls, "requests_get", return_value=requests.Response()
    ) as mock_get:
        actual_validated_url_1 = urls.validate_url_string(url_string)
        actual_validated_url_2 = urls.validate_url_string(url_string)
    expect_validated_url = "https://commons.wikimedia.org/wiki/User:potato"
    assert actual_validated_url_1 == expect_validated_url
    assert actual_validated_url_2 == expect_validated_url
    mock_get.assert_called_once()


def test_validate_url_string_keeps_trailing_slash():
    url_string = "https://wordpress.org/photos/photo/5262839486/"
    actual_validated_url = urls.validate_url_string(url_string, strip_slash=False)
    assert actual_validated_url == url_string


def test_validate_url_string_removes_trailing_slash():
    url_string = "https://wordpress.org/photos/photo/5262839486/"
    actual_validated_url = urls.validate_url_string(url_string)
    expect_validated_url = "https://wordpress.org/photos/photo/5262839486"
    assert actual_validated_url == expect_validated_url


def test_rewrite_redirected_url_returns_when_ok(clear_rewriter_cache, monkeypatch):
    expect_url = "https://rewritten.url"
    r = requests.Response()
    r.status_code = 200
    r.url = expect_url
    monkeypatch.setattr(urls, "requests_get", lambda *args: r)
    actual_url = urls.rewrite_redirected_url("https://input.url")
    assert actual_url == expect_url


def test_rewrite_redirected_url_nones_when_not_ok(clear_rewriter_cache, monkeypatch):
    r = requests.Response()
    r.status_code = 404
    r.url = "https://rewritten.url"
    monkeypatch.setattr(urls, "requests_get", lambda *args: r)
    actual_url = urls.rewrite_redirected_url("https://input.url")
    assert actual_url is None


def test_rewrite_redirected_url_nones_when_error_occurs(
    clear_rewriter_cache, monkeypatch
):
    def mock_get(*args):
        raise RequestException()

    monkeypatch.setattr(urls, "requests_get", mock_get)
    actual_url = urls.rewrite_redirected_url("https://input.url")
    assert actual_url is None


def test_rewrite_redirected_url_caches_results(clear_rewriter_cache, monkeypatch):
    expect_url = "https://rewritten.url"
    r = requests.Response()
    r.status_code = 200
    r.url = expect_url
    input_url = "https://rewritten.url"
    with patch.object(urls, "requests_get", return_value=r) as mock_get:
        actual_rewritten_url_1 = urls.rewrite_redirected_url(input_url)
        actual_rewritten_url_2 = urls.rewrite_redirected_url(input_url)
    assert actual_rewritten_url_1 == expect_url
    assert actual_rewritten_url_2 == expect_url
    mock_get.assert_called_once()


def test_add_url_scheme_adds_scheme():
    url_stub = "creativecommons.org"
    actual_url = urls.add_url_scheme(url_stub, scheme="https")
    expect_url = "https://creativecommons.org"
    assert actual_url == expect_url


def test_add_url_scheme_upgrades_scheme():
    url_stub = "http://creativecommons.org"
    actual_url = urls.add_url_scheme(url_stub, scheme="https")
    expect_url = "https://creativecommons.org"
    assert actual_url == expect_url


def test_add_url_scheme_leaves_scheme():
    url_stub = "http://creativecommons.org"
    actual_url = urls.add_url_scheme(url_stub, scheme="http")
    expect_url = "http://creativecommons.org"
    assert actual_url == expect_url


def test_add_url_scheme_handles_h():
    url_stub = "hreativecommons.org/h"
    actual_url = urls.add_url_scheme(url_stub, scheme="https")
    expect_url = "https://hreativecommons.org/h"
    assert actual_url == expect_url


def test_add_url_scheme_leaves_nonprefix_scheme():
    url_stub = "hreativecommons.org/?referer=https://abc.com"
    actual_url = urls.add_url_scheme(url_stub, scheme="https")
    expect_url = "https://hreativecommons.org/?referer=https://abc.com"
    assert actual_url == expect_url


def test_validate_url_string_contain_space():
    with pytest.raises(urls.SpaceInUrlError):
        url_string = "https://wordpress.org/photos/photo/526283 9486/"
        urls.validate_url_string(url_string)

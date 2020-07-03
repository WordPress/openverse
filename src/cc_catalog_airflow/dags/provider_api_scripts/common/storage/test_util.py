import logging
import requests

import pytest

from common.storage import util
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.DEBUG)


@pytest.fixture
def clear_tls_cache():
    util._test_tls_for_fully_qualified_domain_name.cache_clear()


@pytest.fixture
def get_good(monkeypatch):
    def mock_get(url, timeout=60):
        return requests.Response()
    monkeypatch.setattr(util.requests, 'get', mock_get)


@pytest.fixture
def get_bad(monkeypatch):
    def mock_get(url, timeout=60):
        raise Exception
    monkeypatch.setattr(util.requests, 'get', mock_get)


@pytest.fixture
def mock_rewriter(monkeypatch):
    def mock_rewrite_url_string(url_string):
        return url_string
    monkeypatch.setattr(
        util, '_rewrite_url_string', mock_rewrite_url_string
    )


def test_get_source_preserves_given_both():
    expect_source = 'Source'
    actual_source = util.get_source(expect_source, 'test_provider')
    assert actual_source == expect_source


def test_get_source_preserves_source_without_provider():
    input_provider, expect_source = None, 'Source'
    actual_source = util.get_source(expect_source, input_provider)
    assert actual_source == expect_source


def test_get_source_fills_source_if_none_given():
    input_provider, input_source = 'Provider', None
    actual_source = util.get_source(input_source, input_provider)
    expect_source = 'Provider'
    assert actual_source == expect_source


def test_get_source_nones_if_none_given():
    actual_source = util.get_source(None, None)
    assert actual_source is None

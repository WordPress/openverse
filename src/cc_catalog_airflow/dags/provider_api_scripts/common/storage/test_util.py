import logging
import requests
from unittest.mock import patch

import pytest

from common.storage import util

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.DEBUG)

# This avoids needing the internet for testing.
util.tldextract.extract = util.tldextract.TLDExtract(suffix_list_urls=None)


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


def test_choose_license_and_version_prefers_derived_values(monkeypatch):

    def mock_get_license(url_string):
        return 'derivedlicense', '10.0'

    def mock_validate_pair(license_, license_version):
        return license_, license_version

    monkeypatch.setattr(util, '_get_license_from_url', mock_get_license)
    monkeypatch.setattr(util, '_validate_license_pair', mock_validate_pair)

    actual_license, actual_version = util.choose_license_and_version(
        'https://creativecommons.org/licenses/and/so/on',
        'license',
        '1.0'
    )
    expected_license, expected_version = 'derivedlicense', '10.0'

    assert actual_license == expected_license
    assert actual_version == expected_version


def test_choose_license_and_version_with_missing_derived_license(monkeypatch):

    def mock_get_license(url_string):
        return None, '10.0'

    def mock_validate_pair(license_, license_version):
        return license_, license_version

    monkeypatch.setattr(util, '_get_license_from_url', mock_get_license)
    monkeypatch.setattr(util, '_validate_license_pair', mock_validate_pair)

    actual_license, actual_version = util.choose_license_and_version(
        'https://creativecommons.org/licenses/and/so/on',
        'license',
        '1.0'
    )
    expected_license, expected_version = 'license', '1.0'

    assert actual_license == expected_license
    assert actual_version == expected_version


def test_choose_license_and_version_with_missing_derived_version(monkeypatch):

    def mock_get_license(url_string):
        return 'derived_license', None

    def mock_validate_pair(license_, license_version):
        return license_, license_version

    monkeypatch.setattr(util, '_get_license_from_url', mock_get_license)
    monkeypatch.setattr(util, '_validate_license_pair', mock_validate_pair)

    actual_license, actual_version = util.choose_license_and_version(
        'https://creativecommons.org/licenses/and/so/on',
        'license',
        '1.0'
    )
    expected_license, expected_version = 'license', '1.0'

    assert actual_license == expected_license
    assert actual_version == expected_version


def test_validate_url_string_adds_http_without_scheme(
        clear_tls_cache, get_bad
):
    url_string = 'creativecomons.org'
    actual_validated_url = util.validate_url_string(url_string)
    expect_validated_url = 'http://creativecomons.org'
    assert actual_validated_url == expect_validated_url


def test_validate_url_string_nones_with_invalid_structure_domain(
        clear_tls_cache, get_bad
):
    url_string = 'https:/abcd'
    actual_validated_url = util.validate_url_string(url_string)
    expect_validated_url = None
    assert actual_validated_url == expect_validated_url


def test_validate_url_string_upgrades_scheme(clear_tls_cache, get_good):
    url_string = 'http://abcd.com'
    actual_validated_url = util.validate_url_string(url_string)
    expect_validated_url = 'https://abcd.com'
    assert actual_validated_url == expect_validated_url


def test_validate_url_string_handles_wmc_type_scheme(
        clear_tls_cache, get_good
):
    url_string = '//commons.wikimedia.org/wiki/User:potato'
    actual_validated_url = util.validate_url_string(url_string)
    expect_validated_url = 'https://commons.wikimedia.org/wiki/User:potato'
    assert actual_validated_url == expect_validated_url


def test_validate_url_string_caches_tls_support(clear_tls_cache, monkeypatch):
    url_string = 'commons.wikimedia.org/wiki/User:potato'
    with patch.object(
            util.requests, 'get', return_value=requests.Response()
    ) as mock_get:
        actual_validated_url_1 = util.validate_url_string(url_string)
        actual_validated_url_2 = util.validate_url_string(url_string)
    expect_validated_url = 'https://commons.wikimedia.org/wiki/User:potato'
    assert actual_validated_url_1 == expect_validated_url
    assert actual_validated_url_2 == expect_validated_url
    mock_get.assert_called_once()


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


def test_get_license_from_url_finds_info_from_path(get_good):
    path_map = {
        'by/1.0': {'license': 'by', 'version': '1.0'},
        'zero/1.0': {'license': 'cc0', 'version': '1.0'}
    }
    actual_license, actual_version = util._get_license_from_url(
        'http://creativecommons.org/licenses/by/1.0/',
        path_map=path_map
    )
    expect_license, expect_version = 'by', '1.0'
    assert actual_license == expect_license
    assert actual_version == expect_version


def test_get_license_from_url_finds_correct_nonstandard_info(get_good):
    path_map = {
        'by/1.0': {'license': 'by', 'version': '1.0'},
        'zero/1.0': {'license': 'cc0', 'version': '1.0'}
    }
    actual_license, actual_version = util._get_license_from_url(
        'http://creativecommons.org/publicdomain/zero/1.0/',
        path_map=path_map
    )
    expect_license, expect_version = 'cc0', '1.0'
    assert actual_license == expect_license
    assert actual_version == expect_version


def test_get_license_from_url_finds_info_from_allcaps_path(get_good):
    path_map = {
        'by/1.0': {'license': 'by', 'version': '1.0'},
        'cc0/1.0': {'license': 'cc0', 'version': '1.0'}
    }
    actual_license, actual_version = util._get_license_from_url(
        'http://creativecommons.org/licenses/CC0/1.0/legalcode',
        path_map=path_map
    )
    expect_license, expect_version = 'cc0', '1.0'
    assert actual_license == expect_license
    assert actual_version == expect_version


def test_get_license_from_url_nones_wrong_domain(get_good):
    path_map = {'by/1.0': {'license': 'by', 'version': '1.0'}}
    actual_license, actual_version = util._get_license_from_url(
        'http://notcreativecommons.org/licenses/by/1.0/',
        path_map=path_map
    )
    expect_license, expect_version = None, None
    assert actual_license == expect_license
    assert actual_version == expect_version


def test_get_license_from_url_nones_invalid_version():
    path_map = {'by/1.0': {'license': 'by', 'version': '1.0'}}
    actual_license, actual_version = util._get_license_from_url(
        'http://creativecommons.org/licenses/by/1.2/',
        path_map=path_map
    )
    expect_license, expect_version = None, None
    assert actual_license == expect_license
    assert actual_version == expect_version


def test_get_license_from_url_nones_invalid_license():
    path_map = {'by/1.0': {'license': 'by', 'version': '1.0'}}
    actual_license, actual_version = util._get_license_from_url(
        'http://creativecommons.org/licenses/ba/1.0/',
        path_map=path_map
    )
    expect_license, expect_version = None, None
    assert actual_license == expect_license
    assert actual_version == expect_version


def test_get_license_from_url_nones_missing_url():
    actual_license, actual_version = util._get_license_from_url(None)
    expect_license, expect_version = None, None
    assert actual_license == expect_license
    assert actual_version == expect_version


def test_validate_license_pair_nones_missing_license():
    path_map = {'by/1.0': {'license': 'by', 'version': '1.0'}}
    actual_license, actual_version = util._validate_license_pair(
        None,
        '1.0',
        path_map
    )
    expect_license, expect_version = None, None
    assert actual_license == expect_license
    assert actual_version == expect_version


def test_validate_license_pair_nones_missing_version():
    path_map = {'by/1.0': {'license': 'by', 'version': '1.0'}}
    actual_license, actual_version = util._validate_license_pair(
        'by',
        None,
        path_map
    )
    expect_license, expect_version = None, None
    assert actual_license == expect_license
    assert actual_version == expect_version


def test_validate_license_pair_handles_float_version():
    path_map = {'by/1.0': {'license': 'by', 'version': '1.0'}}
    actual_license, actual_version = util._validate_license_pair(
        'by',
        1.0,
        path_map
    )
    expect_license, expect_version = 'by', '1.0'
    assert actual_license == expect_license
    assert actual_version == expect_version


def test_validate_license_pair_handles_int_version():
    path_map = {'by/1.0': {'license': 'by', 'version': '1.0'}}
    actual_license, actual_version = util._validate_license_pair(
        'by',
        1,
        path_map
    )
    expect_license, expect_version = 'by', '1.0'
    assert actual_license == expect_license
    assert actual_version == expect_version

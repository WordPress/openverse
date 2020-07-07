import logging
import requests

import pytest
import tldextract

from common.licenses import licenses

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.DEBUG)

licenses.urls.tldextract.extract = tldextract.TLDExtract(
    suffix_list_urls=None
)


@pytest.fixture
def get_good(monkeypatch):
    def mock_get(url, timeout=60):
        return requests.Response()
    monkeypatch.setattr(licenses.requests, 'get', mock_get)


@pytest.fixture
def get_bad(monkeypatch):
    def mock_get(url, timeout=60):
        raise Exception
    monkeypatch.setattr(licenses.requests, 'get', mock_get)


@pytest.fixture
def mock_rewriter(monkeypatch):
    def mock_rewrite_redirected_url(url_string):
        return url_string
    monkeypatch.setattr(
        licenses.urls, 'rewrite_redirected_url', mock_rewrite_redirected_url
    )


def test_get_license_info_prefers_derived_values(monkeypatch):
    expected_license, expected_version = 'derivedlicense', '10.0'
    expected_url = 'modified_url'

    def mock_get_license(url_string):
        return expected_url, expected_license, expected_version

    def mock_validate_pair(license_, license_version):
        return license_, license_version

    monkeypatch.setattr(licenses, '_get_license_from_url', mock_get_license)
    monkeypatch.setattr(licenses, '_validate_license_pair', mock_validate_pair)

    actual_license, actual_version, actual_url = licenses.get_license_info(
        'https://creativecommons.org/licenses/and/so/on',
        'license',
        '1.0'
    )

    assert actual_license == expected_license
    assert actual_version == expected_version
    assert actual_url == expected_url


def test_get_license_info_with_missing_derived_license(monkeypatch):
    expected_license, expected_version = 'license', '1.0'
    expected_url = 'https://creativecommons.org/licenses/and/so/on'

    def mock_get_license(url_string):
        return url_string, None, '10.0'

    def mock_validate_pair(license_, license_version):
        return license_, license_version

    monkeypatch.setattr(licenses, '_get_license_from_url', mock_get_license)
    monkeypatch.setattr(licenses, '_validate_license_pair', mock_validate_pair)

    actual_license, actual_version, actual_url = licenses.get_license_info(
        expected_url,
        expected_license,
        expected_version,
    )

    assert actual_license == expected_license
    assert actual_version == expected_version
    assert actual_url == expected_url


def test_get_license_info_with_missing_derived_version(monkeypatch):
    expected_license, expected_version = 'license', '1.0'
    expected_url = 'https://creativecommons.org/licenses/and/so/on'

    def mock_get_license(url_string):
        return url_string, 'derived_license', None

    def mock_validate_pair(license_, license_version):
        return license_, license_version

    monkeypatch.setattr(licenses, '_get_license_from_url', mock_get_license)
    monkeypatch.setattr(licenses, '_validate_license_pair', mock_validate_pair)

    actual_license, actual_version, actual_url = licenses.get_license_info(
        expected_url,
        expected_license,
        expected_version,
    )

    assert actual_license == expected_license
    assert actual_version == expected_version
    assert actual_url == expected_url


def test_get_license_from_url_finds_info_from_path(mock_rewriter):
    actual_url, actual_license, actual_version = licenses._get_license_from_url(
        'http://creativecommons.org/licenses/by/1.0/',
    )
    expect_license, expect_version = 'by', '1.0'
    assert actual_license == expect_license
    assert actual_version == expect_version


def test_get_license_from_url_finds_correct_nonstandard_info(mock_rewriter):
    actual_url, actual_license, actual_version = licenses._get_license_from_url(
        'http://creativecommons.org/publicdomain/zero/1.0/',
    )
    expect_license, expect_version = 'cc0', '1.0'
    assert actual_license == expect_license
    assert actual_version == expect_version


def test_get_license_from_url_finds_info_from_allcaps_path(mock_rewriter):
    actual_url, actual_license, actual_version = licenses._get_license_from_url(
        'http://creativecommons.org/licenses/CC0/1.0/legalcode',
    )
    expect_license, expect_version = 'cc0', '1.0'
    assert actual_license == expect_license
    assert actual_version == expect_version


def test_get_license_from_url_nones_wrong_domain(mock_rewriter):
    actual_url, actual_license, actual_version = licenses._get_license_from_url(
        'http://notcreativecommons.org/licenses/by/1.0/',
    )
    expect_license, expect_version = None, None
    assert actual_license == expect_license
    assert actual_version == expect_version


def test_get_license_from_url_nones_invalid_version(mock_rewriter):
    actual_url, actual_license, actual_version = licenses._get_license_from_url(
        'http://creativecommons.org/licenses/by/1.2/',
    )
    expect_license, expect_version = None, None
    assert actual_license == expect_license
    assert actual_version == expect_version


def test_get_license_from_url_nones_invalid_license(mock_rewriter):
    actual_url, actual_license, actual_version = licenses._get_license_from_url(
        'http://creativecommons.org/licenses/ba/1.0/',
    )
    expect_license, expect_version = None, None
    assert actual_license == expect_license
    assert actual_version == expect_version


def test_get_license_from_url_nones_missing_url(mock_rewriter):
    actual_url, actual_license, actual_version = licenses._get_license_from_url(
        None
    )
    expect_license, expect_version = None, None
    assert actual_license == expect_license
    assert actual_version == expect_version


def test_validate_license_pair_nones_missing_license():
    path_map = {'by/1.0': {'license': 'by', 'version': '1.0'}}
    actual_license, actual_version = licenses._validate_license_pair(
        None,
        '1.0',
        path_map
    )
    expect_license, expect_version = None, None
    assert actual_license == expect_license
    assert actual_version == expect_version


def test_validate_license_pair_nones_missing_version():
    path_map = {'by/1.0': {'license': 'by', 'version': '1.0'}}
    actual_license, actual_version = licenses._validate_license_pair(
        'by',
        None,
        path_map
    )
    expect_license, expect_version = None, None
    assert actual_license == expect_license
    assert actual_version == expect_version


def test_validate_license_pair_handles_float_version():
    path_map = {'by/1.0': {'license': 'by', 'version': '1.0'}}
    actual_license, actual_version = licenses._validate_license_pair(
        'by',
        1.0,
        path_map
    )
    expect_license, expect_version = 'by', '1.0'
    assert actual_license == expect_license
    assert actual_version == expect_version


def test_validate_license_pair_handles_int_version():
    path_map = {'by/1.0': {'license': 'by', 'version': '1.0'}}
    actual_license, actual_version = licenses._validate_license_pair(
        'by',
        1,
        path_map
    )
    expect_license, expect_version = 'by', '1.0'
    assert actual_license == expect_license
    assert actual_version == expect_version

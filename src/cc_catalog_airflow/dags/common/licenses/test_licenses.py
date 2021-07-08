import logging

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
def mock_rewriter(monkeypatch):
    def mock_rewrite_redirected_url(url_string):
        return url_string
    monkeypatch.setattr(
        licenses.urls, 'rewrite_redirected_url', mock_rewrite_redirected_url
    )


@pytest.fixture
def mock_cc_url_validator(monkeypatch):
    def mock_get_valid_cc_url(url_string):
        return url_string
    monkeypatch.setattr(
        licenses, '_get_valid_cc_url', mock_get_valid_cc_url
    )


def test_get_license_info_prefers_derived_values(monkeypatch):
    expected_license, expected_version = 'derivedlicense', '10.0'
    expected_url = 'https://creativecommons.org/licenses/and/so/on'
    expected_raw_url = None

    def mock_get_license_from_url(url_string, path_map=None):
        return expected_license, expected_version, expected_url, None

    monkeypatch.setattr(
        licenses, '_get_license_info_from_url', mock_get_license_from_url
    )

    (
        actual_license, actual_version, actual_url, actual_raw_url
    ) = licenses.get_license_info(
        expected_url,
        'license',
        '1.0'
    )

    assert actual_license == expected_license
    assert actual_version == expected_version
    assert actual_url == expected_url
    assert actual_raw_url == expected_raw_url


def test_get_license_info_falls_back_with_invalid_license_url(
        mock_rewriter, monkeypatch,
):
    expected_license = 'cc0'
    expected_version = '1.0'
    expected_url = 'https://creativecommons.org/publicdomain/zero/1.0/'
    expected_raw_url = 'https://licenses.com/my/license'

    def mock_cc_license_validator(url_string):
        return None
    monkeypatch.setattr(
        licenses, '_get_valid_cc_url', mock_cc_license_validator
    )

    (
        actual_license, actual_version, actual_url, actual_raw_url
    ) = licenses.get_license_info(
        license_url='https://licenses.com/my/license',
        license_='cc0',
        license_version='1.0'
    )
    assert actual_license == expected_license
    assert actual_version == expected_version
    assert actual_url == expected_url
    assert actual_raw_url == expected_raw_url


def test_get_valid_cc_url_makes_url_lowercase(mock_rewriter):
    actual_url = licenses._get_valid_cc_url(
        'http://creativecommons.org/licenses/CC0/1.0/legalcode',
    )
    expected_url = actual_url.lower()
    assert actual_url == expected_url


def test_get_valid_cc_url_nones_wrong_domain(mock_rewriter):
    actual_url = licenses._get_valid_cc_url(
        'http://notcreativecommons.org/licenses/licenses/by/1.0/',
    )
    assert actual_url is None


def test_get_valid_cc_url_nones_missing_url(mock_rewriter):
    actual_url = licenses._get_valid_cc_url(None)
    assert actual_url is None


def test_get_valid_cc_url_uses_rewritten_url(monkeypatch):
    expected_url = 'https://creativecommons.org/licenses/licenses/by/1.0/'

    def mock_rewrite_redirected_url(url_string):
        return expected_url

    monkeypatch.setattr(
        licenses.urls, 'rewrite_redirected_url', mock_rewrite_redirected_url
    )
    actual_url = licenses._get_valid_cc_url(
        'http://creativecommons.org/a/b/c/d/'
    )
    assert actual_url == expected_url


def test_get_valid_cc_url_handles_none_rewritten_url(monkeypatch):
    def mock_rewrite_redirected_url(url_string):
        return None

    monkeypatch.setattr(
        licenses.urls, 'rewrite_redirected_url', mock_rewrite_redirected_url
    )
    actual_url = licenses._get_valid_cc_url(
        'http://creativecommons.org/a/b/c/d/'
    )
    assert actual_url is None


def test_get_valid_cc_url_nones_invalid_rewritten_url(monkeypatch):
    def mock_rewrite_redirected_url(url_string):
        return 'https://creativecommons.org/abcljasdf'

    monkeypatch.setattr(
        licenses.urls, 'rewrite_redirected_url', mock_rewrite_redirected_url
    )
    actual_url = licenses._get_valid_cc_url(
        'http://creativecommons.org/a/b/c/d/'
    )
    assert actual_url is None


def test_get_license_info_from_url_with_license_url_path_mismatch(
        mock_cc_url_validator,
        monkeypatch
):
    license_url = 'https://not.in/path/map'
    path_map = {'publicdomain/zero/1.0': ('cc0', '1.0')}
    license_info = licenses._get_license_info_from_url(
        license_url, path_map=path_map
    )
    assert all([i is None for i in license_info])


def test_get_license_info_from_url_with_good_license_url(
        mock_cc_url_validator
):
    expected_license, expected_version = 'cc0', '1.0'
    license_url = 'https://creativecommons.org/publicdomain/zero/1.0/'
    path_map = {'publicdomain/zero/1.0': ('cc0', '1.0')}
    actual_license_info = licenses._get_license_info_from_url(
        license_url, path_map=path_map
    )
    expected_license_info = (
        expected_license, expected_version, license_url, license_url
    )
    assert actual_license_info == expected_license_info


def test_get_license_info_from_license_pair_nones_when_missing_license(
        mock_rewriter
):
    pair_map = {('by', '1.0'): 'licenses/by/1.0'}
    license_info = licenses._get_license_info_from_license_pair(
        None,
        '1.0',
        pair_map=pair_map
    )
    assert all([i is None for i in license_info])


def test_get_license_info_from_license_pair_nones_missing_version(
        mock_rewriter
):
    pair_map = {('by', '1.0'): 'licenses/by/1.0'}
    license_info = licenses._get_license_info_from_license_pair(
        'by',
        None,
        pair_map=pair_map
    )
    assert all([i is None for i in license_info])


def test_validate_license_pair_handles_float_version(mock_rewriter):
    pair_map = {('by', '1.0'): 'licenses/by/1.0'}
    actual_license_info = licenses._get_license_info_from_license_pair(
        'by',
        1.0,
        pair_map=pair_map
    )
    expected_license_info = (
        'by', '1.0', 'https://creativecommons.org/licenses/by/1.0/'
    )
    assert actual_license_info == expected_license_info


def test_validate_license_pair_handles_int_version(mock_rewriter):
    pair_map = {('by', '1.0'): 'licenses/by/1.0'}
    actual_license_info = licenses._get_license_info_from_license_pair(
        'by',
        1,
        pair_map=pair_map
    )
    expected_license_info = (
        'by', '1.0', 'https://creativecommons.org/licenses/by/1.0/'
    )
    assert actual_license_info == expected_license_info


def test_validate_license_pair_handles_na_version(mock_rewriter):
    pair_map = {('publicdomain', 'N/A'): 'licenses/publicdomain'}
    actual_license_info = licenses._get_license_info_from_license_pair(
        'publicdomain',
        'N/A',
        pair_map=pair_map
    )
    expected_license_info = (
        'publicdomain',
        'N/A',
        'https://creativecommons.org/licenses/publicdomain/'
    )
    assert actual_license_info == expected_license_info


def test_build_license_url_raises_exception_when_derived_url_unrewritable(
        monkeypatch
):
    monkeypatch.setattr(
        licenses.urls,
        'rewrite_redirected_url',
        lambda x: None
    )

    with pytest.raises(licenses.InvalidLicenseURLException):
        licenses._build_license_url('abcdefg')

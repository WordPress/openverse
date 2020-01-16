import logging

from storage import util

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.DEBUG)


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


def test_validate_url_string_discards_without_scheme():
    url_string = 'creativecomons.org'
    actual_validated_url = util.validate_url_string(url_string)
    expect_validated_url = None
    assert actual_validated_url == expect_validated_url


def test_validate_url_string_discards_without_domain():
    url_string = 'https:/abcd'
    actual_validated_url = util.validate_url_string(url_string)
    expect_validated_url = None
    assert actual_validated_url == expect_validated_url


def test_ensure_int_nones_non_number_strings():
    actual_int = util.ensure_int('abc123')
    expect_int = None
    assert actual_int == expect_int


def test_ensure_int_truncates_floats():
    actual_int = util.ensure_int(2.34)
    expect_int = 2
    assert actual_int == expect_int


def test_ensure_int_casts_and_truncates_float_strings():
    actual_int = util.ensure_int('3.45')
    expect_int = 3
    assert actual_int == expect_int


def test_ensure_int_leaves_ints():
    actual_int = util.ensure_int(4)
    expect_int = 4
    assert actual_int == expect_int


def test_ensure_int_casts_int_strings():
    actual_int = util.ensure_int('5')
    expect_int = 5
    assert actual_int == expect_int


def test_ensure_sql_bool_defaults_to_none():
    actual_bool = util.ensure_sql_bool('g')
    expect_bool = None
    assert actual_bool == expect_bool


def test_ensure_sql_bool_leaves_t():
    actual_bool = util.ensure_sql_bool('t')
    expect_bool = 't'
    assert actual_bool == expect_bool


def test_ensure_sql_bool_leaves_f():
    actual_bool = util.ensure_sql_bool('f')
    expect_bool = 'f'
    assert actual_bool == expect_bool


def test_enforce_char_limit_leaves_shorter_strings_unchanged():
    actual_string = util.enforce_char_limit('abcde', 5)
    expect_string = 'abcde'
    assert actual_string == expect_string


def test_enforce_char_limit_truncates_long_strings_by_default():
    actual_string = util.enforce_char_limit('abcdef', 5)
    expect_string = 'abcde'
    assert actual_string == expect_string


def test_enforce_char_limit_nones_long_strings_with_flag():
    actual_string = util.enforce_char_limit('abcdef', 5, truncate=False)
    expect_string = None
    assert actual_string == expect_string


def test_get_provider_and_source_preserves_given_both():
    expect_provider, expect_source = 'Provider', 'Source'
    actual_provider, actual_source = util.get_provider_and_source(
        expect_provider, expect_source
    )
    assert actual_provider == expect_provider
    assert actual_source == expect_source


def test_get_provider_and_source_preserves_given_both_and_default():
    expect_provider, expect_source = 'Provider', 'Source'
    actual_provider, actual_source = util.get_provider_and_source(
        expect_provider, expect_source, default='default_provider'
    )
    assert actual_provider == expect_provider
    assert actual_source == expect_source


def test_get_provider_and_source_preserves_source_without_provider():
    input_provider, expect_source = None, 'Source'
    actual_provider, actual_source = util.get_provider_and_source(
        input_provider, expect_source
    )
    assert actual_source == expect_source


def test_get_provider_and_source_keeps_source_without_provider_with_default():
    input_provider, expect_source = None, 'Source'
    actual_provider, actual_source = util.get_provider_and_source(
        input_provider, expect_source, default='Default Provider'
    )
    assert actual_source == expect_source


def test_get_provider_and_source_fills_source_if_none_given():
    input_provider, input_source = 'Provider', None
    actual_provider, actual_source = util.get_provider_and_source(
        input_provider, input_source
    )
    expect_provider, expect_source = 'Provider', 'Provider'
    assert actual_provider == expect_provider
    assert actual_source == expect_source


def test_get_provider_and_source_fills_both_from_default_if_none_given():
    input_provider, input_source = None, None
    actual_provider, actual_source = util.get_provider_and_source(
        input_provider, input_source, default='Default'
    )
    expect_provider, expect_source = 'Default', 'Default'
    assert actual_provider == expect_provider
    assert actual_source == expect_source


def test_enforce_all_arguments_truthy_false_when_one_argument_is_empty_str():
    truthy = util.enforce_all_arguments_truthy(
        dog='dog',
        cat=''
    )
    assert truthy is False


def test_enforce_all_arguments_truthy_false_when_one_argument_is_nonetype():
    truthy = util.enforce_all_arguments_truthy(
        dog='dog',
        cat='cat',
        rat=None
    )
    assert truthy is False


def test_enforce_all_arguments_truthy_false_when_truthy_is_last():
    truthy = util.enforce_all_arguments_truthy(
        dog='dog',
        cat=None,
        rat='rat'
    )
    assert truthy is False


def test_enforce_all_arguments_truthy_false_when_one_is_empty_list():
    truthy = util.enforce_all_arguments_truthy(
        dog='dog',
        cat=[],
        rat='rat'
    )
    assert truthy is False


def test_enforce_all_arguments_truthy_false_when_one_is_empty_dict():
    truthy = util.enforce_all_arguments_truthy(
        dog='dog',
        cat={},
        rat='rat'
    )
    assert truthy is False


def test_enforce_all_arguments_truthy_false_when_one_is_zero():
    truthy = util.enforce_all_arguments_truthy(
        dog='dog',
        cat=0,
        rat='rat'
    )
    assert truthy is False


def test_enforce_all_arguments_truthy_true_with_different_types():
    truthy = util.enforce_all_arguments_truthy(
        ant=2,
        bat={'animal': 'bat'},
        dog='dog',
        cat=['cat'],
    )
    assert truthy is True


def test_get_license_from_url_finds_info_from_path():
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


def test_get_license_from_url_finds_correct_nonstandard_info():
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


def test_get_license_from_url_finds_info_from_allcaps_path():
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


def test_get_license_from_url_nones_wrong_domain():
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

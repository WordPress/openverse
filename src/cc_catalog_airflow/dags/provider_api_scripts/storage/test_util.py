import logging
import string

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


def test_enforce_char_limit_nones_non_strings():
    actual_string = util.enforce_char_limit(3, 5)
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


def test_prepare_output_field_string_makes_falsy_into_nullchar():
    for i in ['', 0, 0.0, [], {}, (), set()]:
        actual_str = util.prepare_output_field_string(i)
        expect_str = '\\N'
        assert actual_str == expect_str


def test_prepare_output_field_string_sanitizes_dict_json(monkeypatch):
    def mock_sanitize_json(unknown_input):
        unknown_input['a'] = 'sanitized'
        return unknown_input
    monkeypatch.setattr(util, '_sanitize_json_values', mock_sanitize_json)
    input_dict = {'a': 'dict'}
    actual_str = util.prepare_output_field_string(input_dict)
    expect_str = '{"a": "sanitized"}'
    assert actual_str == expect_str


def test_prepare_output_field_string_sanitizes_list_json(monkeypatch):
    def mock_sanitize_json(unknown_input):
        unknown_input.append('sanitized')
        return unknown_input
    monkeypatch.setattr(util, '_sanitize_json_values', mock_sanitize_json)
    input_dict = ['a', 'list']
    actual_str = util.prepare_output_field_string(input_dict)
    expect_str = '["a", "list", "sanitized"]'
    assert actual_str == expect_str


def test_prepare_output_field_string_casts_to_strings():
    # This test is just in case we someday stop using sanitize_string on the
    # output of this function.
    for i in [3, '2.3', 2.3, ';', {'a': 'dict'}, ['a', 'list']]:
        assert type(util.prepare_output_field_string(i)) == str


def test_sanitize_json_values_handles_flat_dict(monkeypatch):
    def mock_sanitize_string(some_string):
        return some_string + ' sanitized'
    monkeypatch.setattr(util, '_sanitize_string', mock_sanitize_string)
    given_dict = {'key1': 'val1', 'key2': 'val2'}
    actual_dict = util._sanitize_json_values(given_dict)
    expect_dict = {'key1': 'val1 sanitized', 'key2': 'val2 sanitized'}
    assert expect_dict == actual_dict


def test_sanitize_json_values_handles_nested_dict(monkeypatch):
    def mock_sanitize_string(some_string):
        return some_string + ' sanitized'
    monkeypatch.setattr(util, '_sanitize_string', mock_sanitize_string)
    given_dict = {'key1': 'val1', 'key2': {'key3': 'val3'}}
    actual_dict = util._sanitize_json_values(given_dict)
    expect_dict = {
        'key1': 'val1 sanitized', 'key2': {'key3': 'val3 sanitized'}
    }
    assert expect_dict == actual_dict


def test_sanitize_json_values_handles_dict_containing_list(monkeypatch):
    def mock_sanitize_string(some_string):
        return some_string + ' sanitized'
    monkeypatch.setattr(util, '_sanitize_string', mock_sanitize_string)
    given_dict = {'key1': 'val1', 'key2': ['item1', 'item2']}
    actual_dict = util._sanitize_json_values(given_dict)
    expect_dict = {
        'key1': 'val1 sanitized',
        'key2': ['item1 sanitized', 'item2 sanitized']
    }
    assert expect_dict == actual_dict


def test_sanitize_json_values_handles_list_of_str(monkeypatch):
    def mock_sanitize_string(some_string):
        return some_string + ' sanitized'
    monkeypatch.setattr(util, '_sanitize_string', mock_sanitize_string)
    given_list = ['item1', 'item2']
    actual_list = util._sanitize_json_values(given_list)
    expect_list = ['item1 sanitized', 'item2 sanitized']
    assert expect_list == actual_list


def test_sanitize_json_values_handles_list_of_list(monkeypatch):
    def mock_sanitize_string(some_string):
        return some_string + ' sanitized'
    monkeypatch.setattr(util, '_sanitize_string', mock_sanitize_string)
    given_list = ['item1', ['item2', ['item3'], 'item4'], 'item5']
    actual_list = util._sanitize_json_values(given_list)
    expect_list = [
        'item1 sanitized', [
            'item2 sanitized', [
                'item3 sanitized'
            ], 'item4 sanitized'
        ], 'item5 sanitized'
    ]
    assert expect_list == actual_list


def test_sanitize_json_values_handles_list_of_dict(monkeypatch):
    def mock_sanitize_string(some_string):
        return some_string + ' sanitized'
    monkeypatch.setattr(util, '_sanitize_string', mock_sanitize_string)
    given_list = [
        {'name': 'valuea', 'provider': 'valueb'},
        {'name': 'aname', 'provider': 'aprovider'}
    ]
    actual_list = util._sanitize_json_values(given_list)
    expect_list = [
        {'name': 'valuea sanitized', 'provider': 'valueb sanitized'},
        {'name': 'aname sanitized', 'provider': 'aprovider sanitized'}
    ]
    assert expect_list == actual_list


def test_sanitize_json_values_does_not_over_recurse(monkeypatch):
    def mock_sanitize_string(some_string):
        return str(some_string)
    monkeypatch.setattr(util, '_sanitize_string', mock_sanitize_string)
    L = []
    L.extend([L])
    actual_list = util._sanitize_json_values(L, recursion_limit=3)
    expect_list = [[['[[...]]']]]
    assert actual_list == expect_list


def test_sanitize_string_replaces_whitespaces():
    for s in string.whitespace:
        for i in range(1, 3):
            test_string = 'a' + s*i + 'b'
            actual_sanitized = util._sanitize_string(test_string)
            expect_sanitized = 'a b'
            assert actual_sanitized == expect_sanitized


def test_sanitize_string_casts_to_strings():
    input_list = [
        1, False
    ]
    for i in input_list:
        assert type(util._sanitize_string(i)) == str


def test_sanitize_string_converts_nonetype_to_empty_str():
    actual_str = util._sanitize_string(None)
    expect_str = ''
    assert actual_str == expect_str


def test_sanitize_string_removes_backspace_char():
    actual_str = util._sanitize_string('a\bc\b')
    expect_str = 'ac'
    assert actual_str == expect_str


def test_sanitize_string_switches_double_quotes_to_single():
    actual_str = util._sanitize_string('I said, "Hello!"')
    expect_str = "I said, 'Hello!'"
    assert actual_str == expect_str


def test_sanitize_string_escapes_escaped_escapes():
    actual_str = util._sanitize_string('a\t\\N\b')
    expect_str = "a \\\\N"
    assert actual_str == expect_str


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


def test_get_license_from_url_nones_missing_url():
    path_map = {'by/1.0': {'license': 'by', 'version': '1.0'}}
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

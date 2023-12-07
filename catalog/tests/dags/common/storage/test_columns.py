import logging
import string

import pytest
import tldextract

from common import urls
from common.storage import columns
from common.storage.columns import Datatype


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.DEBUG
)


urls.tldextract.extract = tldextract.TLDExtract(suffix_list_urls=None)


class TruncateColumn(columns.Column):
    def __init__(self, size, truncate):
        self.SIZE = size
        self.TRUNCATE = truncate
        super().__init__("test_column", False, datatype=Datatype.char)

    def prepare_string(self, value):
        return self._Column__enforce_char_limit(value, self.SIZE, self.TRUNCATE)


def test_Column_enforce_char_limit_leaves_shorter_strings_unchanged():
    tc = TruncateColumn(5, True)
    actual_string = tc.prepare_string("abcde")
    expect_string = "abcde"
    assert actual_string == expect_string


def test_Column_enforce_char_limit_truncates_long_strings_appropriately():
    tc = TruncateColumn(5, True)
    actual_string = tc.prepare_string("abcdef")
    expect_string = "abcde"
    assert actual_string == expect_string


def test_Column_enforce_char_limit_nones_long_strings_with_flag():
    tc = TruncateColumn(5, False)
    actual_string = tc.prepare_string("abcdef")
    expect_string = None
    assert actual_string == expect_string


def test_Column_enforce_char_limit_nones_non_strings():
    tc = TruncateColumn(5, False)
    actual_string = tc.prepare_string(3)
    expect_string = None
    assert actual_string == expect_string


class SanitizeStringColumn(columns.Column):
    def __init__(self):
        super().__init__("test_column", False)

    def prepare_string(self, value):
        return self._Column__sanitize_string(value)


def test_Column_sanitize_string_replaces_whitespaces():
    sc = SanitizeStringColumn()
    for s in string.whitespace:
        for i in range(1, 3):
            test_string = "a" + s * i + "b"
            actual_sanitized = sc._Column__sanitize_string(test_string)
            expect_sanitized = "a b"
            assert actual_sanitized == expect_sanitized


def test_Column_sanitize_string_casts_to_strings():
    sc = SanitizeStringColumn()
    input_list = [1, False]
    for i in input_list:
        assert isinstance(sc._Column__sanitize_string(i), str)


def test_Column_sanitize_string_leaves_nonetype_unchanged():
    sc = SanitizeStringColumn()
    actual_str = sc._Column__sanitize_string(None)
    expect_str = None
    assert actual_str == expect_str


def test_Column_sanitize_string_removes_backspace_char():
    sc = SanitizeStringColumn()
    actual_str = sc._Column__sanitize_string("a\bc\b")
    expect_str = "ac"
    assert actual_str == expect_str


def test_Column_sanitize_string_switches_double_quotes_to_single():
    sc = SanitizeStringColumn()
    actual_str = sc._Column__sanitize_string('I said, "Hello!"')
    expect_str = "I said, 'Hello!'"
    assert actual_str == expect_str


def test_Column_sanitize_string_escapes_escaped_escapes():
    sc = SanitizeStringColumn()
    actual_str = sc._Column__sanitize_string("a\t\\N\b")
    expect_str = "a \\\\N"
    assert actual_str == expect_str


def test_IntegerColumn_prepare_string_nones_non_number_strings():
    ic = columns.IntegerColumn("test", False)
    actual_int = ic.prepare_string("abc123")
    expect_int = None
    assert actual_int == expect_int


def test_IntegerColumn_prepare_string_truncates_floats():
    ic = columns.IntegerColumn("test", False)
    actual_int = ic.prepare_string(2.34)
    expect_int = "2"
    assert actual_int == expect_int


def test_IntegerColumn_prepare_string_casts_and_truncates_float_strings():
    ic = columns.IntegerColumn("test", False)
    actual_int = ic.prepare_string("3.45")
    expect_int = "3"
    assert actual_int == expect_int


def test_IntegerColumn_prepare_string_casts_ints():
    ic = columns.IntegerColumn("test", False)
    actual_int = ic.prepare_string(4)
    expect_int = "4"
    assert actual_int == expect_int


def test_IntegerColumn_prepare_string_leaves_int_strings():
    ic = columns.IntegerColumn("test", False)
    actual_int = ic.prepare_string("5")
    expect_int = "5"
    assert actual_int == expect_int


def test_BooleanColumn_prepare_string_falls_back_to_none():
    bc = columns.BooleanColumn("test", False)
    actual_bool = bc.prepare_string("g")
    expect_bool = None
    assert actual_bool == expect_bool


def test_BooleanColumn_prepare_string_leaves_t():
    bc = columns.BooleanColumn("test", False)
    actual_bool = bc.prepare_string("t")
    expect_bool = "t"
    assert actual_bool == expect_bool


def test_BooleanColumn_prepare_string_leaves_f():
    bc = columns.BooleanColumn("test", False)
    actual_bool = bc.prepare_string("f")
    expect_bool = "f"
    assert actual_bool == expect_bool


def test_BooleanColumn_prepare_string_casts_truthlike():
    bc = columns.BooleanColumn("test", False)
    truthlike_values = [True, "true", "True", "t", "T"]
    assert all([bc.prepare_string(v) == "t" for v in truthlike_values])


def test_BooleanColumn_prepare_string_casts_falselike():
    bc = columns.BooleanColumn("test", False)
    falselike_values = [False, "false", "False", "f", "F"]
    assert all([bc.prepare_string(v) == "f" for v in falselike_values])


def test_JSONColumn_prepare_string_nones_empty_list():
    jc = columns.JSONColumn("test", False)
    L = []
    actual_json = jc.prepare_string(L)
    expect_json = None
    assert actual_json == expect_json


def test_JSONColumn_prepare_string_nones_empty_dict():
    jc = columns.JSONColumn("test", False)
    D = {}
    actual_json = jc.prepare_string(D)
    expect_json = None
    assert actual_json == expect_json


def test_JSONColumn_prepare_string_returns_json_string():
    jc = columns.JSONColumn("test", False)
    D = {"test": "dict"}
    actual_json = jc.prepare_string(D)
    expect_json = '{"test": "dict"}'
    assert actual_json == expect_json


def test_JSONColumn_prepare_string_returns_unicode_json_string():
    jc = columns.JSONColumn("test", False)
    D = {"test": "A unicode \u018e string \xf1"}
    actual_json = jc.prepare_string(D)
    expect_json = '{"test": "A unicode Ǝ string ñ"}'
    assert actual_json == expect_json


def test_JSONColumn_sanitize_json_values_handles_flat_dict(monkeypatch):
    jc = columns.JSONColumn("test", False)

    def mock_sanitize_string(some_string):
        return some_string + " sanitized"

    monkeypatch.setattr(jc, "_Column__sanitize_string", mock_sanitize_string)
    given_dict = {"key1": "val1", "key2": "val2"}
    actual_dict = jc._sanitize_json_values(given_dict)
    expect_dict = {"key1": "val1 sanitized", "key2": "val2 sanitized"}
    assert expect_dict == actual_dict


def test_JSONColumn_sanitize_json_values_handles_nested_dict(monkeypatch):
    jc = columns.JSONColumn("test", False)

    def mock_sanitize_string(some_string):
        return some_string + " sanitized"

    monkeypatch.setattr(jc, "_Column__sanitize_string", mock_sanitize_string)
    given_dict = {"key1": "val1", "key2": {"key3": "val3"}}
    actual_dict = jc._sanitize_json_values(given_dict)
    expect_dict = {"key1": "val1 sanitized", "key2": {"key3": "val3 sanitized"}}
    assert expect_dict == actual_dict


def test_JSONColumn_sanitize_json_values_handles_dict_with_list(monkeypatch):
    jc = columns.JSONColumn("test", False)

    def mock_sanitize_string(some_string):
        return some_string + " sanitized"

    monkeypatch.setattr(jc, "_Column__sanitize_string", mock_sanitize_string)
    given_dict = {"key1": "val1", "key2": ["item1", "item2"]}
    actual_dict = jc._sanitize_json_values(given_dict)
    expect_dict = {
        "key1": "val1 sanitized",
        "key2": ["item1 sanitized", "item2 sanitized"],
    }
    assert expect_dict == actual_dict


def test_JSONColumn_sanitize_json_values_handles_list_of_str(monkeypatch):
    jc = columns.JSONColumn("test", False)

    def mock_sanitize_string(some_string):
        return some_string + " sanitized"

    monkeypatch.setattr(jc, "_Column__sanitize_string", mock_sanitize_string)
    given_list = ["item1", "item2"]
    actual_list = jc._sanitize_json_values(given_list)
    expect_list = ["item1 sanitized", "item2 sanitized"]
    assert expect_list == actual_list


def test_JSONColumn_sanitize_json_values_handles_list_of_list(monkeypatch):
    jc = columns.JSONColumn("test", False)

    def mock_sanitize_string(some_string):
        return some_string + " sanitized"

    monkeypatch.setattr(jc, "_Column__sanitize_string", mock_sanitize_string)
    given_list = ["item1", ["item2", ["item3"], "item4"], "item5"]
    actual_list = jc._sanitize_json_values(given_list)
    expect_list = [
        "item1 sanitized",
        ["item2 sanitized", ["item3 sanitized"], "item4 sanitized"],
        "item5 sanitized",
    ]
    assert expect_list == actual_list


def test_JSONColumn_sanitize_json_values_handles_list_of_dict(monkeypatch):
    jc = columns.JSONColumn("test", False)

    def mock_sanitize_string(some_string):
        return some_string + " sanitized"

    monkeypatch.setattr(jc, "_Column__sanitize_string", mock_sanitize_string)
    given_list = [
        {"name": "valuea", "provider": "valueb"},
        {"name": "aname", "provider": "aprovider"},
    ]
    actual_list = jc._sanitize_json_values(given_list)
    expect_list = [
        {"name": "valuea sanitized", "provider": "valueb sanitized"},
        {"name": "aname sanitized", "provider": "aprovider sanitized"},
    ]
    assert expect_list == actual_list


def test_JSONColumn_sanitize_json_values_does_not_over_recurse(monkeypatch):
    jc = columns.JSONColumn("test", False)

    def mock_sanitize_string(some_string):
        return str(some_string)

    monkeypatch.setattr(jc, "_Column__sanitize_string", mock_sanitize_string)
    L = []
    L.extend([L])
    actual_list = jc._sanitize_json_values(L, recursion_limit=3)
    expect_list = [[["[[...]]"]]]
    assert actual_list == expect_list


def test_StringColumn_prepare_string_sanitizes_then_limits_chars(monkeypatch):
    sc = columns.StringColumn("test", False, 10, True)

    def mock_sanitize_string(some_string):
        return some_string + " sanitized"

    monkeypatch.setattr(sc, "_Column__sanitize_string", mock_sanitize_string)
    actual_str = sc.prepare_string("test str")
    expect_str = "test str s"
    assert actual_str == expect_str


def test_URLColumn_prepare_string_nones_unclean_input(monkeypatch):
    uc = columns.URLColumn("test", False, 100)

    def mock_sanitize_string(some_string):
        return some_string + "diff string"

    monkeypatch.setattr(uc, "_Column__sanitize_string", mock_sanitize_string)
    actual_str = uc.prepare_string("test string")
    expect_str = None
    assert actual_str == expect_str


def test_ArrayColumn_of_StringColumn_prepare_string_returns_pg_array():
    ac = columns.ArrayColumn(
        "test",
        False,
        columns.StringColumn(name="test", size=80, required=False, truncate=False),
    )
    given_list = ["item1", "item2"]
    actual_str = ac.prepare_string(given_list)
    expected_str = '{"item1", "item2"}'
    assert actual_str == expected_str


def test_ArrayColumn_prepare_string_returns_pg_array_from_single_string():
    ac = columns.ArrayColumn(
        "test",
        False,
        columns.StringColumn(name="test", size=80, required=False, truncate=False),
    )
    actual_str = ac.prepare_string("abcdef")
    expected_str = "{abcdef}"
    assert actual_str == expected_str


def test_ArrayColumn_of_IntegerColumn_prepare_string_returns_pg_array():
    ac = columns.ArrayColumn(
        "test", False, columns.IntegerColumn(name="test", required=False)
    )
    given_list = [1.1, 22, 3, 456]
    actual_str = ac.prepare_string(given_list)
    expected_str = '{"1", "22", "3", "456"}'
    assert actual_str == expected_str


@pytest.mark.parametrize(
    "function, prefix, args, expected_output",
    [
        ("my_func", "", [], "my_func()"),
        ("my_func", "EXCLUDED.", [], "my_func()"),
        ("my_func", "", ["foo"], "my_func(foo)"),
        ("my_func", "", ["foo", "bar"], "my_func(foo, bar)"),
        ("my_func", "EXCLUDED.", ["foo"], "my_func(EXCLUDED.foo)"),
        ("my_func", "EXCLUDED.", ["foo", "bar"], "my_func(EXCLUDED.foo, EXCLUDED.bar)"),
        ("my_func", "", [1, 2, "foo"], "my_func(1, 2, foo)"),
    ],
)
def test_calculate_value(function, prefix, args, expected_output):
    actual_output = columns._calculate_value(function, prefix, *args)
    assert actual_output == expected_output


@pytest.mark.parametrize(
    "input, expected_output",
    [
        # returns None for non-number strings
        ("abc123", None),
        # Returns string representation of float when possible
        (2.34, "2.34"),
        ("3.45", "3.45"),
        (4, "4.0"),
        ("5", "5.0"),
        # Maximally preserves sigfigs
        (1.123456789012345678901234567890, "1.1234567890123457"),
    ],
)
def test_CalculatedColumn_prepare_string_nones_non_number_strings(
    input, expected_output
):
    cc = columns.CalculatedColumn("test", False, [])
    actual_output = cc.prepare_string(input)
    assert actual_output == expected_output


def test_CalculatedColumn_get_insert_value():
    cc = columns.CalculatedColumn("test", required=False, sql_args=["foo", "bar"])
    actual_insert_value = cc.get_insert_value(sql_function="my_func")

    # _calculate_value is tested separately
    assert actual_insert_value == "my_func(foo, bar)"


def test_CalculatedColumn_get_update_value():
    cc = columns.CalculatedColumn("test", required=False, sql_args=["foo", "bar"])
    actual_insert_value = cc.get_update_value(sql_function="my_func")

    # _calculate_value is tested separately
    assert actual_insert_value == "test = my_func(EXCLUDED.foo, EXCLUDED.bar)"

import pytest

from api.utils.url import add_protocol


@pytest.mark.parametrize(
    "url, expected",
    [
        (None, None),
        ("", None),
        ("https://example.com/a", "https://example.com/a"),
        ("http://example.com/a", "http://example.com/a"),
        ("example.com/a", "https://example.com/a"),
        ("example.com:8080/user", "https://example.com:8080/user"),
        ("javascript:void(0)", None),
        ("JavaScript:void(0)", None),
        ("  javascript:void(0)", None),
        ("data:text/html,x", None),
        ("vbscript:x", None),
        ("ftp://example.com/a", None),
    ],
)
def test_add_protocol(url, expected):
    assert add_protocol(url) == expected

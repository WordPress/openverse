import html

import pytest

from common.text import strip_markup


# Entity-encoded markup must be stripped the same way as literal markup.
ENCODED_MARKUP = "&lt;iframe&gt;X&lt;/iframe&gt;"


@pytest.mark.parametrize(
    "value, expected",
    [
        (None, None),
        ("", ""),
        ("Jane Doe", "Jane Doe"),
        ("  Jane \n\t Doe ", "  Jane \n\t Doe "),
        ("Tom &amp; Jerry &lt;3 Photography", "Tom &amp; Jerry &lt;3 Photography"),
        ("a < b > c", "a < b > c"),
        ("<b>Jane</b> Doe", "Jane Doe"),
        ("<p>Coffee Bean with bags</p>\n", "Coffee Bean with bags"),
        ("<iframe>X</iframe>", "X"),
        (ENCODED_MARKUP, "X"),
        (html.escape(ENCODED_MARKUP), "X"),
        ("Tom &amp; Jerry &lt;b&gt;Photography&lt;/b&gt;", "Tom & Jerry Photography"),
        ("<untitled>", ""),
        ("<no title>", ""),
        ("&lt;Untitled&gt;", ""),
        ("<untitled-item>", ""),
        ("<x onclick=f()>X</x>", "X"),
        ("<x onclick>X</x>", "X"),
        ("<x href=javascript:f()>X</x>", "X"),
        ("<svg onload=f()>", ""),
        ("<IFRAME>X</IFRAME>", "X"),
        ("<img src=x onerror=f()", ""),
        ("Jane <img src=x onerror=f()", "Jane"),
        ("<b>Jane</b> <img src=x onerror=f()", "Jane"),
        ("&lt;img src=x onerror=f()", ""),
        ("<!-- hidden", ""),
        ("a < b", "a < b"),
        ("AT&T", "AT&T"),
        ("AT&T <b>x</b>", "AT&T x"),
    ],
)
def test_strip_markup(value, expected):
    assert strip_markup(value) == expected

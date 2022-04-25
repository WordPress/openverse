import pytest
from catalog.api.utils.help_text import make_comma_separated_help_text


@pytest.mark.parametrize(
    "items, expected",
    [
        ([], "A comma separated list of items; available items include: ."),
        (
            ["a"],
            "A comma separated list of items; available items include: `a`.",
        ),
        (
            ["a", "b"],
            "A comma separated list of items; "
            "available items include: `a`, and `b`.",
        ),
        (
            ["a", "b", "c"],
            "A comma separated list of items; "
            "available items include: `a`, `b`, and `c`.",
        ),
    ],
)
def test_make_help_text(items, expected):
    actual = make_comma_separated_help_text(items, "items")
    assert actual == expected

import pytest
from ov_attribution.attribution import get_attribution_text


BLANK = object()


@pytest.mark.parametrize(
    "blank_val",
    ["", None],  # Test blank arguments against both ``None`` and empty string.
)
@pytest.mark.parametrize(
    "args, attribution",
    [
        (
            ("by", "Title", "Creator", "0.0", "https://license/url"),  # All known
            '"Title" by Creator is licensed under CC BY 0.0. '
            "To view a copy of this license, visit https://license/url.",
        ),
        (
            ("by", BLANK, "Creator", "0.0", "https://license/url"),  # Unknown title
            "This work by Creator is licensed under CC BY 0.0. "
            "To view a copy of this license, visit https://license/url.",
        ),
        (
            ("by", "Title", BLANK, "0.0", "https://license/url"),  # Unknown creator
            '"Title" is licensed under CC BY 0.0. '
            "To view a copy of this license, visit https://license/url.",
        ),
        (
            ("by", "Title", "Creator", BLANK, "https://license/url"),  # Unknown version
            '"Title" by Creator is licensed under CC BY. '
            "To view a copy of this license, visit https://license/url.",
        ),
        (
            ("by", "Title", "Creator", "0.0", BLANK),  # Unknown license URL
            '"Title" by Creator is licensed under CC BY 0.0. '
            "To view a copy of this license, visit https://creativecommons.org/licenses/by/0.0/.",
        ),
        (
            ("by", "Title", "Creator", "0.0", False),  # Removed license URL
            '"Title" by Creator is licensed under CC BY 0.0.',
        ),
        (
            ("by", BLANK, BLANK, BLANK, BLANK),  # Almost all unknown
            "This work is licensed under CC BY. "
            "To view a copy of this license, visit https://creativecommons.org/licenses/by/4.0/.",
        ),
    ],
)
def test_attribution_text(
    blank_val: str | None,
    args: tuple[str, str, str, str, str],
    attribution: str,
):
    args = (blank_val if arg is BLANK else arg for arg in args)
    assert get_attribution_text(*args) == attribution


@pytest.mark.parametrize(
    "slug, attribution",
    [
        (
            "pdm",
            "This work is marked with Public Domain Mark 1.0. "
            "To view the terms, visit https://creativecommons.org/publicdomain/mark/1.0/.",
        ),
        (
            "cc0",
            "This work is marked with CC0 1.0. "
            "To view the terms, visit https://creativecommons.org/publicdomain/zero/1.0/.",
        ),
    ],
)
def test_attribution_text_differentiates_license_and_other_tools(
    slug: str,
    attribution: str,
):
    assert get_attribution_text(slug) == attribution

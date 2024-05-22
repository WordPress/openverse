import pytest
from openverse_attribution.license import License


BLANK = object()


# Test blank arguments against both ``None`` and empty string.
@pytest.mark.parametrize(
    "blank_val",
    [pytest.param("", id="blank"), pytest.param(None, id="none")],
)
@pytest.mark.parametrize(
    "args, attribution",
    [
        pytest.param(
            ("4.0", "Title", "Creator", "https://license/url"),
            '"Title" by Creator is licensed under CC BY 4.0. '
            "To view a copy of this license, visit https://license/url.",
            id="all_known",
        ),
        pytest.param(
            (None, "Title", "Creator", "https://license/url"),
            '"Title" by Creator is licensed under CC BY. '
            "To view a copy of this license, visit https://license/url.",
            id="unknown_version",
        ),
        pytest.param(
            ("4.0", BLANK, "Creator", "https://license/url"),
            "This work by Creator is licensed under CC BY 4.0. "
            "To view a copy of this license, visit https://license/url.",
            id="unknown_title",
        ),
        pytest.param(
            ("4.0", "Title", BLANK, "https://license/url"),
            '"Title" is licensed under CC BY 4.0. '
            "To view a copy of this license, visit https://license/url.",
            id="unknown_creator",
        ),
        pytest.param(
            ("4.0", "Title", "Creator", BLANK),
            '"Title" by Creator is licensed under CC BY 4.0. '
            "To view a copy of this license, visit https://creativecommons.org/licenses/by/4.0/.",
            id="unknown_license_url",
        ),
        pytest.param(
            ("4.0", "Title", "Creator", False),
            '"Title" by Creator is licensed under CC BY 4.0.',
            id="removed_license_url",
        ),
        pytest.param(
            (None, BLANK, BLANK, BLANK),
            "This work is licensed under CC BY. "
            "To view a copy of this license, visit https://creativecommons.org/licenses/by/4.0/.",
            id="almost_all_unknown",
        ),
    ],
)
def test_attribution_text(
    blank_val: str | None,
    args: tuple[str, str, str, str, str],
    attribution: str,
):
    args = [blank_val if arg is BLANK else arg for arg in args]
    lic = License("by", args[0])
    assert lic.get_attribution_text(*args[1:]) == attribution


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
    assert License(slug).get_attribution_text() == attribution

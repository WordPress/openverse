import re

import pytest

from catalog.api.utils.attribution import get_attribution_text


@pytest.mark.parametrize(
    "args, expectation",
    [
        (
            ("Title", "Creator", "xy", "0.0", "https://license/url"),
            '"Title" by Creator is licensed under CC XY 0.0. '
            "To view a copy of this license, visit https://license/url.",
        ),
        (
            ("", "Creator", "xy", "0.0", "https://license/url"),  # No title
            "This work by Creator is licensed under",
        ),
        (
            ("Title", "", "xy", "0.0", "https://license/url"),  # No creator
            '"Title" is licensed under CC XY 0.0.',
        ),
        (
            ("Title", "Creator", "xy", "0.0", ""),  # No URL
            r'^"Title" by Creator is licensed under CC XY 0.0.$',
        ),
        (
            ("Title", "Creator", "pdm", "0.0", "https://license/url"),  # PDM
            '"Title" by Creator is marked with Public Domain Mark 0.0.',
        ),
        (
            ("Title", "Creator", "cc0", "0.0", "https://license/url"),  # CC0
            '"Title" by Creator is marked with CC0 0.0.',
        ),
        (
            (None, None, "xy", None, None),
            "This work is licensed under CC XY.",  # almost nothing known about the work
        ),
    ],
)
def test_attribution_text(args: tuple[str, str, str, str, str], expectation: str):
    attribution = get_attribution_text(*args)
    assert re.match(expectation, attribution)

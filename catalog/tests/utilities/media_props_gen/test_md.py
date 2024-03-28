import pytest

from catalog.utilities.media_props_gen.md import Md


@pytest.mark.parametrize(
    "input_text,expected_output",
    [
        pytest.param(
            "# Title\n## Prop1\nContent1\n## Prop2\nContent2",
            {"Title": {"Prop1": "Content1", "Prop2": "Content2"}},
            id="Basic Functionality",
        ),
        pytest.param("", {}, id="Empty Input"),
        pytest.param("Just some text without headers.", {}, id="No Headers"),
        pytest.param("# Title", {}, id="Single Header Only"),
        pytest.param(
            "# Title\nJust some standalone content.\n# Title1\n## Prop1\nContent1",
            {"Title1": {"Prop1": "Content1"}},
            id="Missing Subheaders",
        ),
        pytest.param(
            "# Title\n## Prop\nLine 1\nLine 2",
            {"Title": {"Prop": "Line 1Line 2"}},
            id="Multiple Lines per Property",
        ),
        pytest.param(
            "# Title\n\n## Prop\nContent\n\n",
            {"Title": {"Prop": "Content"}},
            id="Whitespace Lines Are Ignored",
        ),
        pytest.param(
            "# Title \n## Prop \nContent ",
            {"Title": {"Prop": "Content"}},
            id="Trailing Whitespace in lines",
        ),
    ],
)
def test_parse(input_text, expected_output):
    assert Md.parse(input_text) == expected_output

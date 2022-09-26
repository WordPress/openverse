import pytest
from data_refresh.record_reporting import report_record_difference


@pytest.mark.parametrize(
    "before, after, expected_in_message",
    [
        ["1", "2", ["1 → 2", "+1 (+100.0%"]],
        ["1", "3", ["1 → 3", "+2 (+200.0%"]],
        ["4", "2", ["4 → 2", "-2 (-50.0%"]],
        ["4000", "2000", ["4,000 → 2,000", "-2,000 (-50.0%"]],
    ],
)
def test_record_reporting(before, after, expected_in_message):
    actual = report_record_difference(before, after, "media", "dag_id")
    assert isinstance(expected_in_message, list), (
        "Value for 'expected_in_message' should be a list, "
        "a string may give a false positive"
    )
    for expected in expected_in_message:
        assert expected in actual

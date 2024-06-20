import pytest

from legacy_data_refresh.reporting import (
    report_record_difference,
    report_status,
)


@pytest.mark.parametrize(
    "before, after, expected_in_message",
    [
        [
            {"src1": 1, "src2": 19},
            {"src1": 2, "src2": 38},
            ["20 → 40", "+20 (+100.000000%", "`src1`:+1", "`src2`:+19"],
        ],
        [
            {"src1": 1, "src2": 19},
            {"src1": 3, "src2": 57, "src3": 20},
            ["20 → 80", "+60 (+300.000000%", "`src1`:+2", "`src2`:+38", "`src3`:+20"],
        ],
        [
            {"src1": 4, "src2": 21},
            {"src1": 4},
            # Unchanged source count shouldn't show up
            ["25 → 4", "-21 (-84.000000%", "`src2`:-21"],
        ],
        [
            {"src1": 4000, "src2": 20},
            {"src1": 2000, "src2": 10},
            ["4,020 → 2,010", "-2,010 (-50.000000%", "`src1`:-2,000", "`src2`:-10"],
        ],
        [
            {},
            {"src1": 10, "src2": 10},
            ["0 → 20", "+20 (+inf%", "`src1`:+10", "`src2`:+10"],
        ],
        [
            {"src1": 10, "src2": 10},
            {},
            ["20 → 0", "-20 (-100.000000%", "`src1`:-10", "`src2`:-10"],
        ],
        [
            {"src1": 5000000000},
            {"src1": 4938271605},
            ["5,000,000,000 → 4,938,271,605", "-61,728,395 (-1.234568%"],
        ],
        [{"src1": 4}, {"src1": 4}, ["Sources not listed had no change in count"]],
        [{}, {}, ["Both indices missing? No breakdown to show"]],
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


def test_report_status():
    actual = report_status("image", "This is my message", "sample_dag_id")
    assert actual == "`image`: This is my message"

import pytest

from data_refresh.reporting import report_record_difference, report_status


@pytest.mark.parametrize(
    "before, after, expected_in_message",
    [
        [
            {"src1": 1, "src2": 19},
            {"src1": 2, "src2": 38},
            ["20 → 40", "+20 (+100.0%", "`src1`:+1", "`src2`:+19"],
        ],
        [
            {"src1": 1, "src2": 19},
            {"src1": 3, "src2": 57, "src3": 20},
            ["20 → 80", "+60 (+300.0%", "`src1`:+2", "`src2`:+38", "`src3`:+20"],
        ],
        [
            {"src1": 4, "src2": 21},
            {"src1": 4},
            ["25 → 4", "-21 (-84.0%", "`src1`:+0", "`src2`:-21"],
        ],
        [
            {"src1": 4000, "src2": 20},
            {"src1": 2000, "src2": 10},
            ["4,020 → 2,010", "-2,010 (-50.0%", "`src1`:-2,000", "`src2`:-10"],
        ],
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

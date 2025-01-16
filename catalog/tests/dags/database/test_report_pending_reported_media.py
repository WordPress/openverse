from unittest import mock

import pytest

from database.report_pending_reported_media import report_actionable_records


def _make_reported_records_data(media_type: str):
    return [
        (
            {"dmca": 1, "mature": 2, "other": 3},
            [
                f"{media_type}: 6",
                "_(1 dmca, 2 mature, 3 other)_",
            ],
        ),
        (
            {"dmca": 1, "mature": 2},
            [
                f"{media_type}: 3",
                "_(1 dmca, 2 mature)_",
            ],
        ),
        (
            {"other": 7},
            [
                f"{media_type}: 7",
                "_(7 other)_",
            ],
        ),
    ]


@pytest.mark.parametrize(
    "audio_counts, audio_expected_messages", _make_reported_records_data("audio")
)
@pytest.mark.parametrize(
    "image_counts, image_expected_messages", _make_reported_records_data("image")
)
def test_report_actionable_records(
    audio_counts, audio_expected_messages, image_counts, image_expected_messages
):
    with mock.patch("common.slack.send_alert") as send_alert_mock:
        report_counts_by_media_type = {"audio": audio_counts, "image": image_counts}
        report_actionable_records(report_counts_by_media_type)

        for message in audio_expected_messages + image_expected_messages:
            assert message in send_alert_mock.call_args.args[0], (
                "Completion message doesn't contain expected text"
            )


def test_report_actionable_records_no_data_message():
    with mock.patch("common.slack.send_message") as send_message_mock:
        report_counts_by_media_type = {"audio": {}, "image": {}}
        report_actionable_records(report_counts_by_media_type)

        assert (
            "No records require review at this time"
            in send_message_mock.call_args.args[0]
        )

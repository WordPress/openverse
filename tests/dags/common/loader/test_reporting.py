from unittest import mock

import pytest
from common.loader.reporting import (
    RecordMetrics,
    clean_duration,
    clean_record_counts,
    report_completion,
)


@pytest.fixture(autouse=True)
def send_message_mock() -> mock.MagicMock:
    with mock.patch("common.slack.SlackMessage.send") as SendMessageMock:
        yield SendMessageMock


@pytest.mark.parametrize(
    "should_send_message",
    [True, False],
)
def test_report_completion(should_send_message):
    with mock.patch(
        "common.slack.should_send_message", return_value=should_send_message
    ):
        report_completion(
            "Jamendo",
            [
                "audio",
            ],
            None,
            {"audio": RecordMetrics(100, 0, 0, 0)},
        )
        # Send message is only called if `should_send_message` is True.
        send_message_mock.called = should_send_message


def _make_report_completion_contents_data(media_type: str):
    return [
        # Happy path
        ({media_type: RecordMetrics(100, 0, 0, 0)}, f"  - `{media_type}`: 100"),
        # Missing columns detected
        (
            {media_type: RecordMetrics(90, 10, 0, 0)},
            f"  - `{media_type}`: 90 _(10 missing columns)_",
        ),
        # Foreign ID duplicates detected
        (
            {media_type: RecordMetrics(90, 0, 10, 0)},
            f"  - `{media_type}`: 90 _(10 duplicate foreign IDs)_",
        ),
        # URL duplicates detected
        (
            {media_type: RecordMetrics(90, 0, 0, 10)},
            f"  - `{media_type}`: 90 _(10 duplicate URLs)_",
        ),
        # Missing columns and foreign ID duplicates detected
        (
            {media_type: RecordMetrics(75, 10, 15, 0)},
            f"  - `{media_type}`: 75 _(10 missing columns, 15 duplicate foreign IDs)_",
        ),
        # Both duplicates detected, large numbers
        (
            {media_type: RecordMetrics(75_000, 0, 10_000, 15_000)},
            f"  - `{media_type}`: 75,000 _(10,000 duplicate foreign IDs, "
            f"15,000 duplicate URLs)_",
        ),
        # Cases with missing data
        (
            {media_type: RecordMetrics(None, None, None, None)},
            f"  - `{media_type}`: _No data_",
        ),
        (
            {media_type: RecordMetrics(100, None, None, None)},
            f"  - `{media_type}`: 100",
        ),
        (
            {media_type: RecordMetrics(None, 100, None, None)},
            f"  - `{media_type}`: _No data_",
        ),
        (
            {media_type: RecordMetrics(None, None, 100, None)},
            f"  - `{media_type}`: _No data_",
        ),
        (
            {media_type: RecordMetrics(None, None, None, 100)},
            f"  - `{media_type}`: _No data_",
        ),
        # Cases for when a load_to_s3 task skips due to a lack of records.
        # The task doesn't produce any XComs, so the RecordMetrics object is None.
        (
            {media_type: None},
            f"  - `{media_type}`: _No data_",
        ),
    ]


def _make_report_completion_contents_list_data(media_type: str):
    return [
        # List of RecordMetrics should be summed and handle Nones
        (
            [
                {media_type: RecordMetrics(100, 10, 10, 10)},
                {media_type: RecordMetrics(200, 20, 0, 0)},
                {media_type: None},
                {media_type: RecordMetrics(None, None, None, None)},
                {media_type: RecordMetrics(100, None, 100, 200)},
            ],
            f"  - `{media_type}`: 400 _(30 missing columns, 110 duplicate foreign"
            f" IDs, 210 duplicate URLs)_",
        ),
        # List of RecordMetrics that sum to no data
        (
            [
                {media_type: RecordMetrics(0, 0, 0, 0)},
                {media_type: None},
                {media_type: RecordMetrics(None, None, None, None)},
                {media_type: RecordMetrics(0, None, None, 0)},
                {media_type: RecordMetrics(None, 0, 0, 0)},
            ],
            f"  - `{media_type}`: _No data_",
        ),
    ]


# This sets up parameterizations for both audio and image simultaneously, in order
# to test that the statistics are reported accurately independent of each other.
@pytest.mark.parametrize(
    "audio_data, audio_expected", _make_report_completion_contents_data("audio")
)
@pytest.mark.parametrize(
    "image_data, image_expected", _make_report_completion_contents_data("image")
)
@pytest.mark.parametrize(
    "dated, date_range_start, date_range_end, expected_date_range",
    [
        # Not dated, no date range
        (False, None, None, "all"),
        # Not dated, but date range supplied
        (False, "2022-01-01", "2022-05-01", "all"),
        # Schedule interval and date range supplied
        (True, "2022-01-01", "2022-01-02", "2022-01-01 -> 2022-01-02"),
    ],
)
def test_report_completion_contents(
    audio_data,
    audio_expected,
    image_data,
    image_expected,
    dated,
    date_range_start,
    date_range_end,
    expected_date_range,
):
    with mock.patch("common.loader.reporting.send_message"):
        message = report_completion(
            "Jamendo",
            ["audio", "image"],
            None,
            {**audio_data, **image_data},
            dated,
            date_range_start,
            date_range_end,
        )
        for expected in [audio_expected, image_expected]:
            assert (
                expected in message
            ), "Completion message doesn't contain expected text"
        # Split message into "sections"
        parts = message.strip().split("\n")
        # Get the date section
        date_part = parts[1]
        assert expected_date_range in date_part


# This sets up parameterizations for both audio and image simultaneously, in order
# to test that the statistics are reported accurately independent of each other.
@pytest.mark.parametrize(
    "audio_data, audio_expected", _make_report_completion_contents_list_data("audio")
)
@pytest.mark.parametrize(
    "image_data, image_expected", _make_report_completion_contents_list_data("image")
)
@pytest.mark.parametrize(
    "dated, date_range_start, date_range_end, expected_date_range",
    [
        # Not dated, no date range
        (False, None, None, "all"),
        # Not dated, but date range supplied
        (False, "2022-01-01", "2022-05-01", "all"),
        # Schedule interval and date range supplied
        (True, "2022-01-01", "2022-01-02", "2022-01-01 -> 2022-01-02"),
    ],
)
def test_report_completion_contents_with_lists(
    audio_data,
    audio_expected,
    image_data,
    image_expected,
    dated,
    date_range_start,
    date_range_end,
    expected_date_range,
):
    with mock.patch("common.loader.reporting.send_message"):
        # Build record_counts_by_media_type
        record_counts_by_media_type = [
            {**audio, **image} for audio, image in zip(audio_data, image_data)
        ]

        message = report_completion(
            "Jamendo",
            ["audio", "image"],
            None,
            record_counts_by_media_type,
            dated,
            date_range_start,
            date_range_end,
        )

        for expected in [audio_expected, image_expected]:
            assert (
                expected in message
            ), "Completion message doesn't contain expected text"
        # Split message into "sections"
        parts = message.strip().split("\n")
        # Get the date section
        date_part = parts[1]
        assert expected_date_range in date_part


@pytest.mark.parametrize(
    "seconds, expected",
    [
        (0.1, "less than 1 sec"),
        (1, "1 sec"),
        (10, "10 secs"),
        (100, "1 min, 40 secs"),
        (1000, "16 mins, 40 secs"),
        (10000, "2 hours, 46 mins, 40 secs"),
        (100000, "1 day, 3 hours, 46 mins, 40 secs"),
        (1000000, "1 week, 4 days, 13 hours, 46 mins, 40 secs"),
        (10000000, "16 weeks, 3 days, 17 hours, 46 mins, 40 secs"),
        # Lists of durations
        ([0.1, 0.2, 0.1], "less than 1 sec"),
        ([0.2, 0.2, 0.6], "1 sec"),
        ([3, 7], "10 secs"),
        ([4, 6, 40, 50], "1 min, 40 secs"),
        ([150, 150, 300, 300, 100], "16 mins, 40 secs"),
        ([2000, 5000, 3000], "2 hours, 46 mins, 40 secs"),
    ],
)
def test_clean_time_duration(seconds, expected):
    actual = clean_duration(seconds)
    assert actual == expected


@pytest.mark.parametrize(
    "record_counts_by_media_type, media_types, expected",
    [
        # Single, one media type
        (
            {"image": RecordMetrics(1, 2, 3, 4)},
            [
                "image",
            ],
            {"image": RecordMetrics(1, 2, 3, 4)},
        ),
        # Single, multiple media types
        (
            {"image": RecordMetrics(1, 2, 3, 4), "audio": RecordMetrics(1, 2, 0, 0)},
            ["image", "audio"],
            {"image": RecordMetrics(1, 2, 3, 4), "audio": RecordMetrics(1, 2, 0, 0)},
        ),
        # Multiple
        (
            [
                {
                    "image": RecordMetrics(1, 2, 3, 4),
                    "audio": RecordMetrics(1, 2, 0, 0),
                },
                {"image": None, "audio": RecordMetrics(0, None, 0, 0)},
                {"image": RecordMetrics(0, 0, None, 0), "audio": None},
                {
                    "image": RecordMetrics(None, None, None, None),
                    "audio": RecordMetrics(1, 2, 0, 0),
                },
                {
                    "image": RecordMetrics(4, 3, 2, 1),
                    "audio": RecordMetrics(10, 1, 7, 2),
                },
            ],
            ["image", "audio"],
            {"image": RecordMetrics(5, 5, 5, 5), "audio": RecordMetrics(12, 5, 7, 2)},
        ),
    ],
)
def test_clean_record_counts(record_counts_by_media_type, media_types, expected):
    actual = clean_record_counts(record_counts_by_media_type, media_types)
    assert actual == expected

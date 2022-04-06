from unittest import mock

import pytest
from common.loader.reporting import humanize_time_duration, report_completion


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
        report_completion("Jamendo", None, {"audio": (100, 100, 100)})
        # Send message is only called if `should_send_message` is True.
        send_message_mock.called = should_send_message


def _make_report_completion_contents_data(media_type: str):
    return [
        # Happy path
        ({media_type: (100, 0, 100)}, f"  - `{media_type}`: 100"),
        # Cleaned detected
        ({media_type: (100, 10, 90)}, f"  - `{media_type}`: 90 _(10 cleaned)_"),
        # Duplicates detected
        ({media_type: (100, 0, 90)}, f"  - `{media_type}`: 90 _(10 duplicates)_"),
        # Cleaned and duplicates detected
        (
            {media_type: (100, 10, 75)},
            f"  - `{media_type}`: 75 _(10 cleaned, 15 duplicates)_",
        ),
        # Cleaned and duplicates, large numbers
        (
            {media_type: (100_000, 10_000, 75_000)},
            f"  - `{media_type}`: 75,000 _(10,000 cleaned, 15,000 duplicates)_",
        ),
        # Cases with missing data
        ({media_type: (None, None, None)}, f"  - `{media_type}`: _No data_"),
        ({media_type: (100, None, None)}, f"  - `{media_type}`: _No data_"),
        ({media_type: (None, 100, None)}, f"  - `{media_type}`: _No data_"),
        ({media_type: (None, None, 100)}, f"  - `{media_type}`: 100"),
    ]


# This sets up parameterizations for both audio and image simultaneously, in order
# to test that the statistics are reported accurately independent of each other.
@pytest.mark.parametrize(
    "audio_data, audio_expected", _make_report_completion_contents_data("audio")
)
@pytest.mark.parametrize(
    "image_data, image_expected", _make_report_completion_contents_data("image")
)
def test_report_completion_contents(
    audio_data, audio_expected, image_data, image_expected
):
    with mock.patch("common.loader.reporting.send_message") as send_message_mock:
        report_completion("Jamendo", None, {**audio_data, **image_data})
        for expected in [audio_expected, image_expected]:
            assert (
                expected in send_message_mock.call_args.args[0]
            ), "Completion message doesn't contain expected text"


@pytest.mark.parametrize(
    "seconds, expected",
    [
        (1, "1 sec"),
        (10, "10 secs"),
        (100, "1 min, 40 secs"),
        (1000, "16 mins, 40 secs"),
        (10000, "2 hours, 46 mins, 40 secs"),
        (100000, "1 day, 3 hours, 46 mins, 40 secs"),
        (1000000, "1 week, 4 days, 13 hours, 46 mins, 40 secs"),
        (10000000, "16 weeks, 3 days, 17 hours, 46 mins, 40 secs"),
    ],
)
def test_humanize_time_duration(seconds, expected):
    actual = humanize_time_duration(seconds)
    assert actual == expected

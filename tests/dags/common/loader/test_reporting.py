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
        report_completion("Jamendo", None, {"audio": 100})
        # Send message is only called if `should_send_message` is True.
        send_message_mock.called = should_send_message


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

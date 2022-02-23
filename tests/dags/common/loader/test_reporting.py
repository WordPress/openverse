from unittest import mock

import pytest
from common.loader.reporting import report_completion


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
        report_completion("Jamendo", "Audio", None, 100)
        # Send message is only called if `should_send_message` is True.
        send_message_mock.called = should_send_message

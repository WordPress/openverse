from unittest import mock

import pytest

from ingestion_server import slack


@pytest.mark.parametrize(
    "text, summary, expected_summary",
    [
        # Short text with default summary
        ("sample text", None, "sample text"),
        # Short text with explicit summary
        ("sample text", "different summary", "different summary"),
        # Multi-line text with default summary
        ("sample text\nLook a new line!", None, "Ingestion server message"),
        # Multi-line text with explicit summary
        ("sample text\nLook a new line!", "different summary", "different summary"),
    ],
)
@pytest.mark.parametrize(
    "webhook, should_alert",
    [
        # Actual webhook supplied
        ("http://fake", True),
        # No webhook supplied
        ("", False),
    ],
)
@pytest.mark.parametrize(
    "environment",
    [
        # Default environment
        None,
        # Different, explicit environment
        "staging",
    ],
)
def test_message(
    text,
    summary,
    webhook,
    should_alert,
    expected_summary,
    environment,
    monkeypatch,
):
    monkeypatch.setenv("ENVIRONMENT", environment)
    monkeypatch.setenv(slack.SLACK_WEBHOOK, webhook)
    with mock.patch("requests.post") as mock_post:
        slack.message(text, summary)
        assert mock_post.called == should_alert
        if not should_alert:
            return
        data = mock_post.call_args.kwargs["json"]
        assert data["blocks"][0]["text"]["text"] == text
        assert data["text"] == expected_summary
        if environment:
            assert data["username"].endswith(environment.upper())

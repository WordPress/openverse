from datetime import datetime
from unittest import mock

import pytest
from airflow.exceptions import AirflowNotFoundException

from common.slack import (
    SLACK_ALERTS_CONN_ID,
    SlackMessage,
    on_failure_callback,
    send_alert,
    send_message,
    should_send_message,
    should_silence_message,
)


_FAKE_IMAGE = "http://image.com/img.jpg"
p = pytest.param


@pytest.fixture(autouse=True)
def http_hook_mock() -> mock.MagicMock:
    with mock.patch("common.slack.HttpHook") as HttpHookMock:
        yield HttpHookMock.return_value


@pytest.mark.parametrize(
    "plain_text, expected",
    [
        (
            False,
            {"type": "mrkdwn", "text": "test message"},
        ),
        (
            True,
            {"type": "plain_text", "text": "test message"},
        ),
    ],
)
def test_text_section(plain_text, expected):
    actual = SlackMessage._text_block("test message", plain_text)
    assert actual == expected


@pytest.mark.parametrize(
    "url, title, alt_text, expected",
    [
        (
            _FAKE_IMAGE,
            None,
            None,
            {"type": "image", "image_url": _FAKE_IMAGE, "alt_text": "img.jpg"},
        ),
        (
            _FAKE_IMAGE,
            "Sample title",
            None,
            {
                "type": "image",
                "image_url": _FAKE_IMAGE,
                "title": {"type": "plain_text", "text": "Sample title"},
                "alt_text": "img.jpg",
            },
        ),
        (
            _FAKE_IMAGE,
            None,
            "Sample alternative text",
            {
                "type": "image",
                "image_url": _FAKE_IMAGE,
                "alt_text": "Sample alternative text",
            },
        ),
        (
            _FAKE_IMAGE,
            "Both title",
            "And alt text",
            {
                "type": "image",
                "image_url": _FAKE_IMAGE,
                "title": {"type": "plain_text", "text": "Both title"},
                "alt_text": "And alt text",
            },
        ),
    ],
)
def test_image_section(url, title, alt_text, expected):
    actual = SlackMessage._image_block(url, title, alt_text)
    assert actual == expected


def test_clear():
    s = SlackMessage()
    s.blocks = [{"text": "fake"}, {"text": "fake2"}]
    s._context = {"fake-context": "value"}
    s._payload = {"fake-payload": "value"}
    s.clear()
    assert s.blocks == []
    assert s._context == {}
    assert s._payload == s._base_payload


def test_payload_property():
    s = SlackMessage()
    s.blocks = [{"text": "fake"}, {"text": "fake2"}]
    assert s.payload == {
        "blocks": [{"text": "fake"}, {"text": "fake2"}],
        "icon_emoji": ":airflow:",
        "unfurl_links": True,
        "unfurl_media": True,
        "username": "Airflow",
    }


def test_add_context_no_initial_context():
    s = SlackMessage()
    assert s._context == {}
    s.add_context("Sample context")
    assert s._context == {
        "type": "context",
        "elements": [{"type": "mrkdwn", "text": "Sample context"}],
    }


def test_add_context_multiple():
    s = SlackMessage()
    s.add_context("Sample context")
    s.add_context("Additional context")
    assert s._context == {
        "type": "context",
        "elements": [
            {"type": "mrkdwn", "text": "Sample context"},
            {"type": "mrkdwn", "text": "Additional context"},
        ],
    }


def test_add_context_too_many():
    s = SlackMessage()
    with pytest.raises(
        ValueError, match="Unable to include more than 10 context elements"
    ):
        for idx in range(20):
            s.add_context(f"Sample context {idx}")


def test_add_context_image_no_initial_context():
    s = SlackMessage()
    assert s._context == {}
    s.add_context_image(_FAKE_IMAGE, alt_text="fake alt")
    assert s._context == {
        "type": "context",
        "elements": [
            {
                "alt_text": "fake alt",
                "image_url": "http://image.com/img.jpg",
                "type": "image",
            }
        ],
    }


def test_add_context_image_multiple():
    s = SlackMessage()
    s.add_context_image(_FAKE_IMAGE, alt_text="fake alt")
    s.add_context_image(_FAKE_IMAGE, alt_text="other alt")
    assert s._context == {
        "type": "context",
        "elements": [
            {
                "alt_text": "fake alt",
                "image_url": "http://image.com/img.jpg",
                "type": "image",
            },
            {
                "alt_text": "other alt",
                "image_url": "http://image.com/img.jpg",
                "type": "image",
            },
        ],
    }


def test_add_context_image_too_many():
    s = SlackMessage()
    with pytest.raises(
        ValueError, match="Unable to include more than 10 context elements"
    ):
        for idx in range(20):
            s.add_context_image(_FAKE_IMAGE, alt_text=f"Alt: {idx}")


def test_add_block():
    s = SlackMessage()
    s._add_block({"fake": "value"})
    assert s._context == {}
    assert s.blocks == [{"fake": "value"}]


def test_add_block_with_context():
    s = SlackMessage()
    s.add_context("Additional context")
    s._add_block({"fake": "value"})
    assert s._context == {}
    assert s.blocks == [
        {
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": "Additional context"}],
        },
        {"fake": "value"},
    ]


def test_add_divider():
    s = SlackMessage()
    s.add_divider()
    assert s.blocks == [{"type": "divider"}]


def test_add_text():
    s = SlackMessage()
    s.add_text("Fake message")
    assert s.blocks == [
        {"type": "section", "text": {"type": "mrkdwn", "text": "Fake message"}}
    ]


def test_add_image():
    s = SlackMessage()
    s.add_image(_FAKE_IMAGE)
    assert s.blocks == [
        {
            "type": "image",
            "image_url": "http://image.com/img.jpg",
            "alt_text": "img.jpg",
        }
    ]


def test_send_no_message():
    s = SlackMessage()
    with pytest.raises(ValueError, match="Nothing to send!"):
        s.send()


def test_send_no_context(http_hook_mock):
    s = SlackMessage()
    s.blocks = [1, 2, 3]
    s.send()
    http_hook_mock.run.assert_called_with(
        endpoint=None,
        data='{"username": "Airflow", "unfurl_links": true, "unfurl_media": true, '
        '"icon_emoji": ":airflow:", "blocks": [1, 2, 3], '
        '"text": "Airflow notification"}',
        headers={"Content-type": "application/json"},
        extra_options={"verify": True},
    )
    assert s._payload == s._base_payload


def test_send_with_context(http_hook_mock):
    s = SlackMessage()
    s.blocks = [1, 2, 3]
    s.add_context("Sample context")
    s.send()
    http_hook_mock.run.assert_called_with(
        endpoint=None,
        data='{"username": "Airflow", "unfurl_links": true, "unfurl_media": true, '
        '"icon_emoji": ":airflow:", "blocks": [1, 2, 3, {"type": "context", '
        '"elements": [{"type": "mrkdwn", "text": "Sample context"}]}], '
        '"text": "Airflow notification"}',
        headers={"Content-type": "application/json"},
        extra_options={"verify": True},
    )
    assert s._payload == s._base_payload


def test_send_fails(http_hook_mock):
    s = SlackMessage()
    error_message = "Some fake error"
    # Cause an exception within the raise_for_status call
    http_hook_mock.run.return_value.raise_for_status.side_effect = Exception(
        error_message
    )
    s.add_text("Sample message")
    with pytest.raises(Exception, match=error_message):
        s.send()


@pytest.mark.parametrize(
    "environment, slack_message_override, silenced_notifications, expected_result",
    [
        # non-production
        # Message is not sent by default. It is only sent if the override is enabled,
        # AND notifications are not silenced.
        # Default
        ("local", False, False, False),
        # Override is not enabled AND notifications are silenced
        ("local", False, True, False),
        # Override is enabled AND notifications NOT silenced
        ("local", True, False, True),
        # Override is enabled but notifications are silenced
        ("local", True, True, False),
        # Production
        # Message is sent by default; the override has no effect, but messages are
        # not sent when notifications are silenced.
        # Default
        ("production", False, False, True),
        # Override not enabled, notifications ARE silenced
        ("production", False, True, False),
        # Override enabled, notifications are NOT silenced
        ("production", True, False, True),
        # Override enabled, notifications ARE silenced
        ("production", True, True, False),
    ],
)
def test_should_send_message(
    environment, slack_message_override, silenced_notifications, expected_result
):
    with (
        mock.patch("common.slack.Variable") as MockVariable,
        mock.patch(
            "common.slack.should_silence_message", return_value=silenced_notifications
        ),
    ):
        # Mock the calls to Variable.get, in order
        MockVariable.get.side_effect = [
            environment,
            slack_message_override,
        ]
        assert should_send_message("text", "user", "mock_dag_id") == expected_result


def test_should_send_message_is_false_without_hook(http_hook_mock):
    http_hook_mock.get_conn.side_effect = AirflowNotFoundException("nope")
    assert not should_send_message("text", "user", "test_workflow")


@pytest.mark.parametrize(
    "silenced_notifications, should_silence",
    (
        # Do not silence when silenced_notifications is empty
        p({}, False, id="empty notifications"),
        # dag_id is not in silenced_notifications
        p(
            {
                "another_dag_id": [
                    {
                        "issue": "https://github.com/WordPress/openverse/issues/1",
                        "predicate": "KeyError",
                    }
                ]
            },
            False,
            id="wrong dag_id",
        ),
        # dag_id is configured, but text and username do not match
        p(
            {
                "test_dag_id": [
                    {
                        "issue": "https://github.com/WordPress/openverse/issues/1",
                        "predicate": "Unit codes",
                    }
                ]
            },
            False,
            id="unmatched predicate",
        ),
        # text matches
        p(
            {
                "test_dag_id": [
                    {
                        "issue": "https://github.com/WordPress/openverse/issues/1",
                        "predicate": "KeyError: 'image'",
                    }
                ]
            },
            True,
            id="matches predicate",
        ),
        # a substring of text matches
        p(
            {
                "test_dag_id": [
                    {
                        "issue": "https://github.com/WordPress/openverse/issues/1",
                        "predicate": "KeyError",
                    }
                ]
            },
            True,
            id="matches substring",
        ),
        # matches are case-insensitive
        p(
            {
                "test_dag_id": [
                    {
                        "issue": "https://github.com/WordPress/openverse/issues/1",
                        "predicate": "kEYErrOR",
                    }
                ]
            },
            True,
            id="matches case-insensitive",
        ),
        # username matches
        p(
            {
                "test_dag_id": [
                    {
                        "issue": "https://github.com/WordPress/openverse/issues/1",
                        "predicate": "Airflow DAG Failure",
                    }
                ]
            },
            True,
            id="matches message username",
        ),
        # Wrong task ID with pattern
        p(
            {
                "test_dag_id": [
                    {
                        "issue": "https://github.com/WordPress/openverse/issues/1",
                        "predicate": "KeyError",
                        "task_id_pattern": "totally_different",
                    }
                ]
            },
            False,
            id="wrong task_id",
        ),
        p(
            {
                "test_dag_id": [
                    {
                        "issue": "https://github.com/WordPress/openverse/issues/1",
                        "predicate": "Does not exist",
                        "task_id_pattern": "test_task_id_1",
                    }
                ]
            },
            False,
            id="matches task pattern but not predicate",
        ),
        p(
            {
                "test_dag_id": [
                    {
                        "issue": "https://github.com/WordPress/openverse/issues/1",
                        "predicate": "KeyError",
                        "task_id_pattern": "test_task_id_1",
                    }
                ]
            },
            True,
            id="matches task pattern and predicate",
        ),
        p(
            {
                "test_dag_id": [
                    {
                        "issue": "https://github.com/WordPress/openverse/issues/1",
                        "predicate": "KeyError",
                        "task_id_pattern": "task_id",
                    }
                ]
            },
            True,
            id="matches task pattern (substring) and predicate",
        ),
        p(
            {
                "test_dag_id": [
                    {
                        "issue": "https://github.com/WordPress/openverse/issues/1",
                        "predicate": "KeyError",
                        "task_id_pattern": "task_.*?_1",
                    }
                ]
            },
            True,
            id="matches task pattern (regex) and predicate",
        ),
    ),
)
def test_should_silence_message(silenced_notifications, should_silence):
    with mock.patch("common.slack.Variable") as MockVariable:
        MockVariable.get.side_effect = [silenced_notifications]
        assert (
            should_silence_message(
                "KeyError: 'image'",
                "Airflow DAG Failure",
                "test_dag_id",
                "test_task_id_1",
            )
            == should_silence
        )


@pytest.mark.parametrize("environment", ["local", "production"])
def test_send_message(environment, http_hook_mock):
    with mock.patch("common.slack.should_send_message", return_value=True), mock.patch(
        "common.slack.Variable"
    ) as MockVariable:
        MockVariable.get.side_effect = [environment]
        send_message("Sample text", dag_id="test_workflow", username="DifferentUser")
        http_hook_mock.run.assert_called_with(
            endpoint=None,
            data=f'{{"username": "DifferentUser | {environment}", "unfurl_links": false, "unfurl_media": false,'
            ' "icon_emoji": ":airflow:", "blocks": [{"type": "section", "text": '
            '{"type": "mrkdwn", "text": "Sample text"}}], "text": "Sample text"}',
            headers={"Content-type": "application/json"},
            extra_options={"verify": True},
        )


def test_send_message_does_not_send_if_checks_fail(http_hook_mock):
    with mock.patch("common.slack.should_send_message", return_value=False):
        send_message("Sample text", dag_id="test_workflow", username="DifferentUser")
        http_hook_mock.run.assert_not_called()


def test_send_alert():
    with mock.patch("common.slack.send_message") as send_message_mock:
        send_alert("Sample text", dag_id="test_workflow", username="DifferentUser")
        send_message_mock.assert_called_with(
            "Sample text",
            "test_workflow",
            "DifferentUser",
            ":airflow:",
            True,
            False,
            False,
            http_conn_id=SLACK_ALERTS_CONN_ID,
            task_id=None,
        )


@pytest.mark.parametrize(
    "exception, environment, slack_message_override, call_expected",
    [
        # Message with exception
        (ValueError("Whoops!"), "local", False, False),
        (ValueError("Whoops!"), "local", True, True),
        (ValueError("Whoops!"), "production", False, True),
        (ValueError("Whoops!"), "production", True, True),
        # Strings should also be allowed
        ("task marked as failed externally", "local", False, False),
        ("task marked as failed externally", "local", True, True),
        ("task marked as failed externally", "production", False, True),
        ("task marked as failed externally", "production", True, True),
        # Message without exception
        (None, "local", False, False),
        (None, "local", True, True),
        (None, "production", False, True),
        (None, "production", True, True),
        # Exception with upstream failure message should never run
        (ValueError("Upstream task(s) failed"), "local", False, False),
        (ValueError("Upstream task(s) failed"), "local", True, False),
        (ValueError("Upstream task(s) failed"), "production", False, False),
        (ValueError("Upstream task(s) failed"), "production", True, False),
    ],
)
def test_on_failure_callback(
    exception, environment, slack_message_override, call_expected, http_hook_mock
):
    context = {
        "task_instance": mock.Mock(),
        "logical_date": datetime.now(),
        "exception": exception,
        "dag": mock.Mock(),
    }
    env_vars = {
        "ENVIRONMENT": environment,
        "SLACK_MESSAGE_OVERRIDE": slack_message_override,
        "SILENCED_SLACK_NOTIFICATIONS": {},
    }

    # Mock env variables
    def environment_vars_mock(value, **kwargs):
        return env_vars[value]

    with mock.patch("common.slack.Variable") as MockVariable:
        run_mock = http_hook_mock.run
        MockVariable.get.side_effect = environment_vars_mock
        on_failure_callback(context)
        assert run_mock.called == call_expected
        if call_expected:
            # Check that an exception message is present only if one is provided
            assert bool(exception) ^ (
                "Exception" not in run_mock.call_args.kwargs["data"]
            )

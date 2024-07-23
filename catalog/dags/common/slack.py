"""
# Slack Block Message Builder

TODO:
    - track number of characters, raise error after 4k
    - attach text, fields

This class is intended to be used with a channel-specific slack webhook.
More information can be found here: <https://app.slack.com/block-kit-builder>.

## Messages are not configured to send in development

Messages or alerts sent using `send_message` or `on_failure_callback` will only
send if a Slack connection is defined and we are running in production. You can
manually override this for testing purposes by setting the `SLACK_MESSAGE_OVERRIDE`
variable to `true` in the Airflow UI.

## Send multiple messages - payload is reset after sending

>>> slack = SlackMessage(username="Multi-message Test")

>>> slack.add_text("message 1")
>>> slack.send()

>>> slack.add_text("message 2")
>>> slack.send()

## Embed images, plus context

>>> slack = SlackMessage(username="Blocks - Referenced Images")

>>> slack.add_context(":pika-love: context stuff *here*")

>>> msg = "Example message with new method of embedding images and divider below."

>>> slack.add_text(msg)
>>> slack.add_divider()
>>> slack.add_image(url1, title=img1_title, alt_text="img #1")
>>> slack.add_image(url2, title=img2_title, alt_text="img #2")
>>> slack.send()

## Dev Tools
>>> # prints current payload
>>> slack.display()

>>> # get payload dict
>>> payload = slack.payload

"""

import json
import logging
import re
from collections.abc import Callable
from os.path import basename
from typing import Any

from airflow.decorators import task
from airflow.exceptions import AirflowNotFoundException
from airflow.models import Variable
from airflow.providers.http.hooks.http import HttpHook
from requests import Response
from typing_extensions import NotRequired, TypedDict


SLACK_NOTIFICATIONS_CONN_ID = "slack_notifications"
SLACK_ALERTS_CONN_ID = "slack_alerts"
JsonDict = dict[str, Any]
log = logging.getLogger(__name__)


class SilencedSlackNotification(TypedDict):
    """
    Configuration for a silenced Slack notification.

    issue: A link to a GitHub issue which describes why the notification
           is silenced and tracks resolving the problem.
    predicate: Slack notifications whose text or username contain the
               predicate will be silenced. Matching is case-insensitive.
    task_id_pattern: A regex pattern that matches the task_id of the task
                     that triggered the notification. (Optional)
    """

    issue: str
    predicate: str
    task_id_pattern: NotRequired[str | None]


class SlackMessage:
    """Slack Block Message Builder"""

    def __init__(
        self,
        username: str = "Airflow",
        icon_emoji: str = ":airflow:",
        unfurl_links: bool = True,
        unfurl_media: bool = True,
        http_conn_id: str = SLACK_NOTIFICATIONS_CONN_ID,
    ):
        self.http = HttpHook(method="POST", http_conn_id=http_conn_id)
        self.blocks = []
        self._context = {}
        self._payload: dict[str, Any] = {
            "username": username,
            "unfurl_links": unfurl_links,
            "unfurl_media": unfurl_media,
        }

        if icon_emoji:
            self._payload["icon_emoji"] = icon_emoji

        self._base_payload = self._payload.copy()

    @staticmethod
    def _text_block(message: str, plain_text: bool) -> JsonDict:
        text_type = "plain_text" if plain_text else "mrkdwn"
        return {"type": text_type, "text": message}

    @staticmethod
    def _image_block(
        url: str, title: str | None = None, alt_text: str | None = None
    ) -> JsonDict:
        img = {"type": "image", "image_url": url}
        if title:
            img.update({"title": {"type": "plain_text", "text": title}})
        if alt_text:
            img["alt_text"] = alt_text
        else:
            img["alt_text"] = basename(url)
        return img

    def clear(self) -> None:
        """Clear all stored data to prime the instance for a new message."""
        self.blocks = []
        self._context = {}
        self._payload = self._base_payload.copy()

    def display(self) -> None:
        """Print current payload, intended for local development only."""
        if self._context:
            self._append_context()
        self._payload.update({"blocks": self.blocks})
        print(json.dumps(self._payload, indent=4))

    @property
    def payload(self) -> JsonDict:
        payload = self._payload.copy()
        payload.update({"blocks": self.blocks})
        return payload

    ####################################################################################
    # Context
    ####################################################################################

    def _append_context(self) -> None:
        self.blocks.append(self._context.copy())
        self._context = {}

    def _add_context(
        self, body_generator: Callable, main_text: str, **options: Any
    ) -> None:
        if not self._context:
            self._context = {"type": "context", "elements": []}
        body = body_generator(main_text, **options)
        if len(self._context["elements"]) < 10:
            self._context["elements"].append(body)
        else:
            raise ValueError("Unable to include more than 10 context elements")

    def add_context(self, message: str, plain_text: bool = False) -> None:
        """Display context above or below a text block."""
        self._add_context(
            self._text_block,
            message,
            plain_text=plain_text,
        )

    def add_context_image(self, url: str, alt_text: str | None = None) -> None:
        """Display context image inline within a text block."""
        self._add_context(self._image_block, url, alt_text=alt_text)

    ####################################################################################
    # Blocks
    ####################################################################################

    def _add_block(self, block: JsonDict) -> None:
        if self._context:
            self._append_context()
        self.blocks.append(block)

    def add_divider(self) -> None:
        """Add a divider between blocks."""
        self._add_block({"type": "divider"})

    def add_text(self, message: str, plain_text: bool = False) -> None:
        """Add a text block, using markdown or plain text."""
        text = self._text_block(message, plain_text)
        self._add_block({"type": "section", "text": text})

    def add_image(
        self, url, title: str | None = None, alt_text: str | None = None
    ) -> None:
        """Add an image block, with optional title and alt text."""
        self._add_block(self._image_block(url, title, alt_text))

    ####################################################################################
    # Send
    ####################################################################################

    def send(self, notification_text: str = "Airflow notification") -> Response:
        """
        Send message payload to the channel configured by the webhook.

        Any notification text provided will only show up as the content within
        the notification pushed to various devices.
        """
        if not self._context and not self.blocks:
            raise ValueError("Nothing to send!")

        if self._context:
            self._append_context()
        self._payload.update({"blocks": self.blocks})
        self._payload["text"] = notification_text

        response = self.http.run(
            endpoint=None,
            data=json.dumps(self._payload),
            headers={"Content-type": "application/json"},
            extra_options={"verify": True},
        )

        self.clear()
        response.raise_for_status()
        return response


def should_silence_message(
    text: str,
    username: str,
    dag_id: str,
    task_id: str | None = None,
):
    """
    Determine if a Slack message should be silenced.

    Checks the `SILENCED_SLACK_NOTIFICATIONS` Airflow variable to see if the message
    should be silenced for this DAG.
    """
    # Match on message text and username
    message = username + text

    # Get the configuration for silenced messages for this DAG
    silenced_notifications: list[SilencedSlackNotification] = Variable.get(
        "SILENCED_SLACK_NOTIFICATIONS", default_var={}, deserialize_json=True
    ).get(dag_id, [])

    if not bool(silenced_notifications):
        # No silenced notifications for this DAG, exit early
        return False
    matches = []
    for notification in silenced_notifications:
        # Check that the predicate matches whatever message was raised
        predicate_matches = notification["predicate"].lower() in message.lower()
        # Check that the task ID matches the predicate _if both were supplied_,
        # not all messages supply a task ID but all exception-based alerts do.
        pattern = notification.get("task_id_pattern")
        task_id_matches = (task_id is None or pattern is None) or (
            task_id and pattern and re.search(pattern, task_id)
        )
        matches.append(predicate_matches and task_id_matches)
    return any(matches)


def should_send_message(
    text: str,
    username: str,
    dag_id: str,
    http_conn_id: str = SLACK_NOTIFICATIONS_CONN_ID,
    task_id: str | None = None,
):
    """
    Determine if a Slack message should actually be sent.

    Returns True if:
      * A Slack connection is defined
      * The DAG is not configured to silence messages of this type
      * We are in the prod env OR the message override is set.
    """
    # Exit early if no slack connection exists
    hook = HttpHook(http_conn_id=http_conn_id)
    try:
        hook.get_conn()
    except AirflowNotFoundException:
        return False

    # Exit early if this DAG is configured to skip Slack messaging
    if should_silence_message(text, username, dag_id, task_id):
        log.info(f"Skipping silenced Slack notification for {dag_id}::{task_id}.")
        return False

    # Exit early if we aren't on production or if force alert is not set
    environment = Variable.get("ENVIRONMENT", default_var="local")
    force_message = Variable.get(
        "SLACK_MESSAGE_OVERRIDE", default_var=False, deserialize_json=True
    )

    # prevent circular import
    from common.constants import PRODUCTION

    if not (environment == PRODUCTION or force_message):
        log.info(
            f"Skipping Slack notification for {dag_id}:{task_id} in"
            f" `{environment}` environment. To send the notification, enable"
            " the `SLACK_MESSAGE_OVERRIDE` variable."
        )
        return False

    return True


def send_message(
    text: str,
    dag_id: str,
    username: str = "Airflow",
    icon_emoji: str = ":airflow:",
    markdown: bool = True,
    unfurl_links: bool = False,
    unfurl_media: bool = False,
    http_conn_id: str = SLACK_NOTIFICATIONS_CONN_ID,
    task_id: str | None = None,
) -> None:
    """Send a simple slack message, convenience message for short/simple messages."""
    log.info(text)
    if not should_send_message(
        text, username, dag_id, http_conn_id=http_conn_id, task_id=task_id
    ):
        return

    s = SlackMessage(
        username,
        icon_emoji,
        unfurl_links,
        unfurl_media,
        http_conn_id=http_conn_id,
    )
    s.add_text(text, plain_text=not markdown)
    s.send(text)


def send_alert(
    text: str,
    dag_id: str,
    username: str = "Airflow Alert",
    icon_emoji: str = ":airflow:",
    markdown: bool = True,
    unfurl_links: bool = False,
    unfurl_media: bool = False,
    task_id: str | None = None,
):
    """
    Send a slack alert.

    Wrapper for send_message that allows sending a message to the configured alerts
    channel instead of the default notification channel.
    """
    send_message(
        text,
        dag_id,
        username,
        icon_emoji,
        markdown,
        unfurl_links,
        unfurl_media,
        http_conn_id=SLACK_ALERTS_CONN_ID,
        task_id=task_id,
    )


def on_failure_callback(context: dict) -> None:
    """
    Send an alert out regarding a failure to Slack.

    Errors are only sent out in production and if a Slack connection is defined.
    """
    # Get relevant info
    ti = context["task_instance"]
    dag_id = ti.dag_id
    task_id = ti.task_id
    logical_date = context["logical_date"]
    exception: Exception | None = context.get("exception")
    exception_message = ""

    if exception:
        # Forgo the alert on upstream failures
        if (
            isinstance(exception, Exception)
            and "Upstream task(s) failed" in exception.args
        ):
            log.info("Forgoing Slack alert due to upstream failures")
            return
        exception_message = f"""
*Exception Type*: `{exception.__class__.__module__}.{exception.__class__.__name__}`
*Exception*: {exception}
"""

    message = f"""
*DAG*: `{dag_id}`
*Task*: `{task_id}`
*Logical Date*: {logical_date.strftime('%Y-%m-%dT%H:%M:%SZ')}
*Log*: <{ti.log_url}|View Logs>
{exception_message}
"""
    send_alert(
        message,
        dag_id=dag_id,
        task_id=task_id,
        username="Airflow DAG Failure",
    )


@task
def notify_slack(
    text: str,
    dag_id: str,
    username: str = "Airflow Notification",
    icon_emoji: str = ":airflow:",
) -> None:
    send_message(
        text,
        username=username,
        icon_emoji=icon_emoji,
        dag_id=dag_id,
    )

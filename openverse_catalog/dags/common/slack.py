"""
# Slack Block Message Builder

TODO:
    - track number of characters, raise error after 4k
    - attach text, fields

This class is intended to be used with a channel-specific slack webhook.
More information can be found here: https://app.slack.com/block-kit-builder.

## Messages are not configured to send in development

Messages or alerts sent using `send_message` or `on_failure_callback` will only
send if a Slack connection is defined and we are running in production. You can
manually override this for testing purposes by setting the `slack_message_override`
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
from os.path import basename
from typing import Any, Callable, Optional

from airflow.exceptions import AirflowNotFoundException
from airflow.models import Variable
from airflow.providers.http.hooks.http import HttpHook
from requests import Response


SLACK_NOTIFICATIONS_CONN_ID = "slack_notifications"
SLACK_ALERTS_CONN_ID = "slack_alerts"
JsonDict = dict[str, Any]
log = logging.getLogger(__name__)


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
        url: str, title: Optional[str] = None, alt_text: Optional[str] = None
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
        """Prints current payload, intended for local development only."""
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
        """Display context above or below a text block"""
        self._add_context(
            self._text_block,
            message,
            plain_text=plain_text,
        )

    def add_context_image(self, url: str, alt_text: Optional[str] = None) -> None:
        """Display context image inline within a text block"""
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
        self, url, title: Optional[str] = None, alt_text: Optional[str] = None
    ) -> None:
        """Add an image block, with optional title and alt text."""
        self._add_block(self._image_block(url, title, alt_text))

    ####################################################################################
    # Send
    ####################################################################################

    def send(self, notification_text: str = "Airflow notification") -> Response:
        """
        Sends message payload to the channel configured by the webhook.

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


def send_message(
    text: str,
    username: str = "Airflow",
    icon_emoji: str = ":airflow:",
    markdown: bool = True,
    unfurl_links: bool = True,
    unfurl_media: bool = True,
    http_conn_id: str = SLACK_NOTIFICATIONS_CONN_ID,
) -> None:
    """Send a simple slack message, convenience message for short/simple messages."""
    log.info(text)
    if not should_send_message(http_conn_id):
        return

    environment = Variable.get("environment", default_var="dev")
    s = SlackMessage(
        f"{username} | {environment}",
        icon_emoji,
        unfurl_links,
        unfurl_media,
        http_conn_id=http_conn_id,
    )
    s.add_text(text, plain_text=not markdown)
    s.send(text)


def should_send_message(http_conn_id=SLACK_NOTIFICATIONS_CONN_ID):
    """
    Returns true if a Slack connection is defined and we are in production (or
    the message override is set).
    """
    # Exit early if no slack connection exists
    hook = HttpHook(http_conn_id=http_conn_id)
    try:
        hook.get_conn()
    except AirflowNotFoundException:
        return False

    # Exit early if we aren't on production or if force alert is not set
    environment = Variable.get("environment", default_var="dev")
    force_message = Variable.get(
        "slack_message_override", default_var=False, deserialize_json=True
    )
    return environment == "prod" or force_message


def send_alert(
    text: str,
    dag_id: str | None = None,
    username: str = "Airflow Alert",
    icon_emoji: str = ":airflow:",
    markdown: bool = True,
    unfurl_links: bool = True,
    unfurl_media: bool = True,
):
    """
    Wrapper for send_message that allows sending a message to the configured alerts
    channel instead of the default notification channel.
    """

    known_failures = Variable.get(
        "silenced_slack_alerts", default_var={}, deserialize_json=True
    )
    if dag_id in known_failures:
        log.info(f"Skipping Slack alert for {dag_id}: {text}")
        return

    send_message(
        text,
        username,
        icon_emoji,
        markdown,
        unfurl_links,
        unfurl_media,
        http_conn_id=SLACK_ALERTS_CONN_ID,
    )


def on_failure_callback(context: dict) -> None:
    """
    Send an alert out regarding a failure to Slack.
    Errors are only sent out in production and if a Slack connection is defined.
    """
    # Get relevant info
    dag = context["dag"]
    ti = context["task_instance"]
    execution_date = context["execution_date"]
    exception: Optional[Exception] = context.get("exception")
    exception_message = ""

    if exception:
        # Forgo the alert on upstream failures
        if "Upstream task(s) failed" in exception.args:
            log.info("Forgoing Slack alert due to upstream failures")
            return
        exception_message = f"""
*Exception*: {exception}
*Exception Type*: `{exception.__class__.__module__}.{exception.__class__.__name__}`
"""

    message = f"""
*DAG*: `{ti.dag_id}`
*Task*: `{ti.task_id}`
*Execution Date*: {execution_date.strftime('%Y-%m-%dT%H:%M:%SZ')}
*Log*: {ti.log_url}
{exception_message}
"""
    send_alert(message, dag_id=dag.dag_id, username="Airflow DAG Failure")

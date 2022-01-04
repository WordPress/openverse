import logging
import os

import requests


log = logging.getLogger(__name__)
SLACK_WEBHOOK = "SLACK_WEBHOOK"


def message(text: str, summary: str = None) -> None:
    """
    Send a Slack message to a channel specified by a Slack webhook variable.

    A message is only sent if the SLACK_WEBHOOK environment variable is undefined.
    """
    if not (webhook := os.getenv(SLACK_WEBHOOK)):
        log.debug(
            f"{SLACK_WEBHOOK} variable not defined, skipping slack message: {text}"
        )
        return
    if not summary:
        if "\n" in text:
            summary = "Ingestion server message"
        else:
            summary = text

    data = {
        "blocks": [{"text": {"text": text, "type": "mrkdwn"}, "type": "section"}],
        "text": summary,
        "username": "Data Refresh Notification",
        "icon_emoji": "arrows_counterclockwise",
    }
    try:
        requests.post(webhook, json=data)
    except Exception as err:
        log.exception(f"Unable to issue slack message: {err}")
        pass

import logging
import os
from enum import Enum

import requests
from decouple import config


log = logging.getLogger(__name__)
SLACK_WEBHOOK = "SLACK_WEBHOOK"
LOG_LEVEL = "SLACK_LOG_LEVEL"


class Level(Enum):
    VERBOSE = 0
    INFO = 1
    ERROR = 2


def _message(text: str, summary: str = None, level: Level = Level.INFO) -> None:
    """
    Send a Slack message to a channel specified by a Slack webhook variable.

    A message is only sent if the SLACK_WEBHOOK environment variable is undefined,
    and the environment is configured to log at this level.
    """
    environment = config("ENVIRONMENT", default="local")

    if not (webhook := os.getenv(SLACK_WEBHOOK)):
        log.debug(
            f"{SLACK_WEBHOOK} variable not defined, skipping slack message: {text}"
        )
        return
    # If no log level is configured in the environment, log everything by default.
    os_level = Level[os.getenv(LOG_LEVEL, Level.VERBOSE.name)]
    if level.value < os_level.value:
        log.debug(
            f"Slack logging level for {environment} set to {os_level.name}, skipping \
            slack message with priority {level.name}: {text}"
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
        "username": f"Data Refresh Notification | {environment.upper()}",
        "icon_emoji": "arrows_counterclockwise",
        "unfurl_links": False,
        "unfurl_media": False,
    }
    try:
        requests.post(webhook, json=data)
    except Exception as err:
        log.exception(f"Unable to issue slack message: {err}")
        pass


def verbose(text: str, summary: str = None) -> None:
    _message(text, summary, level=Level.VERBOSE)


def info(text: str, summary: str = None) -> None:
    _message(text, summary, level=Level.INFO)


def error(text: str, summary: str = None) -> None:
    _message(text, summary, level=Level.ERROR)


def status(model: str, text: str) -> None:
    """
    Send a message regarding the status of the data refresh.

    Model is required an all messages get prepended with the model.
    """
    text = f"`{model}`: {text}"
    info(text, None)

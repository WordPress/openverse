"""
Utilities for scrubbing sensitive infrastructure values out of Sentry events.

``send_default_pii=False`` and Sentry's server-side scrubbing only cover known
PII fields by key. Infrastructure hostnames such as the database DNS name can
still reach Sentry as free text — inside breadcrumbs, span descriptions or
exception messages — where key-based scrubbing never sees them. This redacts
those known-sensitive values from an event before it leaves the process.

See https://github.com/WordPress/openverse/issues/670.
"""

from collections.abc import Callable, Iterable
from typing import Any


FILTERED = "[Filtered]"

# Hostnames that are not sensitive and are too broad to be worth redacting.
IGNORED_HOSTS = frozenset({"", "localhost", "127.0.0.1", "::1"})


def _redact(value: Any, secrets: list[str]) -> Any:
    if isinstance(value, str):
        for secret in secrets:
            value = value.replace(secret, FILTERED)
        return value
    if isinstance(value, dict):
        return {key: _redact(item, secrets) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact(item, secrets) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact(item, secrets) for item in value)
    return value


def make_sensitive_value_scrubber(hostnames: Iterable[str]) -> Callable:
    """
    Build a Sentry ``before_send`` / ``before_send_transaction`` hook that
    replaces the given hostnames wherever they appear, as substrings, anywhere
    in the event.

    Longer hostnames are redacted first so that a host which is a substring of
    another (e.g. ``db.example.com`` inside ``replica.db.example.com``) does not
    leave a partial value behind.
    """
    secrets = sorted(
        {host for host in hostnames if host not in IGNORED_HOSTS},
        key=len,
        reverse=True,
    )

    def before_send(event: Any, hint: Any = None) -> Any:
        if not secrets:
            return event
        return _redact(event, secrets)

    return before_send

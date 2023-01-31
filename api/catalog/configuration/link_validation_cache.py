import json
import logging
import os
from collections import defaultdict
from datetime import timedelta

from django.core.exceptions import ImproperlyConfigured

from decouple import config


logger = logging.getLogger(__name__)


class LinkValidationCacheExpiryConfiguration(defaultdict):
    """Link validation cache expiry configuration."""

    SETTING_PREFIX = "LINK_VALIDATION_CACHE_EXPIRY__"

    # Cache successful links for a month, and broken links for 120 days.
    OVERALL_DEFAULT = {"days": 120}
    STATUS_DEFAULTS = {
        200: {"days": 30},
        -1: {"minutes": 30},
    }

    def __init__(self):
        default = self._config("default", default=self.OVERALL_DEFAULT)
        super().__init__(lambda: default)

        self.update(
            {k: self._config(k, default=v) for k, v in self.STATUS_DEFAULTS.items()}
        )

        for k, v in os.environ.items():
            if not k.startswith(self.SETTING_PREFIX) or k.lower().endswith("default"):
                continue

            try:
                status = int(k.replace(self.SETTING_PREFIX, ""))
            except ValueError:
                raise ImproperlyConfigured(
                    "Invalid link validation cache setting name: "
                    f"{self.SETTING_PREFIX}. Please ensure settings "
                    "are named in the format of "
                    f"'{self.SETTING_PREFIX}<http integer status code>'."
                )

            value = self._config(status)

            self[status] = value

    def _config(self, key: str | int, default: dict | None = None) -> int | None:
        try:
            v = config(
                f"{self.SETTING_PREFIX}{str(key)}",
                default=default,
                # Value should either be a str or dict here
                cast=lambda x: json.loads(x) if isinstance(x, str) else x,
            )
            return int(timedelta(**v).total_seconds())
        except (json.JSONDecodeError, TypeError):
            raise ImproperlyConfigured(
                f"Invalid link validation cache setting. Impossible to parse {key}."
            )

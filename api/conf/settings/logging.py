from logging import LogRecord

from decouple import config

from conf.settings.base import INSTALLED_APPS, MIDDLEWARE
from conf.settings.security import DEBUG


def health_check_filter(record: LogRecord) -> bool:
    # Filter out health checks from the logs, they're verbose and happen frequently
    return not ("GET /healthcheck" in record.getMessage() and record.status_code == 200)


# https://django-structlog.readthedocs.io/en/latest/getting_started.html#installation
if "django_structlog" not in INSTALLED_APPS:
    INSTALLED_APPS.append("django_structlog")

MIDDLEWARE.insert(0, "django_structlog.middlewares.RequestMiddleware")

LOG_LEVEL = config("LOG_LEVEL", default="INFO").upper()
DJANGO_DB_LOGGING = config("DJANGO_DB_LOGGING", cast=bool, default=False)

# Set to a pipe-delimited string of gc debugging flags
# https://docs.python.org/3/library/gc.html#gc.DEBUG_STATS
GC_DEBUG_LOGGING = config(
    "GC_DEBUG_LOGGING", cast=lambda x: x.split("|") if x else [], default=""
)

# https://github.com/dabapps/django-log-request-id#logging-all-requests
LOG_REQUESTS = True

# https://github.com/dabapps/django-log-request-id
MIDDLEWARE.insert(0, "log_request_id.middleware.RequestIDMiddleware")

# Logging configuration
LOGGING = {
    # NOTE: Most of this is inherited from the default configuration
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_id": {"()": "log_request_id.filters.RequestIDFilter"},
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
        "health_check": {
            "()": "django.utils.log.CallbackFilter",
            "callback": health_check_filter,
        },
    },
    "formatters": {
        "console": {
            "format": "[%(asctime)s - %(name)s - %(lineno)3d][%(levelname)s] [%(request_id)s] %(message)s",  # noqa: E501
        },
    },
    "handlers": {
        # Default console logger
        "console": {
            "level": LOG_LEVEL,
            "filters": ["request_id"],
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            # Keep this at info to avoid django internal debug logs;
            # we just want our own debug logs when log level is set to debug
            "level": "INFO",
            "propagate": False,
        },
        # Default handler for all other loggers
        "": {
            "handlers": ["console"],
            "filters": ["request_id"],
            "level": LOG_LEVEL,
        },
    },
}

if DJANGO_DB_LOGGING:
    # Behind a separate flag as it's a very noisy debug logger
    # and it's nice to be able to enable it conditionally within that context
    LOGGING["loggers"]["django.db.backends"] = {
        "level": "DEBUG",
        "handlers": ["console"],
        "propagate": False,
    }

    if not DEBUG:
        # WARNING: Do not run in production long-term as it can impact performance.
        middleware = (
            "api.middleware.force_debug_cursor_middleware.force_debug_cursor_middleware"
        )
        if middleware not in MIDDLEWARE:
            MIDDLEWARE.append(middleware)

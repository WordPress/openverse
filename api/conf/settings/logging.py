import logging
from logging import LogRecord

import structlog
from decouple import config
from structlog_sentry import SentryProcessor

from conf.settings.base import ENVIRONMENT, INSTALLED_APPS, MIDDLEWARE
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
LOG_PROCESSOR = config(
    "LOG_PROCESSOR",
    default="console" if ENVIRONMENT == "local" else "json",
)

# Set to a pipe-delimited string of gc debugging flags
# https://docs.python.org/3/library/gc.html#gc.DEBUG_STATS
GC_DEBUG_LOGGING = config(
    "GC_DEBUG_LOGGING", cast=lambda x: x.split("|") if x else [], default=""
)

# This shared_processors approach is modified from structlog's
# documentation for how to handle non-structured logs in a structured format
# https://www.structlog.org/en/stable/standard-library.html#rendering-using-structlog-based-formatters-within-logging
timestamper = structlog.processors.TimeStamper(fmt="iso")

shared_processors = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.CallsiteParameterAdder(
        {
            structlog.processors.CallsiteParameter.FILENAME,
            structlog.processors.CallsiteParameter.FUNC_NAME,
            structlog.processors.CallsiteParameter.LINENO,
        }
    ),
    structlog.processors.StackInfoRenderer(),
    # https://github.com/kiwicom/structlog-sentry - for Sentry integration
    # Must go after `add_logger_name` and `add_log_level`,
    # but before `format_exc_info`
    SentryProcessor(
        event_level=logging.ERROR,
        # `level` here dictates which log levels will be included in breadcrumbs
        # Set to WARNING for now to prevent PII/sensitive info from appearing there
        level=logging.WARNING,
        # Also ignore any Django SQL logs entirely in case they get enabled
        ignore_loggers=["django.db.backends"],
    ),
    structlog.processors.format_exc_info,
    structlog.processors.UnicodeDecoder(),
]


# These loggers duplicate django-structlog's request start/finish
# logs, as well as our nginx request logs. We want to keep only the
# start/finish logs and the nginx logs for access logging, otherwise
# we are just duplicating information!
_UNWANTED_LOGGERS = {
    "uvicorn.access",
    "django.request",
}


def suppress_unwanted_logs(record: LogRecord) -> bool:
    return (
        record.name not in _UNWANTED_LOGGERS
        and "GET /healthcheck" not in record.getMessage()
    )


# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "suppress_unwanted_logs": {
            "()": "django.utils.log.CallbackFilter",
            "callback": suppress_unwanted_logs,
        },
    },
    "formatters": {
        "structured": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": (
                structlog.processors.JSONRenderer()
                if LOG_PROCESSOR == "json"
                else structlog.dev.ConsoleRenderer()
            ),
            "foreign_pre_chain": [
                timestamper,
                # Explanations from https://www.structlog.org/en/stable/standard-library.html#rendering-using-structlog-based-formatters-within-logging
                # Add the log level and a timestamp to the event_dict if the log entry
                # is not from structlog.
                structlog.stdlib.add_log_level,
                # Add extra attributes of LogRecord objects to the event dictionary
                # so that values passed in the extra parameter of log methods pass
                # through to log output.
                structlog.stdlib.ExtraAdder(),
            ]
            + shared_processors,
        },
    },
    "handlers": {
        "console_structured": {
            "level": LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "structured",
            "filters": ["suppress_unwanted_logs"],
        },
    },
    "root": {
        "handlers": ["console_structured"],
        "level": LOG_LEVEL,
        "propagate": False,
    },
    "loggers": {
        "django": {
            "handlers": ["console_structured"],
            # Keep this at info to avoid django internal debug logs;
            # we just want our own debug logs when log level is set to debug
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn": {
            "handlers": ["console_structured"],
            "level": LOG_LEVEL,
        },
    },
}

# https://django-structlog.readthedocs.io/en/latest/getting_started.html
structlog.configure(
    processors=[
        timestamper,
        structlog.stdlib.filter_by_level,
    ]
    + shared_processors
    + [
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=(ENVIRONMENT == "production"),
)

if DJANGO_DB_LOGGING:
    # Behind a separate flag as it's a very noisy debug logger
    # and it's nice to be able to enable it conditionally within that context
    LOGGING["loggers"]["django.db.backends"] = {
        "level": "DEBUG",
        "handlers": ["console_structured"],
        "propagate": False,
    }

    if not DEBUG:
        # WARNING: Do not run in production long-term as it can impact performance.
        middleware = (
            "api.middleware.force_debug_cursor_middleware.force_debug_cursor_middleware"
        )
        if middleware not in MIDDLEWARE:
            MIDDLEWARE.append(middleware)

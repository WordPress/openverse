from logging import LogRecord

import structlog
from decouple import config

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

# Set to a pipe-delimited string of gc debugging flags
# https://docs.python.org/3/library/gc.html#gc.DEBUG_STATS
GC_DEBUG_LOGGING = config(
    "GC_DEBUG_LOGGING", cast=lambda x: x.split("|") if x else [], default=""
)

# Logging configuration
LOGGING = {
    # NOTE: Most of this is inherited from the default configuration
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
        "health_check": {
            "()": "django.utils.log.CallbackFilter",
            "callback": health_check_filter,
        },
    },
    "formatters": {
        "console": {
            "format": "[%(asctime)s - %(name)s - %(lineno)3d][%(levelname)s] %(message)s",  # noqa: E501
        },
        "json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
        },
    },
    "handlers": {
        # Default console logger
        "console": {
            "level": LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
        "console_json": {
            "level": LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "loggers": {
        # Application
        "django_structlog": {
            "handlers": ["console_json"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "api": {
            "handlers": ["console_json"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        # External
        "django": {
            "handlers": ["console"],
            # Keep this at info to avoid django internal debug logs;
            # we just want our own debug logs when log level is set to debug
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {  # Using just "uvicorn" will re-enable access logs
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        # Default handler for all other loggers
        "": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
        },
    },
}

# https://django-structlog.readthedocs.io/en/latest/getting_started.html
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
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
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
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

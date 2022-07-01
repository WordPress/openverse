from logging import LogRecord


def health_check_filter(record: LogRecord) -> bool:
    # Filter out health checks from the logs, they're verbose and happen frequently
    return not ("GET /healthcheck" in record.getMessage() and record.status_code == 200)


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
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] {message}",
            "style": "{",
        },
        "console": {
            "format": "[%(asctime)s - %(name)s - %(lineno)3d][%(levelname)s] [%(request_id)s] %(message)s",  # noqa: E501
        },
    },
    "handlers": {
        # Default console logger
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true", "request_id"],
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
        # Add a clause to log error messages to the console in production
        "console_prod": {
            "level": "WARNING",
            "filters": ["require_debug_false", "request_id"],
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
        # Handler for all other logging
        "general_console": {
            "level": "INFO",
            "filters": ["request_id"],
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
        # Default server logger
        "django.server": {
            "level": "INFO",
            "filters": ["request_id"],
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        # Default mailing logger
        "mail_admins": {
            "level": "ERROR",
            "filters": ["request_id", "require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "console_prod", "mail_admins"],
            "level": "INFO",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["django.server"],
            # Filter health check logs
            "filters": ["health_check", "request_id"],
            "level": "INFO",
            "propagate": False,
        },
        # Default handler for all other loggers
        "": {
            "handlers": ["general_console"],
            "filters": ["request_id"],
            "level": "INFO",
        },
    },
}

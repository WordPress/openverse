bind = ["0.0.0.0:8001"]
capture_output = True
accesslog = "-"
errorlog = "-"
chdir = "./ingestion_server/"
timeout = 120
reload = True
logconfig_dict = {
    # NOTE: Most of this is inherited from the default configuration
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "generic": {
            "format": "[%(asctime)s - %(name)s - %(lineno)3d][%(levelname)s] %(message)s",  # noqa: E501
        },
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "gunicorn.error": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,  # Prevents default handler from also logging this
            "qualname": "gunicorn.error",
        },
        "gunicorn.access": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,  # Prevents default handler from also logging this
            "qualname": "gunicorn.access",
        },
        "": {
            "level": "INFO",
            "handlers": ["console"],
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": "ext://sys.stdout",
        },
    },
}
loglevel = "debug"
wsgi_app = "api:api"

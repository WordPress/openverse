import logging
import os


def configure_logger():
    """
    Configures the logging module to
    - change the log level names to lowercase
    - set the formatter that works with GitHub logging commands
    - set the default log level to LOGGING_LEVEL environment variable
    """

    logging.addLevelName(logging.CRITICAL, "critical")
    logging.addLevelName(logging.ERROR, "error")
    logging.addLevelName(logging.WARNING, "warning")
    logging.addLevelName(logging.INFO, "info")
    logging.addLevelName(logging.DEBUG, "debug")

    logging.basicConfig(
        format="::%(levelname)s::[%(name)s] %(message)s",
        level=int(os.getenv("LOGGING_LEVEL", logging.DEBUG)),
    )

#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import asyncio
import os
import sys

import uvloop


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def main():
    """Run administrative tasks."""

    # This line should not be needed, because the environment variable is
    # already being set in other places, e.g.
    #
    # - the Docker container (using ``.env.docker``)
    # - Pipenv shell (using ``.env``).
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

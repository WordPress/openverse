"""
WSGI config for the Openverse API.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

import django

from conf.wsgi_handler import OpenverseWSGIHandler


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")


def get_wsgi_application():
    django.setup(set_prefix=False)
    return OpenverseWSGIHandler()


application = get_wsgi_application()

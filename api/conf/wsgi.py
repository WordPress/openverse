"""
WSGI config for the Openverse API.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

from gevent import monkey


monkey.patch_all()


import os

from django.core.wsgi import get_wsgi_application

from wsgi_basic_auth import BasicAuth


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")

application = BasicAuth(get_wsgi_application())

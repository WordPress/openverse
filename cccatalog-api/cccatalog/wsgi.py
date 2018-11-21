"""
WSGI config for cccatalog project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from wsgi_basic_auth import BasicAuth

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cccatalog.settings")

from gevent import monkey
monkey.patch_all()
application = get_wsgi_application()
application = BasicAuth(application)

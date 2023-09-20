"""
WSGI config for the Openverse API.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os


if os.getenv("ENABLE_TRACE_VIEW", "0") == "1":
    TRACING = True
    import tracemalloc

    tracemalloc.start()
else:
    TRACING = False

from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")

application = get_wsgi_application()

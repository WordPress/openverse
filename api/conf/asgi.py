import os

import django
from django.conf import settings
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler

from conf.asgi_handler import OpenverseASGIHandler


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")


def get_asgi_application():
    django.setup(set_prefix=False)
    return OpenverseASGIHandler()


application = get_asgi_application()


if settings.ENVIRONMENT == "local":
    static_files_application = ASGIStaticFilesHandler(application)

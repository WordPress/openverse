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


if settings.GC_DEBUG_LOGGING:
    import gc

    flags = []
    for flag_name in settings.GC_DEBUG_LOGGING:
        flags.append(getattr(gc, flag_name))

    setting = flags[0]
    for flag in flags[1:]:
        setting |= flag

    gc.set_debug(setting)

import os

from django.conf import settings
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler

from django_asgi_lifespan.asgi import get_asgi_application

from conf.malloc_trim import start_malloc_trim


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")


application = get_asgi_application()


if settings.ENVIRONMENT == "local":
    application = ASGIStaticFilesHandler(application)


if settings.GC_DEBUG_LOGGING:
    import gc

    setting = 0
    for flag in settings.GC_DEBUG_LOGGING:
        setting |= getattr(gc, flag)

    gc.set_debug(setting)


start_malloc_trim(settings.MALLOC_TRIM_INTERVAL_SECONDS)

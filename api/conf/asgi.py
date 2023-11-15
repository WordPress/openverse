import os

import django
from django.conf import settings
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler

from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from conf.asgi_handler import OpenverseASGIHandler


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")


def get_asgi_application():
    django.setup(set_prefix=False)
    return OpenverseASGIHandler()


# Give the base application a unique name so that it's easily referenced
# by other modules without needing to juggle through any of the various
# middlewares.
# For example, `ASGIStaticFileHandler` saves the application as
# `self.application`. However, `SentryAsgiMiddleware` saves it as `self.app`.
# If we relied on just referencing the pseudo-standard `application` exported
# in this module, we'd have to choose how to resolve the base application
# with the lifecycle handlers depending on what middleware was applied.
# Instead, we can just take advantage of the fact that these middleware
# all treat the passed-in application object as a singleton, so we're safe
# to directly reference `OPENVERSE_APPLICATION`, knowing that any middleware
# applied to it will be referencing the same application object in the end.
OPENVERSE_APPLICATION = get_asgi_application()

application = SentryAsgiMiddleware(OPENVERSE_APPLICATION)

if settings.ENVIRONMENT == "local":
    static_files_application = ASGIStaticFilesHandler(application)

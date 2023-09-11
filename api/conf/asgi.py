import os

import django

from conf.asgi_handler import OpenverseASGIHandler


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")


def get_asgi_application():
    django.setup(set_prefix=False)
    return OpenverseASGIHandler()


application = get_asgi_application()

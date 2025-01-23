from conf.settings.base import INSTALLED_APPS


if "api" not in INSTALLED_APPS:
    INSTALLED_APPS.append("api")

if "open_api" not in INSTALLED_APPS:
    INSTALLED_APPS.append("open_api")

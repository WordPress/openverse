from decouple import config

from conf.settings.base import INSTALLED_APPS, MIDDLEWARE


if "oauth2_provider" not in INSTALLED_APPS:
    INSTALLED_APPS.append("oauth2_provider")

middleware = "oauth2_provider.middleware.OAuth2TokenMiddleware"
if middleware not in MIDDLEWARE:
    MIDDLEWARE.append(middleware)

OAUTH2_PROVIDER = {
    "SCOPES": {
        "read": "Read scope",
        "write": "Write scope",
    },
    "ACCESS_TOKEN_EXPIRE_SECONDS": config(
        "ACCESS_TOKEN_EXPIRE_SECONDS",
        default=12 * 60 * 60,  # 12 hours
        cast=int,
    ),
}

OAUTH2_PROVIDER_APPLICATION_MODEL = "api.ThrottledApplication"

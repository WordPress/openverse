from decouple import config


OAUTH2_PROVIDER = {
    "SCOPES": {
        "read": "Read scope",
        "write": "Write scope",
    },
    "ACCESS_TOKEN_EXPIRE_SECONDS": config(
        "ACCESS_TOKEN_EXPIRE_SECONDS", default=3600 * 12, cast=int
    ),
}

OAUTH2_PROVIDER_APPLICATION_MODEL = "api.ThrottledApplication"

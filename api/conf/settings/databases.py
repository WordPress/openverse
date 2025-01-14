from decouple import config


# Database
# https://docs.djangoproject.com/en/stable/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": config("DJANGO_DATABASE_HOST", default="localhost"),
        "PORT": config("DJANGO_DATABASE_PORT", default=5432, cast=int),
        "USER": config("DJANGO_DATABASE_USER", default="deploy"),
        "PASSWORD": config("DJANGO_DATABASE_PASSWORD", default="deploy"),
        "NAME": config("DJANGO_DATABASE_NAME", default="openledger"),
        "CONN_HEALTH_CHECKS": config(
            "DJANGO_CONN_HEALTH_CHECKS", default=True, cast=bool
        ),
        "OPTIONS": {
            "application_name": config(
                "DJANGO_DATABASE_APPLICATION_NAME", default="openverse-api"
            ),
            "pool": True,
        },
    }
}

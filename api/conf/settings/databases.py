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
            # Every request holds its pooled connection for its whole lifetime,
            # including slow outbound calls (ES, dead-link checks, thumbnails),
            # so the pool must be sized for request concurrency rather than
            # DB concurrency. psycopg's defaults (max_size = min_size = 4,
            # 30 s wait, unbounded queue) stalled entire tasks, health check
            # included, whenever ES slowed down.
            "pool": {
                "min_size": config(
                    "DJANGO_DATABASE_POOL_MIN_SIZE", default=4, cast=int
                ),
                "max_size": config(
                    "DJANGO_DATABASE_POOL_MAX_SIZE", default=32, cast=int
                ),
                "timeout": config(
                    "DJANGO_DATABASE_POOL_TIMEOUT", default=10, cast=float
                ),
            },
        },
    }
}

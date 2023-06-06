from decouple import config


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": config("DJANGO_DATABASE_HOST", default="localhost"),
        "PORT": config("DJANGO_DATABASE_PORT", default=5432, cast=int),
        "USER": config("DJANGO_DATABASE_USER", default="deploy"),
        "PASSWORD": config("DJANGO_DATABASE_PASSWORD", default="deploy"),
        "NAME": config("DJANGO_DATABASE_NAME", default="openledger"),
        "OPTIONS": {
            "application_name": config(
                "DJANGO_DATABASE_APPLICATION_NAME", default="openverse-api"
            ),
        },
    }
}

# Caches

REDIS_HOST = config("REDIS_HOST", default="localhost")
REDIS_PORT = config("REDIS_PORT", default=6379, cast=int)
REDIS_PASSWORD = config("REDIS_PASSWORD", default="")


def _make_cache_config(dbnum: int, **overrides) -> dict:
    return {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{dbnum}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
        | overrides.pop("OPTIONS", {}),
    } | overrides


CACHES = {
    # Site cache writes to 'default'
    "default": _make_cache_config(0),
    # For rapidly changing stats that we don't want to hammer the database with
    "traffic_stats": _make_cache_config(1),
    # For ensuring consistency among multiple Django workers and servers.
    # Used by Redlock.
    "locks": _make_cache_config(2),
    # Used for tracking tallied figures that shouldn't expire and are indexed
    # with a timestamp range (for example, the key could a timestamp valid
    # for a given week), allowing historical data analysis.
    "tallies": _make_cache_config(3, TIMEOUT=None),
}

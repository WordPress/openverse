from decouple import config


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
    # Used for tracking tallied figures that shouldn't expire and are indexed
    # with a timestamp range (for example, the key could a timestamp valid
    # for a given week), allowing historical data analysis.
    "tallies": _make_cache_config(3, TIMEOUT=None),
}

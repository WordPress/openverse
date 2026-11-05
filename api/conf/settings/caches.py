from decouple import config


# Caches

REDIS_HOST = config("REDIS_HOST", default="localhost")
REDIS_PORT = config("REDIS_PORT", default=6379, cast=int)
REDIS_PASSWORD = config("REDIS_PASSWORD", default="")
REDIS_USE_TLS = config("REDIS_USE_TLS", default=False, cast=bool)


def _make_cache_config(dbnum: int, **overrides) -> dict:
    scheme = "rediss" if REDIS_USE_TLS else "redis"
    password = {"PASSWORD": REDIS_PASSWORD} if REDIS_PASSWORD else {}
    return {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{scheme}://{REDIS_HOST}:{REDIS_PORT}/{dbnum}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
        | password
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

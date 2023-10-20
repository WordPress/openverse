from decouple import config


def get_record_limit():
    """
    Get the limit on records to ingest or index, if applicable. If there is no
    limit, return 0.
    """
    limit_default = 100_000

    environment = config("ENVIRONMENT", default="local").lower()
    if environment in {"prod", "production"}:
        # If we're in production, turn off limits unless it's explicitly provided
        limit_default = 0
    return config("DATA_REFRESH_LIMIT", cast=int, default=limit_default)

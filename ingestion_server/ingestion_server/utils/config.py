from decouple import config


def get_record_limit():
    """
    Check and retrieve the limit of records to ingest for the environment.

    If a limit is explicitly configured, it is always used. Otherwise, production
    defaults to no limit, and all other environments default to 100,000.
    """
    configured_limit = config("DATA_REFRESH_LIMIT", default=None)
    if configured_limit is not None:
        return int(configured_limit)

    environment = config("ENVIRONMENT", default="local").lower()
    if environment in {"prod", "production"}:
        return None

    return 100_000

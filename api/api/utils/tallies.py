import logging
from collections import defaultdict
from datetime import datetime, timedelta

import django_redis
from django_redis.client.default import Redis
from redis.exceptions import ConnectionError


parent_logger = logging.getLogger(__name__)


def get_weekly_timestamp() -> str:
    """Get a timestamp for the Monday of any given week."""
    now = datetime.now()
    monday = now - timedelta(days=now.weekday())
    return monday.strftime("%Y-%m-%d")


def get_monthly_timestamp() -> str:
    """Get a timestamp for the month."""
    now = datetime.now()
    return now.strftime("%Y-%m")


def count_provider_occurrences(results: list[dict], index: str) -> None:
    # Use ``get_redis_connection`` rather than Django's caches
    # so that we can open a pipeline rather than sending off ``n``
    # writes and because the RedisPy client's ``incr`` method
    # is safe by default rather than Django's handspun method which:
    # 1. Takes two requests to execute; and
    # 2. Raises a ``ValueError`` if the key doesn't exist rather than
    # just initialising the key to the value like Redis's behaviour.
    tallies: Redis = django_redis.get_redis_connection("tallies")

    provider_occurrences = defaultdict(int)
    for result in results:
        provider_occurrences[result["provider"]] += 1

    week = get_weekly_timestamp()
    with tallies.pipeline() as pipe:
        for provider, occurrences in provider_occurrences.items():
            pipe.incr(f"provider_occurrences:{index}:{week}:{provider}", occurrences)
            pipe.incr(f"provider_appeared_in_searches:{index}:{week}:{provider}", 1)
        try:
            pipe.execute()
        except ConnectionError:
            logger = parent_logger.getChild("count_provider_occurrences")
            logger.warning("Redis connect failed, cannot increment provider tallies.")

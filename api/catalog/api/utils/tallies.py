from collections import defaultdict
from datetime import datetime

import django_redis
from django_redis.client.default import Redis


def _get_weekly_timestamp() -> str:
    """Get a timestamp for the Monday of any given week."""
    now = datetime.now()
    return datetime(
        now.year,
        now.month,
        # Set the day to Monday of the current week
        now.day - now.weekday(),
    ).strftime("%Y-%m-%d")


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

    week = _get_weekly_timestamp()
    with tallies.pipeline() as pipe:
        for provider, occurrences in provider_occurrences.items():
            pipe.incr(f"provider_occurrences:{index}:{week}:{provider}", occurrences)
            pipe.incr(f"provider_appeared_in_searches:{index}:{week}:{provider}", 1)

        pipe.execute()

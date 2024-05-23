import time

import structlog
from django_redis import get_redis_connection
from redis import Redis


REPORT_LOCK_PREFIX = "soft_lock_report"
MODERATOR_LOCK_PREFIX = "soft_lock_moderator"
PREFIXES = [REPORT_LOCK_PREFIX, MODERATOR_LOCK_PREFIX]

logger = structlog.get_logger(__name__)
redis: Redis = get_redis_connection("default")


class LockManager:
    def __init__(self, media_type):
        self.media_type = media_type

    def prune(self):
        """Delete all expired locks."""

        def _prune(pattern: str):
            now = int(time.time())
            pipeline = redis.pipeline()
            for key in redis.keys(pattern):
                for value, score in redis.zrange(key, 0, -1, withscores=True):
                    if score <= now:
                        logger.info("Deleting expired lock", key=key, value=value)
                        pipeline.zrem(key, value)
            pipeline.execute()

        for prefix in PREFIXES:
            _prune(f"{prefix}:*")

    def add_locks(self, username, object_id):
        """
        Add soft-locks for a given username and report pair.

        :param username: the username of the moderator viewing a report
        :param object_id: the ID of the report being viewed
        """

        object = f"{self.media_type}:{object_id}"
        expiration = int(time.time()) + 5 * 60  # 5 minutes from now

        pipe = redis.pipeline()
        logger.info("Adding lock", object=object, user=username, expiration=expiration)
        pipe.zadd(f"{REPORT_LOCK_PREFIX}:{object}", {username: expiration})
        pipe.zadd(f"{MODERATOR_LOCK_PREFIX}:{username}", {object: expiration})
        pipe.execute()

    def remove_locks(self, username, object_id):
        """
        Remove soft-locks for a given username and report pair.

        :param username: the username of the moderator viewing a report
        :param object_id: the ID of the report being viewed
        """

        object = f"{self.media_type}:{object_id}"

        pipe = redis.pipeline()
        logger.info("Removing lock", object=object, user=username)
        pipe.zrem(f"{REPORT_LOCK_PREFIX}:{object}", username)
        pipe.zrem(f"{MODERATOR_LOCK_PREFIX}:{username}", object)
        pipe.execute()

    def moderator_set(self, object_id) -> set[str]:
        """
        Get the list of moderators on a particular item.

        :param object_id: the ID of the report being viewed
        :return: the list of moderators on a particular item
        """

        self.prune()

        object = f"{self.media_type}:{object_id}"
        mods = set(
            item.decode("utf-8")
            for item in redis.zrange(
                f"{REPORT_LOCK_PREFIX}:{object}",
                start=0,
                end=-1,
            )
        )
        logger.info("Retrieved moderators", object=object, mods=mods)
        return mods

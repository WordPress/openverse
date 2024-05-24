import time

import django_redis
import structlog
from redis import Redis
from redis.exceptions import ConnectionError


LOCK_PREFIX = "moderation_lock"

logger = structlog.get_logger(__name__)


class LockManager:
    def __init__(self, media_type):
        self.media_type = media_type
        redis: Redis = django_redis.get_redis_connection("default")
        try:
            redis.ping()
            self.redis = redis
        except ConnectionError:
            logger.error("Redis connection failed")
            self.redis = None

    def prune(self):
        """Delete all expired locks."""

        now = int(time.time())
        pipe = self.redis.pipeline()
        for key in self.redis.keys(f"{LOCK_PREFIX}:*"):
            for value, score in self.redis.zrange(key, 0, -1, withscores=True):
                if score <= now:
                    logger.info("Deleting expired lock", key=key, value=value)
                    pipe.zrem(key, value)
        pipe.execute()

    def add_locks(self, username, object_id):
        """
        Add a soft-lock for a given report to the given moderator.

        :param username: the username of the moderator viewing a report
        :param object_id: the ID of the report being viewed
        """

        if not self.redis:
            return

        object = f"{self.media_type}:{object_id}"
        expiration = int(time.time()) + 5 * 60  # 5 minutes from now

        logger.info("Adding lock", object=object, user=username, expiration=expiration)
        self.redis.zadd(f"{LOCK_PREFIX}:{username}", {object: expiration})

    def remove_locks(self, username, object_id):
        """
        Remove the soft-lock for a given report from the given moderator.

        :param username: the username of the moderator not viewing a report
        :param object_id: the ID of the report not being viewed
        """

        if not self.redis:
            return

        object = f"{self.media_type}:{object_id}"

        logger.info("Removing lock", object=object, user=username)
        self.redis.zrem(f"{LOCK_PREFIX}:{username}", object)

    def moderator_set(self, object_id) -> set[str]:
        """
        Get the list of moderators on a particular item.

        :param object_id: the ID of the report being viewed
        :return: the list of moderators on a particular item
        """

        if not self.redis:
            return set()

        self.prune()

        object = f"{self.media_type}:{object_id}"
        mods = set()
        logger.info("Retrieved moderators", object=object, mods=mods)
        return mods

    def score(self, username, object_id) -> int:
        """
        Get the score of a particular moderator on a particular item.

        :param username: the username of the moderator viewing a report
        :param object_id: the ID of the report being viewed
        :return: the score of a particular moderator on a particular item
        """

        if not self.redis:
            return 0

        object = f"{self.media_type}:{object_id}"
        score = self.redis.zscore(f"{LOCK_PREFIX}:{username}", object)
        logger.info("Retrieved score", object=object, user=username, score=score)
        return score

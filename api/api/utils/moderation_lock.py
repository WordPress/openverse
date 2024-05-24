import time

import django_redis
import structlog
from redis import Redis
from redis.exceptions import ConnectionError

from api.models.moderation import get_moderators


LOCK_PREFIX = "moderation_lock"
TTL = 10  # seconds

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

    def prune(self) -> dict[str, set[str]]:
        """
        Delete all expired locks and get a mapping of usernames to
        reports that have active locks.

        :return: a mapping of moderators to reports they are viewing
        """

        valid_locks = {}

        now = int(time.time())
        pipe = self.redis.pipeline()
        for username in get_moderators().values_list("username", flat=True):
            key = f"{LOCK_PREFIX}:{username}"
            for value, score in self.redis.zrange(key, 0, -1, withscores=True):
                if score <= now:
                    logger.info("Deleting expired lock", key=key, value=value)
                    pipe.zrem(key, value)
                else:
                    logger.info("Keeping valid lock", key=key, value=value)
                    valid_locks.setdefault(username, set()).add(value.decode())
        pipe.execute()

        return valid_locks

    def add_locks(self, username, object_id):
        """
        Add a soft-lock for a given report to the given moderator.

        :param username: the username of the moderator viewing a report
        :param object_id: the ID of the report being viewed
        """

        if not self.redis:
            return

        object = f"{self.media_type}:{object_id}"
        expiration = int(time.time()) + TTL

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

        valid_locks = self.prune()

        object = f"{self.media_type}:{object_id}"
        mods = {mod for mod, objects in valid_locks.items() if object in objects}
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

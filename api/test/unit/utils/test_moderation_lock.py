from datetime import datetime, timedelta

import pytest
from freezegun import freeze_time
from redis import Redis

from api.utils.moderation_lock import LockManager


@pytest.mark.parametrize(
    "is_cache_reachable, cache_name",
    [(True, "redis"), (False, "unreachable_redis")],
)
def test_lock_manager_handles_missing_redis(is_cache_reachable, cache_name, request):
    request.getfixturevalue(cache_name)

    lm = LockManager("media_type")
    lm.add_locks("test", 10)

    if is_cache_reachable:
        assert isinstance(lm.redis, Redis)
        assert lm.moderator_set(10) == {"test"}
    else:
        assert lm.redis is None
        assert lm.moderator_set(10) == set()


def test_lock_manager_adds_and_removes_locks():
    lm = LockManager("media_type")

    lm.add_locks("one", 10)
    assert lm.moderator_set(10) == {"one"}
    lm.add_locks("two", 10)
    assert lm.moderator_set(10) == {"one", "two"}
    lm.remove_locks("two", 10)
    assert lm.moderator_set(10) == {"one"}


def test_relocking_updates_score(redis):
    lm = LockManager("media_type")
    now = datetime.now()

    with freeze_time(now):
        lm.add_locks("one", 10)
        init_score = lm.score("one", 10)

    with freeze_time(now + timedelta(minutes=2)):
        lm.add_locks("one", 10)
        updated_score = lm.score("one", 10)

    assert updated_score == init_score + 120


def test_lock_manager_prunes_after_timeout():
    lm = LockManager("media_type")
    now = datetime.now()

    with freeze_time(now):
        lm.add_locks("test", 10)

    with freeze_time(now + timedelta(minutes=2)):
        lm.prune()
        assert lm.moderator_set(10) == {"test"}

    with freeze_time(now + timedelta(minutes=6)):
        lm.prune()
        assert lm.moderator_set(10) == set()

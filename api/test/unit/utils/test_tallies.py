from datetime import datetime

import pytest
from freezegun import freeze_time

from api.utils import tallies


# Use a fake media type to avoid having to run each test case for each media type
FAKE_MEDIA_TYPE = "this_is_not_a_media_type"


@pytest.mark.parametrize(
    ("now", "expected_timestamp"),
    (
        pytest.param(datetime(2023, 1, 19), "2023-01-16", id="midweek"),
        pytest.param(datetime(2023, 1, 16), "2023-01-16", id="start_of_week"),
        pytest.param(datetime(2023, 1, 15), "2023-01-09", id="end_of_week"),
    ),
)
def test_count_provider_occurrences_uses_week_timestamp(now, expected_timestamp, redis):
    results = [{"provider": "flickr"} for _ in range(4)] + [
        {"provider": "stocksnap"} for _ in range(6)
    ]
    with freeze_time(now):
        tallies.count_provider_occurrences(results, FAKE_MEDIA_TYPE)

    assert (
        redis.get(f"provider_occurrences:{FAKE_MEDIA_TYPE}:{expected_timestamp}:flickr")
        == b"4"
    )
    assert (
        redis.get(
            f"provider_occurrences:{FAKE_MEDIA_TYPE}:{expected_timestamp}:stocksnap"
        )
        == b"6"
    )
    assert (
        redis.get(
            f"provider_appeared_in_searches:{FAKE_MEDIA_TYPE}:{expected_timestamp}:flickr"
        )
        == b"1"
    )
    assert (
        redis.get(
            f"provider_appeared_in_searches:{FAKE_MEDIA_TYPE}:{expected_timestamp}:stocksnap"
        )
        == b"1"
    )


def test_count_provider_occurrences_increments_existing_tallies(redis):
    results_1 = [{"provider": "flickr"} for _ in range(4)] + [
        {"provider": "stocksnap"} for _ in range(6)
    ]

    results_2 = [{"provider": "flickr"} for _ in range(3)] + [
        {"provider": "inaturalist"} for _ in range(7)
    ]

    now = datetime(2023, 1, 19)  # 16th is start of week
    timestamp = "2023-01-16"
    with freeze_time(now):
        tallies.count_provider_occurrences(results_1, FAKE_MEDIA_TYPE)

    assert (
        redis.get(f"provider_occurrences:{FAKE_MEDIA_TYPE}:{timestamp}:flickr") == b"4"
    )
    assert (
        redis.get(f"provider_occurrences:{FAKE_MEDIA_TYPE}:{timestamp}:stocksnap")
        == b"6"
    )
    assert (
        redis.get(f"provider_appeared_in_searches:{FAKE_MEDIA_TYPE}:{timestamp}:flickr")
        == b"1"
    )
    assert (
        redis.get(
            f"provider_appeared_in_searches:{FAKE_MEDIA_TYPE}:{timestamp}:stocksnap"
        )
        == b"1"
    )

    with freeze_time(now):
        tallies.count_provider_occurrences(results_2, FAKE_MEDIA_TYPE)

    assert (
        redis.get(f"provider_occurrences:{FAKE_MEDIA_TYPE}:{timestamp}:flickr") == b"7"
    )  # 4 + 7
    assert (
        redis.get(f"provider_occurrences:{FAKE_MEDIA_TYPE}:{timestamp}:stocksnap")
        == b"6"
    )  # no change
    assert (
        redis.get(f"provider_occurrences:{FAKE_MEDIA_TYPE}:{timestamp}:inaturalist")
        == b"7"
    )
    assert (
        redis.get(f"provider_appeared_in_searches:{FAKE_MEDIA_TYPE}:{timestamp}:flickr")
        == b"2"
    )
    assert (
        redis.get(
            f"provider_appeared_in_searches:{FAKE_MEDIA_TYPE}:{timestamp}:stocksnap"
        )
        == b"1"
    )
    assert (
        redis.get(
            f"provider_appeared_in_searches:{FAKE_MEDIA_TYPE}:{timestamp}:inaturalist"
        )
        == b"1"
    )


def test_writes_error_logs_for_redis_connection_errors(unreachable_redis, caplog):
    provider_counts = {"flickr": 4, "stocksnap": 6}

    results = [
        {"provider": provider}
        for provider, count in provider_counts.items()
        for _ in range(count)
    ]
    now = datetime(2023, 1, 19)  # 16th is start of week
    with freeze_time(now):
        tallies.count_provider_occurrences(results, FAKE_MEDIA_TYPE)

    assert "Redis connect failed, cannot increment provider tallies." in caplog.text

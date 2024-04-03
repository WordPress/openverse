from typing import Unpack, get_type_hints
from datetime import timedelta


def ttl(days: int = 0, seconds: int = 0, minutes: int = 0, hours: int = 0, weeks: int = 0) -> int:
    """
    Retrieve the total number of seconds for kwargs.

    Based on `timedelta` arguments, but leaves out anything smaller than
    a second, because TTLs are defined in seconds, not milli or microseconds.

    It also types all inputs as `int`, rather than `float`, and only returns an int.
    """
    return int(timedelta(
        days=days,
        seconds=seconds,
        minutes=minutes,
        hours=hours,
        weeks=weeks,
    ).total_seconds())

"""
Return freed heap pages to the kernel periodically.

Under load the API's RSS grows by a few MB per hour even though the Python
heap stays flat: glibc never releases freed chunks that sit between live ones.
``MALLOC_TRIM_THRESHOLD_`` only covers the top of the heap, so the only way to
release them is an explicit ``malloc_trim``, which ``madvise``s every fully
free page. In staging it reclaimed 2-5 MB per 15 minutes and held the RSS of
a loaded worker flat where it previously grew without bound.
"""

import ctypes
import threading
import time
from collections.abc import Callable

import structlog


logger = structlog.get_logger(__name__)


def _get_malloc_trim() -> Callable[[int], int] | None:
    """Return glibc's ``malloc_trim`` or ``None`` on other allocators (macOS, musl)."""
    try:
        return ctypes.CDLL(None).malloc_trim
    except (OSError, AttributeError, TypeError):
        return None


def start_malloc_trim(interval_seconds: float) -> threading.Thread | None:
    """
    Start a daemon thread that calls ``malloc_trim(0)`` every ``interval_seconds``.

    Returns the thread, or ``None`` if the interval is not positive or the
    allocator has no ``malloc_trim``.
    """

    if interval_seconds <= 0:
        return None

    malloc_trim = _get_malloc_trim()
    if malloc_trim is None:
        logger.warning("malloc_trim is unavailable, not trimming the heap periodically")
        return None

    def trim_forever():
        while True:
            time.sleep(interval_seconds)
            released = malloc_trim(0)
            logger.debug("Trimmed the heap", released=bool(released))

    thread = threading.Thread(target=trim_forever, name="malloc_trim", daemon=True)
    thread.start()
    return thread

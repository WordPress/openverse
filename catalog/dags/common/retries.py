"""
Retry decorators for flaky provider APIs, built on tenacity.

Both decorators wait with exponential backoff and full jitter, and re-raise the
last exception once they stop retrying.
"""

from collections.abc import Collection

from requests.exceptions import HTTPError
from tenacity import (
    retry,
    retry_if_exception,
    retry_if_exception_type,
    stop_after_attempt,
    stop_after_delay,
    wait_random_exponential,
)


SERVER_ERROR_CODES = frozenset({502, 503, 504})


def retry_on_http_status(
    max_time: float, status_codes: Collection[int] = SERVER_ERROR_CODES
):
    """
    Retry while the call raises an ``HTTPError`` whose status code is in
    ``status_codes``, for up to ``max_time`` seconds. Other errors are raised
    immediately.
    """

    def has_retryable_status(exc: BaseException) -> bool:
        return (
            isinstance(exc, HTTPError)
            and exc.response is not None
            and exc.response.status_code in status_codes
        )

    return retry(
        retry=retry_if_exception(has_retryable_status),
        wait=wait_random_exponential(multiplier=1),
        stop=stop_after_delay(max_time),
        reraise=True,
    )


def retry_on_exceptions(
    exceptions: type[BaseException] | tuple[type[BaseException], ...],
    max_tries: int,
):
    """Retry while the call raises one of ``exceptions``, up to ``max_tries`` calls."""
    return retry(
        retry=retry_if_exception_type(exceptions),
        wait=wait_random_exponential(multiplier=1),
        stop=stop_after_attempt(max_tries),
        reraise=True,
    )

import asyncio
import logging
from collections.abc import Awaitable


parent_logger = logging.getLogger(__name__)


_fire_and_forget_logger = parent_logger.getChild("fire_and_forget")


def fire_and_forget(awaitable: Awaitable) -> None:
    """
    Consume an awaitable without waiting for it to finish.

    This allows us to "fire and forget" an async function that
    we don't care about the result of. This is useful, for example,
    if some operation creates a side effect that isn't necessary for
    the response we're processing (e.g., Redis tallying).
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError as exc:
        _fire_and_forget_logger.error(
            "`fire_and_forget` must be called inside a running" " event loop."
        )
        raise exc

    loop.create_task(awaitable)

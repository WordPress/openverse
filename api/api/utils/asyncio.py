import asyncio
import logging
from collections.abc import Awaitable

from rest_framework.generics import get_object_or_404

from asgiref.sync import sync_to_async


parent_logger = logging.getLogger(__name__)


_do_not_wait_for_logger = parent_logger.getChild("do_not_wait_for")


def do_not_wait_for(awaitable: Awaitable) -> None:
    """
    Consume an awaitable without waiting for it to finish.

    This allows us to call an async function that we don't care about
    the result of, without needing to wait for it to complete. This is
    useful, for example, if some operation creates a side effect that
    isn't necessary for the response we're processing (e.g., Redis tallying).
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError as exc:
        _do_not_wait_for_logger.error(
            "`do_not_wait_for` must be called inside a running event loop."
        )
        raise exc

    loop.create_task(awaitable)


aget_object_or_404 = sync_to_async(get_object_or_404)

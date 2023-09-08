import asyncio
import inspect
import logging
import weakref
from collections.abc import Callable

from django.core.handlers.wsgi import WSGIHandler

from asgiref.sync import async_to_sync


parent_logger = logging.getLogger(__name__)


class OpenverseWSGIHandler(WSGIHandler):
    """
    Extend default WSGIHandler to add a shutdown hook for asyncio cleanup.

    Handlers are registered by calling `register_shutdown_handler`.
    The class maintains only weak references to handler functions
    and methods to prevent memory leaks. This removes the need
    for explicit deregistration of handlers if, for example, their associated
    objects (if a method) or contexts are garbage collected.

    Asynchronous handlers are automatically supported via `async_to_sync`
    and do not need special consideration at registration time.
    """

    logger = parent_logger.getChild("OpenverseWSGIHandler")

    def __init__(self):
        super().__init__()
        self._on_shutdown: list[weakref.WeakMethod | weakref.ref] = []

    def register_shutdown_handler(self, handler: Callable[[], None]):
        """Register an individual shutdown handler."""
        if inspect.ismethod(handler):
            self._on_shutdown.append(weakref.WeakMethod(handler))
        else:
            self._on_shutdown.append(weakref.ref(handler))

    def shutdown(self):
        self.logger.info(
            f"Shutting down with {len(self._on_shutdown)} handlers to execute"
        )

        for handler_ref in self._on_shutdown:
            if not (handler := handler_ref()):
                self.logger.debug("Reference lost, skipping handler")
                continue

            if asyncio.iscoroutinefunction(handler):
                async_to_sync(handler)()
            else:
                handler()

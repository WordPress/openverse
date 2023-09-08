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
    Extend default WSGIHandler for additional asyncio functionality.

    There are two primary extensions in this class:
    1. The addition of a `shutdown` hook, called in worker stoppage
        hooks. These are configured in the Gunicorn configuration.
    2. The creation of a "main event loop" to use for every request to
        the worker. See below for further explanation about why this is
        necessary.

    ## Shutdown handlers usage

    Handlers are registered by calling `register_shutdown_handler`.
    The class maintains only weak references to handler functions
    and methods to prevent memory leaks. This removes the need
    for explicit deregistration of handlers if, for example, their associated
    objects (if a method) or contexts are garbage collected.

    Asynchronous handlers are automatically supported via `async_to_sync`
    and do not need special consideration at registration time.

    ## Event loop creation

    asgiref's `async_to_sync` will create a new event loop to run the passed
    awaitable each time it is called. This means, for example, that each
    """

    logger = parent_logger.getChild("OpenverseWSGIHandler")

    def __init__(self):
        super().__init__()
        self._on_shutdown: list[weakref.WeakMethod | weakref.ref] = []
        # self._create_main_event_loop()

    def _create_main_event_loop(self):
        main_event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(main_event_loop)
        self.register_shutdown_handler(main_event_loop.close)

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

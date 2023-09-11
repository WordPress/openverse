import asyncio
import inspect
import logging
import weakref
from collections.abc import Callable

from django.core.handlers.asgi import ASGIHandler


parent_logger = logging.getLogger(__name__)


class OpenverseASGIHandler(ASGIHandler):
    """
    Extend default ASGIHandler to implement lifetime hooks.

    Handlers are registered by calling `register_shutdown_handler`.
    The class maintains only weak references to handler functions
    and methods to prevent memory leaks. This removes the need
    for explicit deregistration of handlers if, for example, their associated
    objects (if a method) or contexts are garbage collected.

    Asynchronous handlers are automatically supported via `async_to_sync`
    and do not need special consideration at registration time.
    """

    logger = parent_logger.getChild("OpenverseASGIHandler")

    def __init__(self):
        super().__init__()
        self._on_shutdown: list[weakref.WeakMethod | weakref.ref] = []

    def _clean_ref(self, ref):
        self.logger.info("Cleaning up a ref")
        self._on_shutdown.remove(ref)

    def register_shutdown_handler(self, handler: Callable[[], None]):
        """Register an individual shutdown handler."""
        if inspect.ismethod(handler):
            ref = weakref.WeakMethod(handler, self._clean_ref)
        else:
            ref = weakref.ref(handler, self._clean_ref)

        self._on_shutdown.append(ref)

    async def __call__(self, scope, receive, send):
        if scope["type"] == "lifespan":
            while True:
                message = await receive()
                if message["type"] == "lifespan.startup":
                    await send({"type": "lifespan.startup.complete"})

                elif message["type"] == "lifespan.shutdown":
                    await self.shutdown()
                    await send({"type": "lifespan.shutdown.complete"})
                    return

        await super().__call__(scope, receive, send)

    async def shutdown(self):
        live_handlers = 0

        for handler_ref in self._on_shutdown:
            if not (handler := handler_ref()):
                self.logger.debug("Reference dead, skipping handler")
                continue

            live_handlers += 1

            if asyncio.iscoroutinefunction(handler):
                await handler()
            else:
                handler()

        self.logger.info(f"Executed {live_handlers} handler(s) before shutdown.")

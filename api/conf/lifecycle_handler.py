import asyncio
import inspect
import logging
import weakref
from collections.abc import Callable

from django.core.handlers.asgi import ASGIHandler

import sentry_sdk


parent_logger = logging.getLogger(__name__)


class ASGILifecycleHandler:
    """
    Handle ASGI lifecycle messages.

    Django's ASGIHandler does not handle these messages,
    so we have to implement it ourselves. Only shutdown handlers
    are currently supported.

    Register shutdown handlers using the `register_shutdown_handler`
    method. The class maintains only weak references to handler functions
    and methods to prevent memory leaks. This removes the need
    for explicit deregistration of handlers if, for example, their associated
    contexts are garbage collected.

    Asynchronous handlers are automatically supported via `async_to_sync`
    and do not need special consideration at registration time.
    """

    logger = parent_logger.getChild("ASGILifecycleHandler")

    def __init__(self, app: ASGIHandler):
        self.app = app
        self._on_shutdown: list[weakref.WeakMethod | weakref.ref] = []
        self.has_shutdown = False

    def _clean_ref(self, ref):
        if self.has_shutdown:
            return

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

        await self.app(scope, receive, send)

    async def shutdown(self):
        live_handlers = 0

        while self._on_shutdown:
            handler_ref = self._on_shutdown.pop()
            if not (handler := handler_ref()):
                self.logger.debug("Reference dead, skipping handler")
                continue

            live_handlers += 1

            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
            except Exception as exc:
                sentry_sdk.capture_exception(exc)
                self.logger.error(f"Handler {repr(handler)} raised exception.")

        self.logger.info(f"Executed {live_handlers} handler(s) before shutdown.")
        self.has_shutdown = True

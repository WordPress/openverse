"""
Safely share httpx AsyncClient for the entire application.
`httpx` recommends reusing a single AsyncClient for the entire
application[^aiohttp-recommends] in order to benefit from connection pooling.

The basic idea for this approach was found on Stackoverflow[^credit].

However, because our application is not fully asynchronous and we
rely on `async_to_sync`, and because `async_to_sync` in a non-async
program runs "in a per-call event loop in arbitrary sub-threads"[^asgiref],
we need to check whether the running loop has an associated session.

This is because a given client instance only works within the context of the
event loop in which it was created. At request time, if that loop is closed,
the client will not attempt to retrieve the currently running loop or create a
new one. It will simply crash with an "event loop closed" RuntimeError. This
is a sensible implementation as it is very safe. Due to the nature of our
application's runtime and the particular contexts in which we use `httpx`, we
cannot, in fact, easily share a single client for the entire lifetime of our
application. This will continue to be the case until we switch to a fully ASGI
application (meaning, a Django application where all routes are marked `async`
and there are no thread sensitive calls to `sync_to_async`).

Therefore, the implementation in this module makes the relationship between
an httpx client and the event loop it belongs to explicit. When the loop is
gone, the client also gets removed. Any time a request for a client is made,
if a client already exists for the current loop, the client is reused. If one
has not been created for the loop, then we create a new one.

[^shared-client-benefits]:
    https://www.python-httpx.org/advanced/#client-instances

[^credit]: CC BY-SA 4.0 by StackOverflow user
    https://stackoverflow.com/users/8601760/aaron
    https://stackoverflow.com/a/72634224

[^asgiref]: https://github.com/django/asgiref#synchronous-code--threads
"""

import asyncio
import logging
import weakref

import httpx

from conf.wsgi import application


parent_logger = logging.getLogger(__name__)


_CLIENTS: weakref.WeakKeyDictionary[
    asyncio.BaseEventLoop, httpx.AsyncClient
] = weakref.WeakKeyDictionary()


_LOCKS: weakref.WeakKeyDictionary[
    asyncio.BaseEventLoop, asyncio.Lock
] = weakref.WeakKeyDictionary()


async def get_httpx_client() -> httpx.AsyncClient:
    logger = parent_logger.getChild("safe_get_httpx_session")

    loop = asyncio.get_running_loop()

    if loop not in _LOCKS:
        _LOCKS[loop] = asyncio.Lock()

    async with _LOCKS[loop]:
        client = _CLIENTS.get(loop)

        if not client:
            create_client = True
            logger.info("No existing client for this loop. Creating new client.")
        elif client.is_closed:
            create_client = True
            logger.info("Previous client closed. Replacing with new client.")

        if create_client:
            client = httpx.AsyncClient()
            application.register_shutdown_handler(client.aclose)

            _CLIENTS[loop] = client
        else:
            logger.info("Reusing existing session")

    return _CLIENTS[loop]

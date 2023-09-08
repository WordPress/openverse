"""
Safely share aiohttp ClientSession for the entire application.

`aiohttp` recommends reusing a single ClientSession for the entire
application[^aiohttp-recommends] because `ClientSession` instantiation
is particularly heavy.

The basic idea for this approach was found on Stackoverflow[^credit]

However, because our application is not fully asynchronous and we
rely on `async_to_sync`, and because `async_to_sync` in a non-async
program runs "in a per-call event loop in arbitrary sub-threads"[^asgiref],
we need to check whether the running loop has an associated session.
This is because sessions hold on to a reference of the loop in which they were
created. At request time, if that loop is closed, the session will not attempt
to retrieve the currently running loop or create a new one. It will simply
crash with an "event loop closed" RuntimeError. This is a sensible
implementation as it is very safe. Due to the nature of our application's
runtime and the particular contexts in which we use `aiohttp`, we cannot,
in fact, easily share a single ClientSession for the entire lifetime of our
application. This will continue to be the case until we switch to a fully ASGI
application (meaning, a Django application where all routes are marked `async`
and there are no thread sensitive calls to `sync_to_async`).

The implication of this is that we have two options:
1. Create a new session when we detect a loop that does not yet have a session.
2. Find a way to "reuse" the existing session object with new loops.

The first option essentially negates the benefits of reusable aiohttp sessions
outside of code paths that repeatedly call `get_aiohttp_session` within a
single `async_to_sync` context. Those repeated calls will all happen within
the same loop and will therefore be able to reuse the session created for that
loop. It could also easily create a memory leak without careful management
of the retained sessions.

The second option seems tempting, then, because it would be the most widely
effective option, as far as eliminating the cost of recreating `ClientSession`
almost every time one is needed. However, aiohttp does not provide a method
for swapping the referenced event loop on `ClientSession`, so anything we do
here would be definitively hacky. It's also hard to know what the thread-safety
implications are of swapping the `_loop` attribute on the session and its inner
connector object. This appears to work fine locally, but it's essentially
impossible to simulate production traffic locally, so we cannot easily predict
how this would behave in real use.

For now, both implementations are present below. The first option is aptly
named with the `safe_` prefix. The second is likewise named with the `unsafe_`
prefix. To switch between the two, we just swap the assignment to
`get_aiohttp_session` at the bottom of the module.

[^aiohttp-recommends]:
    https://docs.aiohttp.org/en/stable/client_quickstart.html#make-a-request

[^credit]: CC BY-SA 4.0 by StackOverflow user
    https://stackoverflow.com/users/8601760/aaron
    https://stackoverflow.com/a/72634224

[^asgiref]: https://github.com/django/asgiref#synchronous-code--threads
"""

import asyncio
import logging
import time
import weakref

import aiohttp

from conf.wsgi import application


parent_logger = logging.getLogger(__name__)


_SESSION: aiohttp.ClientSession = None

_lock = asyncio.Lock()


async def unsafe_get_aiohttp_session():
    logger = parent_logger.getChild("unsafe_get_aiohttp_session")

    global _SESSION
    loop = asyncio.get_running_loop()

    # Lock to prevent calls fighting to mutable global _SESSION
    async with _lock:
        create_session = False
        msg = "Reusing existing session."

        if not _SESSION:
            create_session = True
            msg = "No existing session. Creating new session."
        elif _SESSION.closed:
            create_session = True
            msg = "Previous session closed. Replacing with new session."
        elif _SESSION._loop is not loop:
            msg = "Reusing session with new loop."
            _SESSION._loop = loop
            _SESSION.connector._loop = loop

        logger.info(msg)

        if create_session:
            _SESSION = aiohttp.ClientSession()
            application.register_shutdown_handler(_SESSION.close)

    return _SESSION


_SESSIONS: weakref.WeakKeyDictionary[
    asyncio.BaseEventLoop, aiohttp.ClientSession
] = weakref.WeakKeyDictionary()


_LOCKS: weakref.WeakKeyDictionary[
    asyncio.BaseEventLoop, asyncio.Lock
] = weakref.WeakKeyDictionary()


_cleanup_most_recent = time.time()
_cleanup_interval = 15


async def _cleanup():
    """Clean up sessions and locks for closed loops."""
    global _cleanup_most_recent

    if time.time() - _cleanup_most_recent < _cleanup_interval:
        return

    logger = parent_logger.getChild("_cleanup")
    logger.info("Cleaning up sessions and locks")

    for loop in list(iter(_SESSIONS.keys())):
        if loop.is_closed():
            await _SESSIONS[loop].close()
            del _SESSIONS[loop]

    for loop in list(iter(_LOCKS.keys())):
        if loop.is_closed():
            del _LOCKS[loop]

    _cleanup_most_recent = time.time()


async def safe_get_aiohttp_session():
    logger = parent_logger.getChild("safe_get_aiohttp_session")

    loop = asyncio.get_running_loop()

    if loop not in _LOCKS:
        _LOCKS[loop] = asyncio.Lock()

    async with _LOCKS[loop]:
        session = _SESSIONS.get(loop)

        if not session:
            create_session = True
            logger.info("No existing session for this loop. Creating new session.")
        elif session.closed:
            create_session = True
            logger.info("Previous session closed. Replacing with new session.")

        if create_session:
            session = aiohttp.ClientSession()
            application.register_shutdown_handler(session.close)
            _SESSIONS[loop] = session
        else:
            logger.info("Reusing existing session")

    await _cleanup()
    return _SESSIONS[loop]


get_aiohttp_session = safe_get_aiohttp_session

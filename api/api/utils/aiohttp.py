import asyncio
import logging
import weakref

import aiohttp

from conf.asgi import APPLICATION_LIFECYCLE


logger = logging.getLogger(__name__)


_SESSIONS: weakref.WeakKeyDictionary[
    asyncio.AbstractEventLoop, aiohttp.ClientSession
] = weakref.WeakKeyDictionary()

_LOCKS: weakref.WeakKeyDictionary[
    asyncio.AbstractEventLoop, asyncio.Lock
] = weakref.WeakKeyDictionary()


async def get_aiohttp_session() -> aiohttp.ClientSession:
    """
    Safely retrieve a shared aiohttp session for the current event loop.

    If the loop already has an aiohttp session associated, it will be reused.
    If the loop has not yet had an aiohttp session created for it, a new one
    will be created and returned.

    While the main application will always run in the same loop, and while
    that covers 99% of our use cases, it is still possible for `async_to_sync`
    to cause a new loop to be created if, for example, `force_new_loop` is
    passed. In order to prevent surprises should that ever be the case, this
    function assumes that it's possible for multiple loops to be present in
    the lifetime of the application and therefore we need to verify that each
    loop gets its own session.
    """

    loop = asyncio.get_running_loop()

    if loop not in _LOCKS:
        _LOCKS[loop] = asyncio.Lock()

    async with _LOCKS[loop]:
        if loop not in _SESSIONS:
            create_session = True
            msg = "No session for loop. Creating new session."
        elif _SESSIONS[loop].closed:
            create_session = True
            msg = "Loop's previous session closed. Creating new session."
        else:
            create_session = False
            msg = "Reusing existing session for loop."

        logger.info(msg)

        if create_session:
            session = aiohttp.ClientSession()
            APPLICATION_LIFECYCLE.register_shutdown_handler(session.close)
            _SESSIONS[loop] = session

        return _SESSIONS[loop]

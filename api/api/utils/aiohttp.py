"""
Safely share aiohttp ClientSession for the entire application.

CC BY-SA 4.0 by StackOverflow user https://stackoverflow.com/users/8601760/aaron
https://stackoverflow.com/a/72634224
"""

import asyncio

import aiohttp

from conf.asgi import application


# aiohttp recommends reusing the same session for the whole application
# https://docs.aiohttp.org/en/stable/client_quickstart.html#make-a-request
_SESSION: aiohttp.ClientSession = None

_lock = asyncio.Lock()


async def get_aiohttp_session():
    global _SESSION

    async with _lock:
        if not _SESSION or _SESSION.closed:
            _SESSION = aiohttp.ClientSession()
            application.on_shutdown.append(_SESSION.close)

    return _SESSION

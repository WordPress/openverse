import aiohttp


# aiohttp recommends reusing the same session for the whole application
# https://docs.aiohttp.org/en/stable/client_quickstart.html#make-a-request
_SESSION: aiohttp.ClientSession = None


def get_aiohttp_session():
    global _SESSION

    if _SESSION is None or _SESSION.loop.is_closed():
        _SESSION = aiohttp.ClientSession()

    return _SESSION

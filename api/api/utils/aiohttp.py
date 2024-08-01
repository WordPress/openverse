import asyncio
import time
import weakref

import aiohttp
import sentry_sdk
import structlog
from django_asgi_lifespan.signals import asgi_shutdown


logger = structlog.get_logger(__name__)


_SESSIONS: weakref.WeakKeyDictionary[
    asyncio.AbstractEventLoop, aiohttp.ClientSession
] = weakref.WeakKeyDictionary()

_LOCKS: weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, asyncio.Lock] = (
    weakref.WeakKeyDictionary()
)


@asgi_shutdown.connect
async def _close_sessions(sender, **kwargs):
    logger.debug("Closing aiohttp sessions on application shutdown")

    closed_sessions = 0

    while _SESSIONS:
        loop, session = _SESSIONS.popitem()
        try:
            await session.close()
            closed_sessions += 1
        except BaseException as exc:
            logger.error(exc)
            sentry_sdk.capture_exception(exc)

    logger.debug("Successfully closed %s session(s)", closed_sessions)


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
            session = aiohttp.ClientSession(trace_configs=[LogTiming()])
            _SESSIONS[loop] = session

        return _SESSIONS[loop]


class LogTiming(aiohttp.TraceConfig):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.on_request_start.append(self._start_timing)
        self.on_request_end.append(self._end_timing)

    async def _start_timing(
        self,
        session: aiohttp.ClientSession,
        trace_config_ctx,
        params: aiohttp.TraceRequestStartParams,
    ):
        trace_config_ctx.start_time = time.perf_counter()

    async def _end_timing(
        self,
        session: aiohttp.ClientSession,
        trace_config_ctx,
        params: aiohttp.TraceRequestEndParams,
    ):
        if not (
            trace_config_ctx.trace_request_ctx
            and "timing_event_name" in trace_config_ctx.trace_request_ctx
        ):
            return

        end_time = time.perf_counter()
        start_time = trace_config_ctx.start_time

        request_ctx = trace_config_ctx.trace_request_ctx

        logger.info(
            request_ctx["timing_event_name"],
            status=params.response.status,
            time=end_time - start_time,
            url=str(params.url),
            **request_ctx.get("timing_event_ctx", {}),
        )

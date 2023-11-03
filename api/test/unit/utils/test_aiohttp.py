import asyncio

import pytest
from asgiref.sync import async_to_sync

from api.utils.aiohttp import get_aiohttp_session
from conf.asgi import application


@pytest.fixture(autouse=True)
def get_new_loop():
    loops: list[asyncio.AbstractEventLoop] = []

    def _get_new_loop():
        loop = asyncio.new_event_loop()
        loops.append(loop)
        return loop

    yield _get_new_loop

    async_to_sync(application.shutdown)()
    for loop in loops:
        loop.close()


def test_reuses_session_within_same_loop(get_new_loop):
    loop = get_new_loop()

    session_1 = loop.run_until_complete(get_aiohttp_session())
    session_2 = loop.run_until_complete(get_aiohttp_session())

    assert session_1 is session_2


def test_creates_new_session_for_separate_loops(get_new_loop):
    loop_1 = get_new_loop()
    loop_2 = get_new_loop()

    loop_1_session = loop_1.run_until_complete(get_aiohttp_session())
    loop_2_session = loop_2.run_until_complete(get_aiohttp_session())

    assert loop_1_session is not loop_2_session


def test_multiple_loops_reuse_separate_sessions(get_new_loop):
    loop_1 = get_new_loop()
    loop_2 = get_new_loop()

    loop_1_session_1 = loop_1.run_until_complete(get_aiohttp_session())
    loop_1_session_2 = loop_1.run_until_complete(get_aiohttp_session())
    loop_2_session_1 = loop_2.run_until_complete(get_aiohttp_session())
    loop_2_session_2 = loop_2.run_until_complete(get_aiohttp_session())

    assert loop_1_session_1 is loop_1_session_2
    assert loop_2_session_1 is loop_2_session_2


def test_registers_shutdown_cleanup(get_new_loop):
    assert len(application._on_shutdown) == 0

    loop = get_new_loop()
    loop.run_until_complete(get_aiohttp_session())

    assert len(application._on_shutdown) == 1

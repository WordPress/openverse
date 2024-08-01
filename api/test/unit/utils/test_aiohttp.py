import asyncio

import aiohttp
import pytest
from structlog.testing import capture_logs

from api.utils.aiohttp import get_aiohttp_session


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


def test_log_timing_trace_config_ignored_if_event_name_undefined(session_loop):
    aiohttp_session = session_loop.run_until_complete(get_aiohttp_session())

    with capture_logs() as logs:
        session_loop.run_until_complete(
            aiohttp_session.get("http://httpbin:8080/status/202")
        )

    assert len(logs) == 0


_EXPECTED_BASE_CTX = {"url", "status", "time"}


def test_log_timing_trace_config_no_request_ctx(session_loop):
    aiohttp_session = session_loop.run_until_complete(get_aiohttp_session())

    event_name = "no_request_ctx_timing_event_test"
    with capture_logs() as logs:
        session_loop.run_until_complete(
            aiohttp_session.get(
                "http://httpbin:8080/status/202",
                trace_request_ctx={
                    "timing_event_name": event_name,
                },
            )
        )

    log_event = next(log for log in logs if log["event"] == event_name)
    assert _EXPECTED_BASE_CTX & log_event.keys() == _EXPECTED_BASE_CTX
    assert log_event["status"] == 202
    assert log_event["url"] == "http://httpbin:8080/status/202"


def test_log_timing_trace_config_empty_request_ctx(session_loop):
    aiohttp_session = session_loop.run_until_complete(get_aiohttp_session())

    event_name = "empty_request_ctx_timing_event_test"
    with capture_logs() as logs:
        session_loop.run_until_complete(
            aiohttp_session.get(
                "http://httpbin:8080/status/202",
                trace_request_ctx={
                    "timing_event_name": event_name,
                    "timing_event_ctx": {},
                },
            )
        )

    log_event = next(log for log in logs if log["event"] == event_name)
    assert _EXPECTED_BASE_CTX & log_event.keys() == _EXPECTED_BASE_CTX
    assert log_event["status"] == 202
    assert log_event["url"] == "http://httpbin:8080/status/202"


def test_log_timing_trace_config_with_request_ctx(session_loop):
    aiohttp_session = session_loop.run_until_complete(get_aiohttp_session())

    event_name = "empty_request_ctx_timing_event_test"
    event_ctx = {
        "amazing_info": "hello_test",
        "helpful_info": "so cool",
    }

    with capture_logs() as logs:
        session_loop.run_until_complete(
            aiohttp_session.get(
                "http://httpbin:8080/status/202",
                trace_request_ctx={
                    "timing_event_name": event_name,
                    "timing_event_ctx": event_ctx,
                },
            )
        )

    log_event = next(log for log in logs if log["event"] == event_name)

    assert _EXPECTED_BASE_CTX & log_event.keys() == _EXPECTED_BASE_CTX
    assert log_event["status"] == 202
    assert log_event["url"] == "http://httpbin:8080/status/202"

    log_event_items = log_event.items()
    for event_ctx_item in event_ctx.items():
        assert event_ctx_item in log_event_items


def test_log_timing_trace_config_response_exception(session_loop, monkeypatch):
    aiohttp_session = session_loop.run_until_complete(get_aiohttp_session())

    event_name = "response_exception_timing_event_test"

    with capture_logs() as logs:
        with pytest.raises(aiohttp.ClientResponseError):
            session_loop.run_until_complete(
                aiohttp_session.get(
                    "http://httpbin:8080/status/400",
                    # raise for status coerces a client response error within the tracing context
                    raise_for_status=True,
                    trace_request_ctx={
                        "timing_event_name": event_name,
                    },
                )
            )

    log_event = next(log for log in logs if log["event"] == event_name)

    assert _EXPECTED_BASE_CTX & log_event.keys() == _EXPECTED_BASE_CTX
    assert log_event["status"] == 400
    assert log_event["url"] == "http://httpbin:8080/status/400"


def test_log_timing_trace_config_runtime_exception(session_loop, monkeypatch):
    aiohttp_session = session_loop.run_until_complete(get_aiohttp_session())

    event_name = "runtime_exception_timing_event_test"

    with capture_logs() as logs:
        with pytest.raises(aiohttp.InvalidURL):
            session_loop.run_until_complete(
                aiohttp_session.get(
                    # The malformed URL will raise an error when the client tries to parse
                    # the URL to redirect to
                    "http://httpbin:8080/redirect-to",
                    params={"url": "//:@/"},
                    allow_redirects=True,
                    trace_request_ctx={
                        "timing_event_name": event_name,
                    },
                )
            )

    log_event = next(log for log in logs if log["event"] == event_name)

    assert _EXPECTED_BASE_CTX & log_event.keys() == _EXPECTED_BASE_CTX
    assert log_event["status"] == -1
    assert log_event["url"] == "http://httpbin:8080/redirect-to?url=//:@/"


def test_log_timing_trace_config_timeout(session_loop):
    aiohttp_session = session_loop.run_until_complete(get_aiohttp_session())

    event_name = "empty_request_ctx_timing_event_test"

    with capture_logs() as logs:
        with pytest.raises(asyncio.TimeoutError):
            session_loop.run_until_complete(
                aiohttp_session.get(
                    "http://httpbin:8080/delay/4",
                    timeout=aiohttp.ClientTimeout(1),
                    trace_request_ctx={
                        "timing_event_name": event_name,
                    },
                )
            )

    log_event = next(log for log in logs if log["event"] == event_name)

    assert _EXPECTED_BASE_CTX & log_event.keys() == _EXPECTED_BASE_CTX
    assert log_event["status"] == -2
    assert log_event["url"] == "http://httpbin:8080/delay/4"

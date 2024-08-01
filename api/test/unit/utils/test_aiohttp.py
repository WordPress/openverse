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
            aiohttp_session.get("http://localhost:50280/v1/images/")
        )

    assert len(logs) == 0


_EXPECTED_BASE_CTX = {"url", "status", "time"}


def test_log_timing_trace_config_no_request_ctx(session_loop):
    aiohttp_session = session_loop.run_until_complete(get_aiohttp_session())

    event_name = "no_request_ctx_timing_event_test"
    with capture_logs() as logs:
        session_loop.run_until_complete(
            aiohttp_session.get(
                "http://localhost:50280/v1/images/",
                trace_request_ctx={
                    "timing_event_name": event_name,
                },
            )
        )

    log_event = next(log for log in logs if log["event"] == event_name)
    assert _EXPECTED_BASE_CTX & log_event.keys() == _EXPECTED_BASE_CTX


def test_log_timing_trace_config_empty_request_ctx(session_loop):
    aiohttp_session = session_loop.run_until_complete(get_aiohttp_session())

    event_name = "empty_request_ctx_timing_event_test"
    with capture_logs() as logs:
        session_loop.run_until_complete(
            aiohttp_session.get(
                "http://localhost:50280/v1/images/",
                trace_request_ctx={
                    "timing_event_name": event_name,
                    "timing_event_ctx": {},
                },
            )
        )

    log_event = next(log for log in logs if log["event"] == event_name)
    assert _EXPECTED_BASE_CTX & log_event.keys() == _EXPECTED_BASE_CTX


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
                "http://localhost:50280/v1/images/",
                trace_request_ctx={
                    "timing_event_name": event_name,
                    "timing_event_ctx": event_ctx,
                },
            )
        )

    log_event = next(log for log in logs if log["event"] == event_name)

    assert _EXPECTED_BASE_CTX & log_event.keys() == _EXPECTED_BASE_CTX

    log_event_items = log_event.items()
    for event_ctx_item in event_ctx.items():
        assert event_ctx_item in log_event_items

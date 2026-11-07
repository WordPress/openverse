import threading

from conf import malloc_trim


def test_disabled_when_interval_is_not_positive(monkeypatch):
    monkeypatch.setattr(malloc_trim, "_get_malloc_trim", lambda: lambda pad: 1)

    assert malloc_trim.start_malloc_trim(0) is None
    assert malloc_trim.start_malloc_trim(-1) is None


def test_disabled_without_glibc(monkeypatch):
    monkeypatch.setattr(malloc_trim, "_get_malloc_trim", lambda: None)

    assert malloc_trim.start_malloc_trim(1) is None


def test_trims_periodically(monkeypatch):
    calls = []
    called_twice = threading.Event()

    def fake_trim(pad):
        calls.append(pad)
        if len(calls) >= 2:
            called_twice.set()
        return 1

    monkeypatch.setattr(malloc_trim, "_get_malloc_trim", lambda: fake_trim)

    thread = malloc_trim.start_malloc_trim(0.01)

    assert thread is not None
    assert thread.daemon
    assert called_twice.wait(timeout=5)
    assert calls[:2] == [0, 0]


def test_real_malloc_trim_matches_platform():
    trim = malloc_trim._get_malloc_trim()

    if trim is not None:
        # glibc returns 1 when memory was released and 0 otherwise, never raises
        assert trim(0) in (0, 1)

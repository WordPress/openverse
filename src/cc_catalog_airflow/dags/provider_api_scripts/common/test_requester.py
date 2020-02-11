import requests
import time

from common import requester


def test_get_waits_before_getting(monkeypatch):
    delay = 0.2

    def mock_requests_get(url, params, **kwargs):
        return requests.Response()

    monkeypatch.setattr(requester.requests, 'get', mock_requests_get)
    dq = requester.DelayedRequester(delay)
    s = time.time()
    dq.get('https://google.com')
    print(time.time() - s)
    start = time.time()
    dq.get('https://google.com')
    assert time.time() - start >= delay


def test_get_handles_exception(monkeypatch):
    def mock_requests_get(url, params, **kwargs):
        raise requests.exceptions.ReadTimeout('test timeout!')

    monkeypatch.setattr(requester.requests, 'get', mock_requests_get)

    dq = requester.DelayedRequester(1)
    dq.get('https://google.com/')

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pytest
from requests import Request, Response

from api.utils.watermark import HEADERS, watermark


_MOCK_IMAGE_PATH = Path(__file__).parent / ".." / ".." / "factory"
_MOCK_IMAGE_BYTES = (_MOCK_IMAGE_PATH / "sample-image.jpg").read_bytes()
_MOCK_IMAGE_INFO = json.loads((_MOCK_IMAGE_PATH / "sample-image-info.json").read_text())


@dataclass
class RequestsFixture:
    requests: list[Request]
    response_factory: Callable[[Request], Response] = (  # noqa: E731
        lambda x: RequestsFixture._default_response_factory(x)
    )

    @staticmethod
    def _default_response_factory(req: Request) -> Response:
        res = Response()
        res.url = req.url
        res.status_code = 200
        res._content = _MOCK_IMAGE_BYTES
        return res


@pytest.fixture(autouse=True)
def requests(monkeypatch) -> RequestsFixture:
    fixture = RequestsFixture([])

    def requests_get(url, **kwargs):
        req = Request(method="GET", url=url, **kwargs)
        fixture.requests.append(req)
        response = fixture.response_factory(req)
        return response

    monkeypatch.setattr("requests.get", requests_get)

    return fixture


def test_sends_UA_header(requests):
    watermark("http://example.com/", _MOCK_IMAGE_INFO)

    assert len(requests.requests) > 0
    for r in requests.requests:
        assert r.headers == HEADERS


# Previously, wrapped titles would throw a TypeError:
# slice indices must be integers or None or have an __index__ method.
# See: https://github.com/WordPress/openverse/issues/2466
def test_long_title_wraps_correctly(requests):
    # Make the title 400 chars long
    _MOCK_IMAGE_INFO_LONG_TITLE = dict(_MOCK_IMAGE_INFO)
    _MOCK_IMAGE_INFO_LONG_TITLE["title"] = "a" * 400

    watermark("http://example.com/", _MOCK_IMAGE_INFO_LONG_TITLE)

    assert len(requests.requests) > 0
    for r in requests.requests:
        assert r.headers == HEADERS

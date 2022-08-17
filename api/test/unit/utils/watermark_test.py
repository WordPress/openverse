import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pytest
from requests import Request, Response

from catalog.api.utils.watermark import HEADERS, watermark


_MOCK_IMAGE_PATH = Path(__file__).parent / ".." / ".." / "factory"
_MOCK_IMAGE_BYTES = (_MOCK_IMAGE_PATH / "sample-image.jpg").read_bytes()
_MOCK_IMAGE_INFO = json.loads((_MOCK_IMAGE_PATH / "sample-image-info.json").read_text())


@dataclass
class RequestsFixture:
    requests: list[Request]
    response_factory: Callable[
        (Request,), Response
    ] = lambda x: RequestsFixture._default_response_factory(x)

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

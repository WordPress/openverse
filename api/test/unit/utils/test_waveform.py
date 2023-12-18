import json
from collections.abc import Callable
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import pytest
from requests import Request, Response
from requests.structures import CaseInsensitiveDict

from api.utils.waveform import UA_STRING, download_audio


_MOCK_AUDIO_PATH = Path(__file__).parent / ".." / ".." / "factory"
_MOCK_AUDIO_BYTES = (_MOCK_AUDIO_PATH / "sample-audio.mp3").read_bytes()
_MOCK_AUDIO_INFO = json.loads((_MOCK_AUDIO_PATH / "sample-audio-info.json").read_text())


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
        res.raw = BytesIO(_MOCK_AUDIO_BYTES)
        res.headers = CaseInsensitiveDict(_MOCK_AUDIO_INFO["headers"])
        return res


@pytest.fixture(autouse=True)
def requests(monkeypatch) -> RequestsFixture:
    fixture = RequestsFixture([])

    def requests_get(url, **kwargs):
        kwargs.pop("stream")
        req = Request(method="GET", url=url, **kwargs)
        fixture.requests.append(req)
        response = fixture.response_factory(req)
        return response

    monkeypatch.setattr("requests.get", requests_get)

    return fixture


def test_download_audio_sends_ua_header(requests):
    download_audio("http://example.org", "abcd-1234")

    assert len(requests.requests) > 0
    for r in requests.requests:
        assert r.headers["User-Agent"] == UA_STRING

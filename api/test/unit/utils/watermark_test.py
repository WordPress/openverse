import json
import struct
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Callable
from unittest import mock

import pytest
from PIL import Image
from requests import Request, Response

from catalog.api.utils.watermark import HEADERS, _open_image, watermark


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


def test_catch_struct_errors_from_piexif(requests):
    img_mock = Image.open(BytesIO(_MOCK_IMAGE_BYTES))
    img_mock.info["exif"] = "bad_info"

    with mock.patch("PIL.Image.open") as open_mock, mock.patch(
        "piexif.load"
    ) as load_mock:
        open_mock.return_value = img_mock
        load_mock.side_effect = struct.error("unpack requires a buffer of 2 bytes")

        img, exif = _open_image("http://example.com/")

    assert img is not None
    assert exif is None

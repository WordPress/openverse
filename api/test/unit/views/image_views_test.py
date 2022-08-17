import json
from dataclasses import dataclass
from pathlib import Path
from test.factory.models.image import ImageFactory
from typing import Callable

from rest_framework.test import APIClient

import pytest
from requests import Request, Response

from catalog.api.views.image_views import ImageViewSet


_MOCK_IMAGE_PATH = Path(__file__).parent / ".." / ".." / "factory"
_MOCK_IMAGE_BYTES = (_MOCK_IMAGE_PATH / "sample-image.jpg").read_bytes()
_MOCK_IMAGE_INFO = json.loads((_MOCK_IMAGE_PATH / "sample-image-info.json").read_text())


@pytest.fixture
def api_client():
    return APIClient()


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


@pytest.mark.django_db
def test_oembed_sends_ua_header(api_client, requests):
    image = ImageFactory.create()
    res = api_client.get("/v1/images/oembed/", data={"url": f"/{image.identifier}"})

    assert res.status_code == 200

    assert len(requests.requests) > 0
    for r in requests.requests:
        assert r.headers == ImageViewSet.OEMBED_HEADERS

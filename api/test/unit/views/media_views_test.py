import json
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from test.factory.models.audio import AudioFactory
from test.factory.models.image import ImageFactory
from unittest import mock
from unittest.mock import patch

from rest_framework.test import APIClient

import pytest
import requests as requests_lib
from fakeredis import FakeRedis
from requests import PreparedRequest, ReadTimeout, Request, Response

from catalog.api.views.media_views import MediaViewSet, UpstreamThumbnailException


_MOCK_IMAGE_PATH = Path(__file__).parent / ".." / ".." / "factory"
_MOCK_IMAGE_BYTES = (_MOCK_IMAGE_PATH / "sample-image.jpg").read_bytes()
_MOCK_IMAGE_INFO = json.loads((_MOCK_IMAGE_PATH / "sample-image-info.json").read_text())


@pytest.fixture
def api_client():
    return APIClient()


@dataclass
class SentRequest:
    request: PreparedRequest
    kwargs: dict


@dataclass
class RequestsFixture:
    sent_requests: list[SentRequest]
    send_handler: Callable[
        [Request], Response
    ] = lambda *args, **kwargs: RequestsFixture._default_send_handler(*args, **kwargs)
    response_queue: list[Response] = field(default_factory=list)

    @staticmethod
    def _default_send_handler(fixture, session, req, **kwargs) -> Response:
        if fixture.response_queue:
            return fixture.response_queue.pop()

        res = Response()
        res.url = req.url
        res.status_code = 200
        res._content = _MOCK_IMAGE_BYTES
        return res


@pytest.fixture(autouse=True)
def requests(monkeypatch) -> RequestsFixture:
    fixture = RequestsFixture([])

    def send(session, req, **kwargs):
        fixture.sent_requests.append(SentRequest(req, kwargs))
        response = fixture.send_handler(fixture, session, req, **kwargs)
        return response

    monkeypatch.setattr("requests.sessions.Session.send", send)

    return fixture


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("media_type", "media_factory"),
    (
        ("images", ImageFactory),
        ("audio", AudioFactory),
    ),
)
def test_thumb_error(api_client, media_type, media_factory, requests):
    error = None

    def send_handler(fixture, session, req, **kwargs):
        requests.sent_requests.append(SentRequest(req, kwargs))
        nonlocal error
        error = requests_lib.HTTPError(
            req.url, 503, "Bad error upstream whoops", {}, None
        )
        raise error

    requests.send_handler = send_handler

    with mock.patch(
        "catalog.api.views.media_views.capture_exception", autospec=True
    ) as mock_capture_exception:
        media = media_factory.create()
        response = api_client.get(f"/v1/{media_type}/{media.identifier}/thumb/")

    assert response.status_code == 424
    mock_capture_exception.assert_called_once_with(error)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("media_type", "media_factory"),
    (
        ("images", ImageFactory),
        ("audio", AudioFactory),
    ),
)
def test_thumb_sends_ua_header(api_client, media_type, media_factory, requests):
    media = media_factory.create()
    res = api_client.get(f"/v1/{media_type}/{media.identifier}/thumb/")

    assert res.status_code == 200

    assert len(requests.sent_requests) == 1
    assert (
        requests.sent_requests[0].request.headers["User-agent"]
        == MediaViewSet.THUMBNAIL_PROXY_COMM_HEADERS["User-Agent"]
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("media_type", "media_factory"),
    (
        ("images", ImageFactory),
        ("audio", AudioFactory),
    ),
)
def test_thumb(api_client, media_type, media_factory, requests):
    media = media_factory.create()
    res = api_client.get(f"/v1/{media_type}/{media.identifier}/thumb/")

    assert res.status_code == 200
    assert res.content == _MOCK_IMAGE_BYTES
    expected_upstream_params = {
        "quality=",
        "compression=",
        "width=600",
    }
    for entry in expected_upstream_params:
        assert (
            entry in requests.sent_requests[0].request.url
        ), f"{entry} not found in prepared request url: {requests.sent_requests[0].request.url}"


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("media_type", "media_factory"),
    (
        ("images", ImageFactory),
        ("audio", AudioFactory),
    ),
)
def test_thumb_compression(api_client, media_type, media_factory, requests):
    media = media_factory.create()
    res = api_client.get(
        f"/v1/{media_type}/{media.identifier}/thumb/", data={"compressed": "yes"}
    )

    assert res.status_code == 200
    expected_upstream_params = {
        # Don't encode the defaults here, just assert that these params
        # exist, but not with the uncompressed values in the rejected set below
        "quality=",
        "compression=",
    }
    rejected_params = {
        "quality=100",
        "compression=0",
    }
    for entry in expected_upstream_params:
        assert (
            entry in requests.sent_requests[0].request.url
        ), f"{entry} not found in prepared request url: {requests.sent_requests[0].request.url}"

    for entry in rejected_params:
        assert (
            entry not in requests.sent_requests[0].request.url
        ), f"Rejected {entry} found in prepared request url: {requests.sent_requests[0].request.url}"


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("media_type", "media_factory"),
    (
        ("images", ImageFactory),
        ("audio", AudioFactory),
    ),
)
def test_thumb_webp(api_client, media_type, media_factory, requests):
    media = media_factory.create()
    accept_header = "image/webp,image/*,*/*"
    res = api_client.get(
        f"/v1/{media_type}/{media.identifier}/thumb/", HTTP_ACCEPT=accept_header
    )

    assert res.status_code == 200
    expected_upstream_params = {"type=auto"}
    for entry in expected_upstream_params:
        assert (
            entry in requests.sent_requests[0].request.url
        ), f"{entry} not found in prepared request url: {requests.sent_requests[0].request.url}"

    assert ("accept", accept_header) in requests.sent_requests[
        0
    ].request.headers.lower_items()


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("media_type", "media_factory"),
    (
        ("images", ImageFactory),
        ("audio", AudioFactory),
    ),
)
def test_thumb_full_size(api_client, media_type, media_factory, requests):
    media = media_factory.create()

    upstream_width = 1200
    info_response = Response()
    info_response.status = 200
    info_response._content = json.dumps({"width": upstream_width}).encode()
    requests.response_queue = [info_response]

    res = api_client.get(
        f"/v1/{media_type}/{media.identifier}/thumb/", data={"full_size": "yes"}
    )

    assert res.status_code == 200
    rejected_params = {
        "width=600",
    }

    for entry in rejected_params:
        assert (
            entry not in requests.sent_requests[1].request.url
        ), f"Rejected {entry} found in prepared request url: {requests.sent_requests[0].request.url}"

    expected_params = {f"width={upstream_width}"}
    for entry in expected_params:
        assert (
            entry in requests.sent_requests[1].request.url
        ), f"{entry} not found in prepared request url: {requests.sent_requests[0].request.url}"


@pytest.fixture
def redis(monkeypatch) -> FakeRedis:
    fake_redis = FakeRedis()
    monkeypatch.setattr("catalog.api.views.media_views.cache", fake_redis)

    yield fake_redis

    fake_redis.client().close()


@pytest.mark.parametrize("count", [1, 3])
def test_thumb_timeout(redis, count: int):
    with patch("requests.get", side_effect=ReadTimeout()):
        for idx in range(count):
            with pytest.raises(UpstreamThumbnailException):
                MediaViewSet._thumbnail_proxy_comm(
                    "test", params={"url": f"https://example.com/image/{idx}"}
                )

    # Conversion to ``int`` required because of bug:
    # https://github.com/cunla/fakeredis-py/issues/58
    assert count == int(redis.get("thumbnail_timeout:example.com"))

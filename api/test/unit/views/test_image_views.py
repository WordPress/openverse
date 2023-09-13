import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from test.factory.models.image import ImageFactory

import pook
import pytest
from PIL import UnidentifiedImageError
from requests import Request, Response

from api.views.image_views import ImageViewSet


_MOCK_IMAGE_PATH = Path(__file__).parent / ".." / ".." / "factory"
_MOCK_IMAGE_BYTES = (_MOCK_IMAGE_PATH / "sample-image.jpg").read_bytes()
_MOCK_IMAGE_INFO = json.loads((_MOCK_IMAGE_PATH / "sample-image-info.json").read_text())


@dataclass
class RequestsFixture:
    requests: list[Request]
    response_factory: Callable[  # noqa: E731
        [Request], Response
    ] = lambda x: RequestsFixture._default_response_factory(x)

    @staticmethod
    def _default_response_factory(req: Request) -> Response:
        res = Response()
        res.url = req.url
        res.status_code = 200
        res._content = _MOCK_IMAGE_BYTES
        return res


@pytest.fixture
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


@pytest.mark.django_db
@pytest.mark.parametrize(
    "smk_has_thumb, expected_thumb_url",
    [(True, "http://iip.smk.dk/thumb.jpg"), (False, "http://iip.smk.dk/image.jpg")],
)
def test_thumbnail_uses_upstream_thumb_for_smk(
    api_client, smk_has_thumb, expected_thumb_url, settings
):
    thumb_url = "http://iip.smk.dk/thumb.jpg" if smk_has_thumb else None
    image = ImageFactory.create(
        url="http://iip.smk.dk/image.jpg",
        thumbnail=thumb_url,
    )
<<<<<<< HEAD
    with patch("api.views.media_views.MediaViewSet.thumbnail") as thumb_call:
        mock_response = HttpResponse("mock_response")
        thumb_call.return_value = mock_response
        api_client.get(f"/v1/images/{image.identifier}/thumb/")
    thumb_call.assert_called_once_with(ANY, image, expected_thumb_url)


@pytest.mark.django_db
def test_watermark_raises_424_for_invalid_image(api_client):
    image = ImageFactory.create()
    expected_error_message = (
        "cannot identify image file <_io.BytesIO object at 0xffff86d8fec0>"
    )

    with patch("PIL.Image.open") as mock_open:
        mock_open.side_effect = UnidentifiedImageError(expected_error_message)
        res = api_client.get(f"/v1/images/{image.identifier}/watermark/")
    assert res.status_code == 424
    assert res.data["detail"] == expected_error_message


@pytest.mark.django_db
def test_watermark_raises_424_for_404_image(api_client):
    image = ImageFactory.create()

    with patch("requests.get") as mock_get:
        mock_get.return_value = Response()
        mock_get.return_value.status_code = 404
        mock_get.return_value.url = image.url
        mock_get.return_value.reason = "Not Found"
        res = api_client.get(f"/v1/images/{image.identifier}/watermark/")
    assert res.status_code == 424
    assert res.data["detail"] == f"404 Client Error: Not Found for url: {image.url}"
=======

    with pook.use():
        mock_get = (
            # Pook interprets a trailing slash on the URL as the path,
            # so strip that so the `path` matcher works
            pook.get(settings.PHOTON_ENDPOINT[:-1])
            .path(expected_thumb_url.replace("http://", "/"))
            .response(200)
        ).mock

        response = api_client.get(f"/v1/images/{image.identifier}/thumb/")

    assert response.status_code == 200
    assert mock_get.matched is True
>>>>>>> dc44ee8b7 (Add ADRF and make the thumbnail view async)

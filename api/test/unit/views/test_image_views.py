import json
from pathlib import Path

import pook
import pytest

from api.views.image_views import ImageViewSet
from test.factory.models.image import ImageFactory


_MOCK_IMAGE_PATH = Path(__file__).parent / ".." / ".." / "factory"
_MOCK_IMAGE_BYTES = (_MOCK_IMAGE_PATH / "sample-image.jpg").read_bytes()
_MOCK_IMAGE_INFO = json.loads((_MOCK_IMAGE_PATH / "sample-image-info.json").read_text())


@pytest.mark.django_db
def test_oembed_sends_ua_header(api_client):
    image = ImageFactory.create()
    image.url = f"https://any.domain/any/path/{image.identifier}"
    image.save()

    with pook.use():
        (
            pook.get(image.url)
            .header("User-Agent", ImageViewSet.OEMBED_HEADERS["User-Agent"])
            .reply(200)
            .body(_MOCK_IMAGE_BYTES)
        )
        res = api_client.get("/v1/images/oembed/", data={"url": image.url})

    assert res.status_code == 200


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
        provider="smk",
        url="http://iip.smk.dk/image.jpg",
        thumbnail=thumb_url,
    )

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

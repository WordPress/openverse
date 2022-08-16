from test.factory.models.image import ImageFactory
from unittest import mock
from urllib.error import HTTPError

from rest_framework.test import APIClient

import pytest

from catalog.api.models.image import Image


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def image() -> Image:
    return ImageFactory.create()


@pytest.mark.django_db
def test_thumb_error(api_client, image):
    error = None

    def urlopen_503_response(url, **kwargs):
        nonlocal error
        error = HTTPError(url, 503, "Bad error upstream whoops", {}, None)
        raise error

    with mock.patch(
        "catalog.api.views.media_views.urlopen"
    ) as urlopen_mock, mock.patch(
        "catalog.api.views.media_views.capture_exception", autospec=True
    ) as mock_capture_exception:
        urlopen_mock.side_effect = urlopen_503_response
        response = api_client.get(f"/v1/images/{image.identifier}/thumb/")

    assert response.status_code == 424
    mock_capture_exception.assert_called_once_with(error)

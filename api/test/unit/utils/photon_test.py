from urllib.parse import urlencode

from django.conf import settings

import pook
import pytest
import requests

from catalog.api.utils.photon import HEADERS, UpstreamThumbnailException
from catalog.api.utils.photon import get as photon_get


PHOTON_URL_FOR_TEST_IMAGE = f"{settings.PHOTON_ENDPOINT}subdomain.example.com/path_part1/part2/image_dot_jpg.jpg"
TEST_IMAGE_URL = PHOTON_URL_FOR_TEST_IMAGE.replace(settings.PHOTON_ENDPOINT, "http://")

UA_HEADER = HEADERS["User-Agent"]

# cannot use actual image response because I kept running into some issue with
# requests not being able to decode the content
# I will come back to try to sort it out later but for now
# this will get the tests working.
MOCK_BODY = "mock response body"


@pytest.fixture
def auth_key():
    test_key = "this is a test Photon Key boop boop, let me in"
    settings.PHOTON_AUTH_KEY = test_key

    yield test_key

    settings.PHOTON_AUTH_KEY = None


@pook.on
def test_get_successful_no_auth_key_default_args(mock_image_data):
    mock_get: pook.Mock = (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .params(
            {
                "w": settings.THUMBNAIL_WIDTH_PX,
                "quality": settings.THUMBNAIL_QUALITY,
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
        .mock
    )

    res = photon_get(TEST_IMAGE_URL)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


@pook.on
def test_get_successful_with_auth_key_default_args(mock_image_data, auth_key):
    mock_get: pook.Mock = (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .params(
            {
                "w": settings.THUMBNAIL_WIDTH_PX,
                "quality": settings.THUMBNAIL_QUALITY,
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .header("X-Photon-Authentication", auth_key)
        .reply(200)
        .body(MOCK_BODY)
        .mock
    )

    res = photon_get(TEST_IMAGE_URL)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


@pook.on
def test_get_successful_no_auth_key_not_compressed(mock_image_data):
    mock_get: pook.Mock = (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .params(
            {
                "w": settings.THUMBNAIL_WIDTH_PX,
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
        .mock
    )

    res = photon_get(TEST_IMAGE_URL, is_compressed=False)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


@pook.on
def test_get_successful_no_auth_key_full_size(mock_image_data):
    mock_get: pook.Mock = (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .params(
            {
                "quality": settings.THUMBNAIL_QUALITY,
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
        .mock
    )

    res = photon_get(TEST_IMAGE_URL, is_full_size=True)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


@pook.on
def test_get_successful_no_auth_key_full_size_not_compressed(mock_image_data):
    mock_get: pook.Mock = (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
        .mock
    )

    res = photon_get(TEST_IMAGE_URL, is_full_size=True, is_compressed=False)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


@pook.on
def test_get_successful_no_auth_key_png_only(mock_image_data):
    mock_get: pook.Mock = (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .params(
            {
                "w": settings.THUMBNAIL_WIDTH_PX,
                "quality": settings.THUMBNAIL_QUALITY,
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/png")
        .reply(200)
        .body(MOCK_BODY)
        .mock
    )

    res = photon_get(TEST_IMAGE_URL, accept_header="image/png")

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


@pook.on
def test_get_successful_forward_query_params(mock_image_data):
    params = urlencode({"hello": "world", 1: 2, "beep": "boop"})
    mock_get: pook.Mock = (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .params(
            {
                "w": settings.THUMBNAIL_WIDTH_PX,
                "quality": settings.THUMBNAIL_QUALITY,
                "q": params,
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
        .mock
    )

    url_with_params = f"{TEST_IMAGE_URL}?{params}"

    res = photon_get(url_with_params)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


@pytest.fixture
def setup_requests_get_exception(monkeypatch):
    def do(exc):
        def raise_exc(*args, **kwargs):
            raise exc

        monkeypatch.setattr("requests.get", raise_exc)

    yield do


def test_get_timeout_no_existing_cache_key(
    capture_exception, setup_requests_get_exception, redis
):
    exc = requests.ReadTimeout()
    setup_requests_get_exception(exc)

    with pytest.raises(UpstreamThumbnailException):
        photon_get(TEST_IMAGE_URL)

    capture_exception.assert_called_once_with(exc)

    key = f"{settings.THUMBNAIL_TIMEOUT_PREFIX}subdomain.example.com"
    assert redis.get(key) == b"1"


def test_get_timeout_existing_cache_key(
    capture_exception, setup_requests_get_exception, redis
):
    exc = requests.ReadTimeout()
    setup_requests_get_exception(exc)
    key = f"{settings.THUMBNAIL_TIMEOUT_PREFIX}subdomain.example.com"
    redis.set(key, 5)

    with pytest.raises(UpstreamThumbnailException, match=r"due to timeout"):
        photon_get(TEST_IMAGE_URL)

    capture_exception.assert_called_once_with(exc)

    assert redis.get(key) == b"6"


@pytest.mark.parametrize(
    "exception, expected_message",
    [
        (  # Includes HTTP response errors
            requests.RequestException(),
            r"Failed to render thumbnail.",
        ),
        (ValueError(), r"due to unidentified exception."),
    ],
)
def test_get_raise_exception_msg(
    capture_exception, setup_requests_get_exception, exception, expected_message
):
    setup_requests_get_exception(exception)

    with pytest.raises(UpstreamThumbnailException, match=expected_message):
        photon_get(TEST_IMAGE_URL)

    capture_exception.assert_called_once_with(exception)


@pook.on
def test_get_successful_https_image_url_sends_ssl_parameter(mock_image_data):
    https_url = TEST_IMAGE_URL.replace("http://", "https://")
    mock_get: pook.Mock = (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .params(
            {
                "w": settings.THUMBNAIL_WIDTH_PX,
                "quality": settings.THUMBNAIL_QUALITY,
                "ssl": "true",
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
        .mock
    )

    res = photon_get(https_url)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched

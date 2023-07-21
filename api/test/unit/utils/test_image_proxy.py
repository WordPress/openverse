from test.factory.models.image import ImageFactory
from unittest.mock import MagicMock
from urllib.parse import urlencode
from uuid import uuid4

from django.conf import settings
from rest_framework.exceptions import UnsupportedMediaType

import aiohttp
import pook
import pytest
import requests
from asgiref.sync import sync_to_async

from api.utils.image_proxy import HEADERS, UpstreamThumbnailException, extension
from api.utils.image_proxy import get as photon_get
from api.utils.tallies import get_monthly_timestamp


TEST_MEDIA_IDENTIFIER = "123"

UA_HEADER = HEADERS["User-Agent"]

# cannot use actual image response because I kept running into some issue with
# requests not being able to decode the content
# I will come back to try to sort it out later but for now
# this will get the tests working.
MOCK_BODY = "mock response body"

SVG_BODY = """<?xml version="1.0" encoding="UTF-8"?>
<svg version="1.1" xmlns="http://www.w3.org/2000/svg">
<text x="10" y="10" fill="white">SVG</text>
</svg>"""


@pytest.fixture
def photon_url():
    return f"{settings.PHOTON_ENDPOINT}subdomain.example.com/path_part1/part2/{uuid4()}.jpg"


@pytest.fixture
def image_url(photon_url):
    return photon_url.replace(settings.PHOTON_ENDPOINT, "http://")


@pytest.fixture
def auth_key():
    test_key = "this is a test Photon Key boop boop, let me in"
    settings.PHOTON_AUTH_KEY = test_key

    yield test_key

    settings.PHOTON_AUTH_KEY = None


@pytest.fixture
def pook_on():
    """
    Safely turn pook on and off for a test.

    pytest mark's in general mess with the `pook.on`
    decorator, so this is a workaround that prevents
    individual tests needing to safely handle clean up.
    """
    pook.on()
    yield
    pook.off()


@pytest.fixture
def pook_off():
    """
    Turn pook off after a test.

    Useful to ensure pook is turned off after a test
    if you need to manually turn pook on (for example,
    to avoid it capturing requests you actually do
    want to send).
    """
    yield
    pook.off()


async def test_get_successful_no_auth_key_default_args(
    photon_url, image_url, pook_on, mock_image_data
):
    mock_get: pook.Mock = (
        pook.get(photon_url)
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

    res = await photon_get(image_url, TEST_MEDIA_IDENTIFIER)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


async def test_get_successful_original_svg_no_auth_key_default_args(
    image_url, pook_on, mock_image_data
):
    mock_get: pook.Mock = (
        pook.get(image_url.replace(".jpg", ".svg"))
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(SVG_BODY)
        .mock
    )

    res = await photon_get(image_url.replace(".jpg", ".svg"), TEST_MEDIA_IDENTIFIER)

    assert res.content == SVG_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


async def test_get_successful_with_auth_key_default_args(
    image_url, photon_url, pook_on, mock_image_data, auth_key
):
    mock_get: pook.Mock = (
        pook.get(photon_url)
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

    res = await photon_get(image_url, TEST_MEDIA_IDENTIFIER)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


async def test_get_successful_no_auth_key_not_compressed(
    image_url, photon_url, pook_on, mock_image_data
):
    mock_get: pook.Mock = (
        pook.get(photon_url)
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

    res = await photon_get(image_url, TEST_MEDIA_IDENTIFIER, is_compressed=False)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


async def test_get_successful_no_auth_key_full_size(
    image_url, photon_url, pook_on, mock_image_data
):
    mock_get: pook.Mock = (
        pook.get(photon_url)
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

    res = await photon_get(image_url, TEST_MEDIA_IDENTIFIER, is_full_size=True)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


async def test_get_successful_no_auth_key_full_size_not_compressed(
    image_url, photon_url, pook_on, mock_image_data
):
    mock_get: pook.Mock = (
        pook.get(photon_url)
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
        .mock
    )

    res = await photon_get(
        image_url, TEST_MEDIA_IDENTIFIER, is_full_size=True, is_compressed=False
    )

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


async def test_get_successful_no_auth_key_png_only(
    image_url, photon_url, pook_on, mock_image_data
):
    mock_get: pook.Mock = (
        pook.get(photon_url)
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

    res = await photon_get(image_url, TEST_MEDIA_IDENTIFIER, accept_header="image/png")

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


async def test_get_successful_forward_query_params(
    image_url, photon_url, pook_on, mock_image_data
):
    params = urlencode({"hello": "world", 1: 2, "beep": "boop"})
    mock_get: pook.Mock = (
        pook.get(photon_url)
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

    url_with_params = f"{image_url}?{params}"

    res = await photon_get(url_with_params, TEST_MEDIA_IDENTIFIER)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


@pytest.fixture
def setup_http_get_exception(monkeypatch):
    def do(exc):
        mock_session = MagicMock(spec=aiohttp.ClientSession)
        mock_session.get.side_effect = exc

        monkeypatch.setattr(
            "api.utils.image_proxy.get_aiohttp_session", lambda: mock_session
        )

    yield do


async def test_get_successful_records_response_code(
    image_url, photon_url, pook_on, mock_image_data, redis
):
    (
        pook.get(photon_url)
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

    await photon_get(image_url, TEST_MEDIA_IDENTIFIER)
    month = get_monthly_timestamp()
    assert redis.get(f"thumbnail_response_code:{month}:200") == b"1"
    assert (
        redis.get(
            f"thumbnail_response_code_by_domain:subdomain.example.com:{month}:200"
        )
        == b"1"
    )


alert_count_params = pytest.mark.parametrize(
    "count_start, should_alert",
    [
        (0, True),
        (1, True),
        (50, True),
        (99, True),
        (100, False),
        (999, True),
        (1000, False),
        (1500, False),
        (1999, True),
    ],
)


@pytest.mark.parametrize(
    "exc, exc_name",
    [
        (ValueError("whoops"), "builtins.ValueError"),
        (requests.ConnectionError("whoops"), "requests.exceptions.ConnectionError"),
        (requests.ConnectTimeout("whoops"), "requests.exceptions.ConnectTimeout"),
        (requests.ReadTimeout("whoops"), "requests.exceptions.ReadTimeout"),
        (requests.Timeout("whoops"), "requests.exceptions.Timeout"),
        (requests.exceptions.SSLError("whoops"), "requests.exceptions.SSLError"),
        (OSError("whoops"), "builtins.OSError"),
    ],
)
@alert_count_params
async def test_get_exception_handles_error(
    exc,
    image_url,
    exc_name,
    count_start,
    should_alert,
    capture_exception,
    setup_http_get_exception,
    redis,
):
    setup_http_get_exception(exc)
    month = get_monthly_timestamp()
    key = f"thumbnail_error:{exc_name}:subdomain.example.com:{month}"
    redis.set(key, count_start)

    with pytest.raises(UpstreamThumbnailException):
        await photon_get(image_url, TEST_MEDIA_IDENTIFIER)

    assert_func = (
        capture_exception.assert_called_once
        if should_alert
        else capture_exception.assert_not_called
    )
    assert_func()
    assert redis.get(key) == str(count_start + 1).encode()


@alert_count_params
@pytest.mark.parametrize(
    "status_code, text",
    [
        (400, "Bad Request"),
        (401, "Unauthorized"),
        (403, "Forbidden"),
        (500, "Internal Server Error"),
    ],
)
async def test_get_http_exception_handles_error(
    status_code,
    text,
    count_start,
    should_alert,
    capture_exception,
    setup_http_get_exception,
    image_url,
    redis,
):
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = status_code
    mock_response.text = text
    exc = requests.HTTPError(response=mock_response)
    setup_http_get_exception(exc)

    month = get_monthly_timestamp()
    key = f"thumbnail_error:requests.exceptions.HTTPError:subdomain.example.com:{month}"
    redis.set(key, count_start)

    with pytest.raises(UpstreamThumbnailException):
        await photon_get(image_url, TEST_MEDIA_IDENTIFIER)

    assert_func = (
        capture_exception.assert_called_once
        if should_alert
        else capture_exception.assert_not_called
    )
    assert_func()
    assert redis.get(key) == str(count_start + 1).encode()

    # Assertions about the HTTP error specific message
    assert (
        redis.get(
            f"thumbnail_http_error:subdomain.example.com:{month}:{status_code}:{text}"
        )
        == b"1"
    )


async def test_get_successful_https_image_url_sends_ssl_parameter(
    image_url, photon_url, pook_on, mock_image_data
):
    https_url = image_url.replace("http://", "https://")
    mock_get: pook.Mock = (
        pook.get(photon_url)
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

    res = await photon_get(https_url, TEST_MEDIA_IDENTIFIER)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


async def test_get_unsuccessful_request_raises_custom_exception(
    image_url, photon_url, pook_on
):
    mock_get: pook.Mock = pook.get(photon_url).reply(404).mock

    with pytest.raises(
        UpstreamThumbnailException, match=r"Failed to render thumbnail."
    ):
        await photon_get(image_url, TEST_MEDIA_IDENTIFIER)

    assert mock_get.matched


@pytest.mark.parametrize(
    "image_url, expected_ext",
    [
        ("example.com/image.jpg", "jpg"),
        ("www.example.com/image.JPG", "jpg"),
        ("http://example.com/image.jpeg", "jpeg"),
        ("https://subdomain.example.com/image.svg", "svg"),
        ("https://example.com/image.png?foo=1&bar=2#fragment", "png"),
        ("https://example.com/possibleimagewithoutext", ""),
        (
            "https://iip.smk.dk/iiif/jp2/kksgb22133.tif.jp2/full/!400,/0/default.jpg",
            "jpg",
        ),
    ],
)
def test__get_extension_from_url(image_url, expected_ext):
    assert extension._get_file_extension_from_url(image_url) == expected_ext


@pytest.mark.django_db
@pytest.mark.parametrize("image_type", ["apng", "tiff", "bmp"])
async def test_photon_get_raises_by_not_allowed_types(image_url, image_type):
    image_url = image_url.replace(".jpg", f".{image_type}")
    image = await sync_to_async(ImageFactory.create)(url=image_url)

    with pytest.raises(UnsupportedMediaType):
        await photon_get(image_url, image.identifier)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "headers, expected_cache_val",
    [
        ({"Content-Type": "image/tiff"}, b"tiff"),
        (None, b"unknown"),
    ],
)
async def test_photon_get_saves_image_type_to_cache(
    pook_off, image_url, redis, headers, expected_cache_val
):
    image_url = image_url.replace(".jpg", "")
    image = await sync_to_async(ImageFactory.create)(url=image_url)

    pook.on()
    mock_head = pook.head(image_url).reply(200)
    if headers:
        mock_head = mock_head.headers(headers)

    with pytest.raises(UnsupportedMediaType):
        await photon_get(image_url, image.identifier)

    key = f"media:{image.identifier}:thumb_type"
    assert redis.get(key) == expected_cache_val

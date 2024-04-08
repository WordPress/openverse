import asyncio
from dataclasses import replace
from urllib.parse import urlencode

from django.conf import settings
from rest_framework.exceptions import UnsupportedMediaType

import aiohttp
import pook
import pytest
from aiohttp import client_exceptions
from aiohttp.client_reqrep import ConnectionKey

from api.utils.image_proxy import (
    HEADERS,
    MediaInfo,
    RequestConfig,
    UpstreamThumbnailException,
    extension,
)
from api.utils.image_proxy import get as _photon_get
from api.utils.tallies import get_monthly_timestamp
from test.factory.models.image import ImageFactory


TEST_IMAGE_DOMAIN = "subdomain.example.com"
PHOTON_URL_FOR_TEST_IMAGE = (
    f"{settings.PHOTON_ENDPOINT}{TEST_IMAGE_DOMAIN}/path_part1/part2/image_dot_jpg.jpg"
)
TEST_IMAGE_URL = PHOTON_URL_FOR_TEST_IMAGE.replace(settings.PHOTON_ENDPOINT, "http://")
TEST_MEDIA_IDENTIFIER = "123"
TEST_MEDIA_PROVIDER = "foo"

TEST_MEDIA_INFO = MediaInfo(
    media_identifier=TEST_MEDIA_IDENTIFIER,
    media_provider=TEST_MEDIA_PROVIDER,
    image_url=TEST_IMAGE_URL,
)

UA_HEADER = HEADERS["User-Agent"]

MOCK_BODY = "mock response body"

SVG_BODY = """<?xml version="1.0" encoding="UTF-8"?>
<svg version="1.1" xmlns="http://www.w3.org/2000/svg">
<text x="10" y="10" fill="white">SVG</text>
</svg>"""


cache_availability_params = pytest.mark.parametrize(
    "is_cache_reachable, cache_name",
    [(True, "redis"), (False, "unreachable_redis")],
)
# This parametrize decorator runs the test function with two scenarios:
# - one where the API can connect to Redis
# - one where it cannot and raises ``ConnectionError``
# The fixtures referenced here are defined below.


@pytest.fixture
def auth_key():
    test_key = "this is a test Photon Key boop boop, let me in"
    settings.PHOTON_AUTH_KEY = test_key

    yield test_key

    settings.PHOTON_AUTH_KEY = None


@pytest.fixture
def photon_get(session_loop):
    """Run ``image_proxy.get`` and wait for all tasks to finish."""

    def do(*args, **kwargs):
        try:
            res = session_loop.run_until_complete(_photon_get(*args, **kwargs))
            return res
        finally:
            tasks = asyncio.all_tasks(session_loop)
            for task in tasks:
                session_loop.run_until_complete(task)

    yield do


@pook.on
def test_get_successful_no_auth_key_default_args(photon_get, mock_image_data):
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

    res = photon_get(TEST_MEDIA_INFO)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


@pook.on
def test_get_successful_original_svg_no_auth_key_default_args(
    photon_get, mock_image_data
):
    mock_get: pook.Mock = (
        pook.get(TEST_IMAGE_URL.replace(".jpg", ".svg"))
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(SVG_BODY)
        .mock
    )

    media_info = replace(
        TEST_MEDIA_INFO, image_url=TEST_MEDIA_INFO.image_url.replace(".jpg", ".svg")
    )

    res = photon_get(media_info)

    assert res.content == SVG_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


@pook.on
def test_get_successful_with_auth_key_default_args(
    photon_get, mock_image_data, auth_key
):
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

    res = photon_get(TEST_MEDIA_INFO)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


@pook.on
def test_get_successful_no_auth_key_not_compressed(photon_get, mock_image_data):
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

    res = photon_get(TEST_MEDIA_INFO, RequestConfig(is_compressed=False))

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


@pook.on
def test_get_successful_no_auth_key_full_size(photon_get, mock_image_data):
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

    res = photon_get(TEST_MEDIA_INFO, RequestConfig(is_full_size=True))

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


@pook.on
def test_get_successful_no_auth_key_full_size_not_compressed(
    photon_get, mock_image_data
):
    mock_get: pook.Mock = (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
        .mock
    )

    res = photon_get(
        TEST_MEDIA_INFO,
        RequestConfig(is_full_size=True, is_compressed=False),
    )

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


@pook.on
def test_get_successful_no_auth_key_png_only(photon_get, mock_image_data):
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

    res = photon_get(TEST_MEDIA_INFO, RequestConfig(accept_header="image/png"))

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


@pook.on
def test_get_successful_forward_query_params(photon_get, mock_image_data):
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

    media_info_with_url_params = replace(
        TEST_MEDIA_INFO, image_url=f"{TEST_IMAGE_URL}?{params}"
    )

    res = photon_get(media_info_with_url_params)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


@pytest.fixture
def setup_request_exception(monkeypatch):
    def do(exc):
        async def raise_exc(*args, **kwargs):
            raise exc

        monkeypatch.setattr(aiohttp.ClientSession, "get", raise_exc)

    yield do


@pook.on
@cache_availability_params
def test_get_successful_records_response_code(
    photon_get, mock_image_data, is_cache_reachable, cache_name, request, caplog
):
    cache = request.getfixturevalue(cache_name)
    (
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
    )

    photon_get(TEST_MEDIA_INFO)
    month = get_monthly_timestamp()

    keys = [
        f"thumbnail_response_code:{month}:200",
        f"thumbnail_response_code_by_domain:{TEST_IMAGE_DOMAIN}:{month}:200",
    ]
    if is_cache_reachable:
        for key in keys:
            assert cache.get(key) == b"1"
    else:
        assert (
            "Redis connect failed, thumbnail response codes not tallied." in caplog.text
        )


alert_count_params = pytest.mark.parametrize(
    "count_start",
    [0, 1, 999],
)

MOCK_CONNECTION_KEY = ConnectionKey(
    host="https://localhost",
    port=None,
    is_ssl=False,
    ssl=None,
    proxy=None,
    proxy_auth=None,
    proxy_headers_hash=None,
)


@pytest.mark.parametrize(
    "exc, exc_name",
    [
        (ValueError("whoops"), "builtins.ValueError"),
        (
            client_exceptions.ClientConnectionError("whoops"),
            "aiohttp.client_exceptions.ClientConnectionError",
        ),
        (
            client_exceptions.ServerTimeoutError("whoops"),
            "aiohttp.client_exceptions.ServerTimeoutError",
        ),
        (
            client_exceptions.ClientSSLError(MOCK_CONNECTION_KEY, OSError()),
            "aiohttp.client_exceptions.ClientSSLError",
        ),
        (
            client_exceptions.ClientOSError("whoops"),
            "aiohttp.client_exceptions.ClientOSError",
        ),
    ],
)
@cache_availability_params
@alert_count_params
def test_get_exception_handles_error(
    photon_get,
    exc,
    exc_name,
    count_start,
    sentry_capture_exception,
    setup_request_exception,
    is_cache_reachable,
    cache_name,
    request,
    caplog,
):
    cache = request.getfixturevalue(cache_name)

    setup_request_exception(exc)
    month = get_monthly_timestamp()
    key = f"thumbnail_error:{exc_name}:{TEST_IMAGE_DOMAIN}:{month}"
    if is_cache_reachable:
        cache.set(key, count_start)

    with pytest.raises(UpstreamThumbnailException):
        photon_get(TEST_MEDIA_INFO)

    sentry_capture_exception.assert_not_called()

    if is_cache_reachable:
        assert cache.get(key) == str(count_start + 1).encode()
    else:
        assert "Redis connect failed, thumbnail errors not tallied." in caplog.text


@cache_availability_params
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
def test_get_http_exception_handles_error(
    photon_get,
    status_code,
    text,
    count_start,
    sentry_capture_exception,
    is_cache_reachable,
    cache_name,
    request,
    caplog,
):
    cache = request.getfixturevalue(cache_name)

    month = get_monthly_timestamp()
    key = f"thumbnail_error:aiohttp.client_exceptions.ClientResponseError:{TEST_IMAGE_DOMAIN}:{month}"
    if is_cache_reachable:
        cache.set(key, count_start)

    with pytest.raises(UpstreamThumbnailException):
        with pook.use():
            pook.get(PHOTON_URL_FOR_TEST_IMAGE).reply(status_code, text)
            photon_get(TEST_MEDIA_INFO)

    sentry_capture_exception.assert_not_called()

    if is_cache_reachable:
        assert cache.get(key) == str(count_start + 1).encode()
        assert (
            cache.get(f"thumbnail_http_error:{TEST_IMAGE_DOMAIN}:{month}:{status_code}")
            == b"1"
        )
    else:
        assert all(
            message in caplog.text
            for message in [
                "Redis connect failed, thumbnail HTTP errors not tallied.",
                "Redis connect failed, thumbnail errors not tallied.",
            ]
        )


@pook.on
def test_get_successful_https_image_url_sends_ssl_parameter(
    photon_get, mock_image_data
):
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

    https_media_info = replace(TEST_MEDIA_INFO, image_url=https_url)

    res = photon_get(https_media_info)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200
    assert mock_get.matched


@pook.on
def test_get_unsuccessful_request_raises_custom_exception(photon_get):
    mock_get: pook.Mock = pook.get(PHOTON_URL_FOR_TEST_IMAGE).reply(404).mock

    with pytest.raises(
        UpstreamThumbnailException, match=r"Failed to render thumbnail."
    ):
        photon_get(TEST_MEDIA_INFO)

    assert mock_get.matched


@pytest.mark.parametrize(
    "image_url, expected_ext",
    [
        ("example.com/image.jpg", "jpg"),
        ("www.example.com/image.JPG", "jpg"),
        ("http://example.com/image.jpeg", "jpeg"),
        ("https://example.com/image.svg", "svg"),
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

@pytest.mark.parametrize(
    "content_type","expected_ext",
    [
        ("image/jpeg", ".jpeg"),
        ("image/png", ".png"),
        ("image/gif", ".gif"),
        ("image/svg+xml", ".svg"),
        ("audio/midi", ".mid"),
        ("audio/mpeg", ".mp3"),
        ("audio/ogg", ".oga"),
        ("application/ogg", ".ogx"),
        ("audio/opus", ".opus"),
        ("audio/wav",".wav"),
        ("video/webm", ".webm")
    ]
)
def test_get_extension_from_content_type(content_type, expected_ext):
    assert extension._get_file_extension_from_content_type(content_type) == expected_ext

@pytest.mark.django_db
@pytest.mark.parametrize("image_type", ["apng", "tiff", "bmp"])
def test_photon_get_raises_by_not_allowed_types(photon_get, image_type):
    image_url = TEST_IMAGE_URL.replace(".jpg", f".{image_type}")
    image = ImageFactory.create(url=image_url)
    media_info = MediaInfo(
        media_identifier=image.identifier,
        media_provider=image.provider,
        image_url=image_url,
    )

    with pytest.raises(UnsupportedMediaType):
        photon_get(media_info)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "headers, expected_cache_val",
    [
        ({"Content-Type": "image/tiff"}, b"tiff"),
        ({"Content-Type": "unknown"}, b"unknown"),
    ],
)
@cache_availability_params
def test_photon_get_saves_image_type_to_cache(
    photon_get,
    headers,
    expected_cache_val,
    is_cache_reachable,
    cache_name,
    request,
    caplog,
):
    cache = request.getfixturevalue(cache_name)

    image_url = TEST_IMAGE_URL.replace(".jpg", "")
    image = ImageFactory.create(url=image_url)
    media_info = MediaInfo(
        media_identifier=image.identifier,
        media_provider=image.provider,
        image_url=image_url,
    )
    with pook.use():
        pook.head(image_url, reply=200, response_headers=headers)
        with pytest.raises(UnsupportedMediaType):
            photon_get(media_info)

    key = f"media:{image.identifier}:thumb_type"
    if is_cache_reachable:
        assert cache.get(key) == expected_cache_val
    else:
        assert all(
            message in caplog.text
            for message in [
                "Redis connect failed, cannot get cached image extension.",
                "Redis connect failed, cannot cache image extension.",
            ]
        )

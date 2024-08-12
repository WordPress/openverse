from dataclasses import replace
from urllib.parse import urlencode
from uuid import uuid4

from django.conf import settings
from rest_framework.exceptions import UnsupportedMediaType

import aiohttp
import pook
import pytest
from aiohttp import client_exceptions
from aiohttp.client_reqrep import ConnectionKey
from asgiref.sync import async_to_sync
from structlog.testing import capture_logs

from api.utils.image_proxy import (
    FAILURE_CACHE_KEY_TEMPLATE,
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
TEST_MEDIA_IDENTIFIER = uuid4()
TEST_MEDIA_PROVIDER = "foo"

# pook assets the params are passed matching type, so `'600' != 600`
# this is a bug in pook, but we need to handle it here anyway
# otherwise we would need to adjust the runtime code to account for
# this testing oddity
THUMBNAIL_WIDTH_PARAM = str(settings.THUMBNAIL_WIDTH_PX)

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


# Do not convert tests to async, because of this issue:
# https://github.com/pytest-dev/pytest-django/issues/580
# While the transaction workaround technically works, it is
# tedious, easy to forget, and just wrapping tested functions
# with async_to_sync is much easier
photon_get = async_to_sync(_photon_get)


@pytest.mark.pook
def test_get_successful_no_auth_key_default_args(mock_image_data):
    (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .params(
            {
                "w": THUMBNAIL_WIDTH_PARAM,
                "quality": settings.THUMBNAIL_QUALITY,
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
    )

    res = photon_get(TEST_MEDIA_INFO)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200


@pytest.mark.pook
def test_get_successful_original_svg_no_auth_key_default_args(mock_image_data):
    (
        pook.get(TEST_IMAGE_URL.replace(".jpg", ".svg"))
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(SVG_BODY)
    )

    media_info = replace(
        TEST_MEDIA_INFO, image_url=TEST_MEDIA_INFO.image_url.replace(".jpg", ".svg")
    )

    res = photon_get(media_info)

    assert res.content == SVG_BODY.encode()
    assert res.status_code == 200


@pytest.mark.pook
def test_get_successful_with_auth_key_default_args(mock_image_data, auth_key):
    (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .params(
            {
                "w": THUMBNAIL_WIDTH_PARAM,
                "quality": settings.THUMBNAIL_QUALITY,
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .header("X-Photon-Authentication", auth_key)
        .reply(200)
        .body(MOCK_BODY)
    )

    res = photon_get(TEST_MEDIA_INFO)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200


@pytest.mark.pook
def test_get_successful_no_auth_key_not_compressed(mock_image_data):
    (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .params(
            {
                "w": THUMBNAIL_WIDTH_PARAM,
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
    )

    res = photon_get(TEST_MEDIA_INFO, RequestConfig(is_compressed=False))

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200


@pytest.mark.pook
def test_get_successful_no_auth_key_full_size(mock_image_data):
    (
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
    )

    res = photon_get(TEST_MEDIA_INFO, RequestConfig(is_full_size=True))

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200


@pytest.mark.pook
def test_get_successful_no_auth_key_full_size_not_compressed(mock_image_data):
    (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
    )

    res = photon_get(
        TEST_MEDIA_INFO,
        RequestConfig(is_full_size=True, is_compressed=False),
    )

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200


@pytest.mark.pook
def test_get_successful_no_auth_key_png_only(mock_image_data):
    (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .params(
            {
                "w": THUMBNAIL_WIDTH_PARAM,
                "quality": settings.THUMBNAIL_QUALITY,
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/png")
        .reply(200)
        .body(MOCK_BODY)
    )

    res = photon_get(TEST_MEDIA_INFO, RequestConfig(accept_header="image/png"))

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200


@pytest.mark.pook
def test_get_successful_forward_query_params(mock_image_data):
    params = urlencode({"hello": "world", 1: 2, "beep": "boop"})
    (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .params(
            {
                "w": THUMBNAIL_WIDTH_PARAM,
                "quality": settings.THUMBNAIL_QUALITY,
                "q": params,
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
    )

    media_info_with_url_params = replace(
        TEST_MEDIA_INFO, image_url=f"{TEST_IMAGE_URL}?{params}"
    )

    res = photon_get(media_info_with_url_params)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200


@pytest.fixture
def setup_request_exception(monkeypatch):
    def do(exc):
        async def raise_exc(*args, **kwargs):
            raise exc

        monkeypatch.setattr(aiohttp.ClientSession, "get", raise_exc)

    yield do


@pytest.mark.pook
@cache_availability_params
def test_get_successful_records_response_code(
    mock_image_data, is_cache_reachable, cache_name, request
):
    cache = request.getfixturevalue(cache_name)
    (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .params(
            {
                "w": THUMBNAIL_WIDTH_PARAM,
                "quality": settings.THUMBNAIL_QUALITY,
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
    )

    with capture_logs() as cap_logs:
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
        messages = [record["event"] for record in cap_logs]
        assert "Redis connect failed, thumbnail response codes not tallied." in messages


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
    exc,
    exc_name,
    count_start,
    sentry_capture_exception,
    setup_request_exception,
    is_cache_reachable,
    cache_name,
    request,
):
    cache = request.getfixturevalue(cache_name)

    setup_request_exception(exc)
    month = get_monthly_timestamp()
    key = f"thumbnail_error:{exc_name}:{TEST_IMAGE_DOMAIN}:{month}"
    if is_cache_reachable:
        cache.set(key, count_start)

    with capture_logs() as cap_logs, pytest.raises(UpstreamThumbnailException):
        photon_get(TEST_MEDIA_INFO)

    sentry_capture_exception.assert_not_called()

    if is_cache_reachable:
        assert cache.get(key) == str(count_start + 1).encode()
    else:
        messages = [record["event"] for record in cap_logs]
        assert "Redis connect failed, thumbnail errors not tallied." in messages


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
@pytest.mark.pook
def test_get_http_exception_handles_error(
    status_code,
    text,
    count_start,
    sentry_capture_exception,
    is_cache_reachable,
    cache_name,
    request,
):
    cache = request.getfixturevalue(cache_name)

    month = get_monthly_timestamp()
    key = f"thumbnail_error:aiohttp.client_exceptions.ClientResponseError:{TEST_IMAGE_DOMAIN}:{month}"
    if is_cache_reachable:
        cache.set(key, count_start)

    with capture_logs() as cap_logs, pytest.raises(UpstreamThumbnailException):
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
        messages = [record["event"] for record in cap_logs]
        assert all(
            message in messages
            for message in [
                "Redis connect failed, thumbnail HTTP errors not tallied.",
                "Redis connect failed, thumbnail errors not tallied.",
            ]
        )


@pytest.mark.pook
def test_caches_failures_if_cache_surpasses_tolerance(mock_image_data, settings, redis):
    tolerance = settings.THUMBNAIL_FAILURE_CACHE_TOLERANCE = 2

    (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .params(
            {
                "w": THUMBNAIL_WIDTH_PARAM,
                "quality": settings.THUMBNAIL_QUALITY,
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .times(tolerance + 1)
        .reply(401)
        .body(MOCK_BODY)
    )

    for _ in range(tolerance + 1):
        with pytest.raises(
            UpstreamThumbnailException, match="Failed to render thumbnail"
        ):
            photon_get(TEST_MEDIA_INFO)

        assert (
            redis.ttl(
                FAILURE_CACHE_KEY_TEMPLATE.format(
                    ident=str(TEST_MEDIA_INFO.media_identifier).replace("-", "")
                )
            )
            is not None
        )

    with pytest.raises(
        UpstreamThumbnailException, match="Thumbnail unavailable from provider"
    ):
        photon_get(TEST_MEDIA_INFO)


@pytest.mark.pook
def test_caches_failures_with_successes_extending_tolerance(
    mock_image_data, settings, redis
):
    settings.THUMBNAIL_FAILURE_CACHE_TOLERANCE = 1

    def _make_failed_request():
        (pook.get(PHOTON_URL_FOR_TEST_IMAGE).reply(401))

        with pytest.raises(
            UpstreamThumbnailException, match="Failed to render thumbnail"
        ):
            photon_get(TEST_MEDIA_INFO)

    def _make_successful_request():
        (pook.get(PHOTON_URL_FOR_TEST_IMAGE).reply(200).body(MOCK_BODY))

        res = photon_get(TEST_MEDIA_INFO)
        assert res.content == MOCK_BODY.encode()

    # Before any requests, count = 0, within tolerance

    _make_failed_request()
    # count = 1, maximum within tolerance

    _make_successful_request()
    # count = 0, decremented due to successful request, allow additional failures before bypassing

    _make_failed_request()
    # count = 1 again, maximum within tolerance

    _make_failed_request()
    # count = 2, over tolerance, next request will fail without requesting upstream

    # "unavailable from provider" indicates the cached failure
    # we do not add any pook mock for this request, proving it is never made
    # and therefore bypassed by the cached failure
    with pytest.raises(
        UpstreamThumbnailException, match="Thumbnail unavailable from provider"
    ):
        photon_get(TEST_MEDIA_INFO)


@pytest.mark.pook
def test_get_successful_https_image_url_sends_ssl_parameter(mock_image_data):
    https_url = TEST_IMAGE_URL.replace("http://", "https://")
    (
        pook.get(PHOTON_URL_FOR_TEST_IMAGE)
        .params(
            {
                "w": THUMBNAIL_WIDTH_PARAM,
                "quality": settings.THUMBNAIL_QUALITY,
                "ssl": "true",
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
    )

    https_media_info = replace(TEST_MEDIA_INFO, image_url=https_url)

    res = photon_get(https_media_info)

    assert res.content == MOCK_BODY.encode()
    assert res.status_code == 200


@pytest.mark.pook
def test_get_unsuccessful_request_raises_custom_exception():
    pook.get(PHOTON_URL_FOR_TEST_IMAGE).reply(404).mock

    with pytest.raises(
        UpstreamThumbnailException, match=r"Failed to render thumbnail."
    ):
        photon_get(TEST_MEDIA_INFO)


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
    "content_type, expected_ext",
    [
        ("image/png;charset=UTF-8", "png"),
        ("image/jpeg", "jpg"),
        ("image/png", "png"),
        ("image/gif", "gif"),
        ("image/svg+xml", "svg"),
        ("audio/midi", "midi"),
        ("audio/mpeg", "mp3"),
        ("audio/ogg", None),
        ("audio/opus", "opus"),
        ("audio/wav", None),
        ("video/webm", "webm"),
        (None, None),
        ("foobar", None),
    ],
)
def test_get_extension_from_content_type(content_type, expected_ext):
    assert extension._get_file_extension_from_content_type(content_type) == expected_ext


@pytest.mark.django_db
@pytest.mark.parametrize("image_type", ["apng", "tiff", "bmp"])
def test_photon_get_raises_by_not_allowed_types(image_type):
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
@pytest.mark.pook(start_active=False)
def test_photon_get_saves_image_type_to_cache(
    headers,
    expected_cache_val,
    is_cache_reachable,
    cache_name,
    request,
):
    cache = request.getfixturevalue(cache_name)

    image_url = TEST_IMAGE_URL.replace(".jpg", "")
    image = ImageFactory.create(url=image_url)
    media_info = MediaInfo(
        media_identifier=image.identifier,
        media_provider=image.provider,
        image_url=image_url,
    )
    pook.on()
    pook.head(image_url, reply=200, response_headers=headers)
    with capture_logs() as cap_logs, pytest.raises(UnsupportedMediaType):
        photon_get(media_info)

    key = f"media:{image.identifier}:thumb_type"
    if is_cache_reachable:
        assert cache.get(key) == expected_cache_val
    else:
        messages = [record["event"] for record in cap_logs]
        assert all(
            message in messages
            for message in [
                "Redis connect failed, cannot get cached image extension.",
                "Redis connect failed, cannot cache image extension.",
            ]
        )


@pytest.mark.django_db
@pytest.mark.pook(start_active=False)
def test_wikimedia_thumbnail_default_params_small_image():
    image_url = (
        "https://upload.wikimedia.org/wikipedia/commons/9/9e/Color_icon_yellow.svg"
    )
    width = settings.THUMBNAIL_WIDTH_PX - 1
    image = ImageFactory.create(url=image_url, provider="wikimedia", width=width)
    # It uses the image width to prevent wikimedia's thumbnail service upscaling the image
    expected_thumbnail_url_path = f"upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Color_icon_yellow.svg/lossy-{width}px-Color_icon_yellow.svg.png"

    pook.on()
    (
        pook.get(settings.PHOTON_ENDPOINT + expected_thumbnail_url_path)
        .params(
            {
                "ssl": "true",
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
    )

    photon_get(
        MediaInfo(
            media_identifier=image.identifier,
            media_provider=image.provider,
            image_url=image_url,
            width=image.width,
        )
    )


@pytest.mark.django_db
@pytest.mark.pook(start_active=False)
def test_wikimedia_thumbnail_default_params_large_image():
    image_url = (
        "https://upload.wikimedia.org/wikipedia/commons/9/9e/Color_icon_yellow.svg"
    )
    width = settings.THUMBNAIL_WIDTH_PX + 1
    image = ImageFactory.create(url=image_url, provider="wikimedia", width=width)
    # Uses the default thumbnail setting because that value is smaller than the width of the image
    expected_thumbnail_url_path = f"upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Color_icon_yellow.svg/lossy-{settings.THUMBNAIL_WIDTH_PX}px-Color_icon_yellow.svg.png"

    pook.on()
    (
        pook.get(settings.PHOTON_ENDPOINT + expected_thumbnail_url_path)
        .params(
            {
                "ssl": "true",
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
    )

    photon_get(
        MediaInfo(
            media_identifier=image.identifier,
            media_provider=image.provider,
            image_url=image_url,
            width=image.width,
        )
    )


@pytest.mark.django_db
@pytest.mark.pook(start_active=False)
def test_wikimedia_thumbnail_default_params_unknown_width():
    image_url = (
        "https://upload.wikimedia.org/wikipedia/commons/9/9e/Color_icon_yellow.svg"
    )
    image = ImageFactory.create(url=image_url, provider="wikimedia")
    # Uses the default thumbnail setting because the actual image size is unknown
    expected_thumbnail_url_path = f"upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Color_icon_yellow.svg/lossy-{settings.THUMBNAIL_WIDTH_PX}px-Color_icon_yellow.svg.png"

    pook.on()
    (
        pook.get(settings.PHOTON_ENDPOINT + expected_thumbnail_url_path)
        .params(
            {
                "ssl": "true",
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
    )

    photon_get(
        MediaInfo(
            media_identifier=image.identifier,
            media_provider=image.provider,
            image_url=image_url,
            width=None,
        )
    )


@pytest.mark.django_db
@pytest.mark.pook(start_active=False)
def test_wikimedia_thumbnail_full_size_params():
    image_url = (
        "https://upload.wikimedia.org/wikipedia/commons/9/9e/Color_icon_yellow.svg"
    )
    image = ImageFactory.create(url=image_url, provider="wikimedia")
    expected_thumbnail_url_path = f"upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Color_icon_yellow.svg/lossy-{image.width}px-Color_icon_yellow.svg.png"

    pook.on()
    (
        pook.get(settings.PHOTON_ENDPOINT + expected_thumbnail_url_path)
        .params(
            {
                "ssl": "true",
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
    )

    photon_get(
        MediaInfo(
            media_identifier=image.identifier,
            media_provider=image.provider,
            image_url=image_url,
            width=image.width,
        ),
        request_config=RequestConfig(is_full_size=True),
    )


@pytest.mark.django_db
@pytest.mark.pook(start_active=False)
def test_wikimedia_thumbnail_uncompressed_params():
    image_url = (
        "https://upload.wikimedia.org/wikipedia/commons/9/9e/Color_icon_yellow.svg"
    )
    # ensure image width is larger than the default so we can reliably assert it is _not_ pulling the full-size image
    # if width is smaller than the default, even if we request full size, it will always use the images actual width
    # to prevent wikimedia's thumbnail service from upscaling the image, which it will do if the requested width is
    # larger than the actual width of the image
    width = settings.THUMBNAIL_WIDTH_PX + 1
    image = ImageFactory.create(url=image_url, provider="wikimedia", width=width)
    expected_thumbnail_url_path = f"upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Color_icon_yellow.svg/{settings.THUMBNAIL_WIDTH_PX}px-Color_icon_yellow.svg.png"

    pook.on()
    (
        pook.get(settings.PHOTON_ENDPOINT + expected_thumbnail_url_path)
        .params(
            {
                "ssl": "true",
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
    )

    photon_get(
        MediaInfo(
            media_identifier=image.identifier,
            media_provider=image.provider,
            image_url=image_url,
            width=image.width,
        ),
        request_config=RequestConfig(is_compressed=False),
    )


@pytest.mark.django_db
@pytest.mark.pook(start_active=False)
def test_wikimedia_thumbnail_uncompressed_full_size_params():
    image_url = (
        "https://upload.wikimedia.org/wikipedia/commons/9/9e/Color_icon_yellow.svg"
    )
    image = ImageFactory.create(url=image_url, provider="wikimedia")
    expected_thumbnail_url_path = f"upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Color_icon_yellow.svg/{image.width}px-Color_icon_yellow.svg.png"

    pook.on()
    (
        pook.get(settings.PHOTON_ENDPOINT + expected_thumbnail_url_path)
        .params(
            {
                "ssl": "true",
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
    )

    photon_get(
        MediaInfo(
            media_identifier=image.identifier,
            media_provider=image.provider,
            image_url=image_url,
            width=image.width,
        ),
        request_config=RequestConfig(is_compressed=False, is_full_size=True),
    )


@pytest.mark.django_db
@pytest.mark.pook(start_active=False)
def test_wikimedia_thumbnail_unknown_url_format():
    image_url = "https://upload.wikimedia.org/path_prefix/Color_icon_yellow.jpg"
    image = ImageFactory.create(url=image_url, provider="wikimedia")
    expected_thumbnail_url_path = (
        "upload.wikimedia.org/path_prefix/Color_icon_yellow.jpg"
    )

    pook.on()
    (
        pook.get(settings.PHOTON_ENDPOINT + expected_thumbnail_url_path)
        .params(
            {
                "ssl": "true",
                "w": THUMBNAIL_WIDTH_PARAM,
                "quality": settings.THUMBNAIL_QUALITY,
            }
        )
        .header("User-Agent", UA_HEADER)
        .header("Accept", "image/*")
        .reply(200)
        .body(MOCK_BODY)
    )

    photon_get(
        MediaInfo(
            media_identifier=image.identifier,
            media_provider=image.provider,
            image_url=image_url,
            width=image.width,
        ),
    )

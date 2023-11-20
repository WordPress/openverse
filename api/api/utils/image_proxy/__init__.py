import logging
from typing import Literal
from urllib.parse import urlparse

from django.conf import settings
from django.http import StreamingHttpResponse
from rest_framework.exceptions import UnsupportedMediaType

import django_redis
import requests
import sentry_sdk
from sentry_sdk import push_scope, set_context

from api.utils.image_proxy.exception import UpstreamThumbnailException
from api.utils.image_proxy.extension import get_image_extension
from api.utils.image_proxy.photon import get_photon_request_params
from api.utils.tallies import get_monthly_timestamp


parent_logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": settings.OUTBOUND_USER_AGENT_TEMPLATE.format(
        purpose="ThumbnailGeneration"
    )
}

PHOTON_TYPES = {"gif", "jpg", "jpeg", "png", "webp"}
ORIGINAL_TYPES = {"svg"}

PHOTON = "photon"
ORIGINAL = "original"
THUMBNAIL_STRATEGY = Literal["photon_proxy", "original"]


def get_request_params_for_extension(
    ext: str,
    headers: dict[str, str],
    image_url: str,
    parsed_image_url: urlparse,
    is_full_size: bool,
    is_compressed: bool,
) -> tuple[str, dict[str, str], dict[str, str]]:
    """
    Get the request params (url, params, headers) for the thumbnail proxy.
    If the image type is supported by photon, we use photon, and compute the necessary
    request params, if the file can be cached and returned as is (SVG), we do that,
    otherwise we raise UnsupportedMediaType exception.
    """
    if ext in PHOTON_TYPES:
        return get_photon_request_params(
            parsed_image_url, is_full_size, is_compressed, headers
        )
    elif ext in ORIGINAL_TYPES:
        return image_url, {}, headers
    raise UnsupportedMediaType(
        f"Image extension {ext} is not supported by the thumbnail proxy."
    )


def get(
    image_url: str,
    media_identifier: str,
    media_provider: str,
    accept_header: str = "image/*",
    is_full_size: bool = False,
    is_compressed: bool = True,
) -> StreamingHttpResponse:
    """
    Proxy an image through Photon if its file type is supported, else return the
    original image if the file type is SVG. Otherwise, raise an exception.
    """
    logger = parent_logger.getChild("get")
    tallies = django_redis.get_redis_connection("tallies")
    month = get_monthly_timestamp()

    image_extension = get_image_extension(image_url, media_identifier)

    headers = {"Accept": accept_header} | HEADERS

    parsed_image_url = urlparse(image_url)
    domain = parsed_image_url.netloc

    upstream_url, params, headers = get_request_params_for_extension(
        image_extension,
        headers,
        image_url,
        parsed_image_url,
        is_full_size,
        is_compressed,
    )

    try:
        upstream_response = requests.get(
            upstream_url,
            timeout=15,
            params=params,
            headers=headers,
            stream=True,
        )
        tallies.incr(f"thumbnail_response_code:{month}:{upstream_response.status_code}")
        tallies.incr(
            f"thumbnail_response_code_by_domain:{domain}:"
            f"{month}:{upstream_response.status_code}"
        )
        tallies.incr(
            f"thumbnail_response_code_by_provider:{media_provider}:"
            f"{month}:{upstream_response.status_code}"
        )
        upstream_response.raise_for_status()
    except Exception as exc:
        exception_name = f"{exc.__class__.__module__}.{exc.__class__.__name__}"
        key = f"thumbnail_error:{exception_name}:{domain}:{month}"
        count = tallies.incr(key)
        if count <= settings.THUMBNAIL_ERROR_INITIAL_ALERT_THRESHOLD or (
            count % settings.THUMBNAIL_ERROR_REPEATED_ALERT_FREQUENCY == 0
        ):
            with push_scope() as scope:
                set_context(
                    "upstream_url",
                    {
                        "url": upstream_url,
                        "params": params,
                        "headers": headers,
                    },
                )
                scope.set_tag(
                    "occurrences", settings.THUMBNAIL_ERROR_REPEATED_ALERT_FREQUENCY
                )
                sentry_sdk.capture_exception(exc)
        if isinstance(exc, requests.exceptions.HTTPError):
            code = exc.response.status_code
            tallies.incr(
                f"thumbnail_http_error:{domain}:{month}:{code}:{exc.response.text}"
            )
            logger.warning(
                f"Failed to render thumbnail {upstream_url=} {code=} {media_provider=}"
            )
        raise UpstreamThumbnailException(f"Failed to render thumbnail. {exc}")

    res_status = upstream_response.status_code
    content_type = upstream_response.headers.get("Content-Type")
    logger.debug(
        f"Image proxy response status: {res_status}, content-type: {content_type}"
    )

    return StreamingHttpResponse(
        upstream_response.iter_content(),
        status=res_status,
        content_type=content_type,
    )

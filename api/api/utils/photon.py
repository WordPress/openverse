import logging
from os.path import splitext
from urllib.parse import urlparse

from django.conf import settings
from django.http import HttpResponse
from rest_framework import status
from rest_framework.exceptions import APIException, UnsupportedMediaType

import django_redis
import requests
import sentry_sdk


parent_logger = logging.getLogger(__name__)


class UpstreamThumbnailException(APIException):
    status_code = status.HTTP_424_FAILED_DEPENDENCY
    default_detail = "Could not render thumbnail due to upstream provider error."
    default_code = "upstream_photon_failure"


ALLOWED_TYPES = ["gif", "jpg", "jpeg", "png", "webp"]

HEADERS = {
    "User-Agent": settings.OUTBOUND_USER_AGENT_TEMPLATE.format(
        purpose="ThumbnailGeneration"
    )
}


def _get_extension_from_url(image_url: str) -> str:
    """Return the image extension if present in the URL."""
    parsed = urlparse(image_url)
    _, ext = splitext(parsed.path)
    return ext[1:]  # remove the leading dot


def check_image_type(image_url: str, media_obj) -> None:
    key = f"media:{media_obj.identifier}:thumb_type"
    cache = django_redis.get_redis_connection("default")

    ext = _get_extension_from_url(image_url)

    if not ext:
        # If the extension is not present in the URL, try to get it from the redis cache
        ext = cache.get(key)

    if not ext:
        # If the extension is still not present, try getting it from the content type
        try:
            response = requests.head(image_url)
            response.raise_for_status()
        except Exception as exc:
            sentry_sdk.capture_exception(exc)
            raise UpstreamThumbnailException(
                f"Failed to render thumbnail due to inability to check media "
                f"type. {exc}"
            )
        else:
            ext = response.headers["Content-Type"].split("/")[1]
            cache.set(key, ext)

    if ext not in ALLOWED_TYPES:
        raise UnsupportedMediaType(ext)


def _get_photon_params(image_url, is_full_size, is_compressed):
    """
    Photon options documented here:
    https://developer.wordpress.com/docs/photon/api/
    """
    params = {}

    if not is_full_size:
        params["w"] = settings.THUMBNAIL_WIDTH_PX

    if is_compressed:
        params["quality"] = settings.THUMBNAIL_QUALITY

    parsed_image_url = urlparse(image_url)

    if parsed_image_url.query:
        # No need to URL encode this string because requests will already
        # pass the `params` object to `urlencode` before it appends it to the
        # request URL.
        params["q"] = parsed_image_url.query

    if parsed_image_url.scheme == "https":
        # Photon defaults to HTTP without this parameter
        # which will cause some providers to fail (if they
        # do not serve over HTTP and do not have a redirect)
        params["ssl"] = "true"

    return params, parsed_image_url


def get(
    image_url: str,
    accept_header: str = "image/*",
    is_full_size: bool = False,
    is_compressed: bool = True,
) -> HttpResponse:
    logger = parent_logger.getChild("get")
    params, parsed_image_url = _get_photon_params(
        image_url, is_full_size, is_compressed
    )

    # Photon excludes the protocol, so we need to reconstruct the url + port + path
    # to send as the "path" of the Photon request
    domain = parsed_image_url.netloc
    path = parsed_image_url.path
    upstream_url = f"{settings.PHOTON_ENDPOINT}{domain}{path}"

    headers = {"Accept": accept_header} | HEADERS
    if settings.PHOTON_AUTH_KEY:
        headers["X-Photon-Authentication"] = settings.PHOTON_AUTH_KEY

    try:
        upstream_response = requests.get(
            upstream_url,
            timeout=15,
            params=params,
            headers=headers,
        )
        upstream_response.raise_for_status()
    except requests.ReadTimeout as exc:
        # Count the incident so that we can identify providers with most timeouts.
        key = f"{settings.THUMBNAIL_TIMEOUT_PREFIX}{domain}"
        cache = django_redis.get_redis_connection("default")
        try:
            cache.incr(key)
        except ValueError:  # Key does not exist.
            cache.set(key, 1)

        sentry_sdk.capture_exception(exc)
        raise UpstreamThumbnailException(
            f"Failed to render thumbnail due to timeout: {exc}"
        )
    except requests.RequestException as exc:
        sentry_sdk.capture_exception(exc)
        raise UpstreamThumbnailException(f"Failed to render thumbnail. {exc}")
    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        raise UpstreamThumbnailException(
            f"Failed to render thumbnail due to unidentified exception. {exc}"
        )
    else:
        res_status = upstream_response.status_code
        content_type = upstream_response.headers.get("Content-Type")
        logger.debug(
            "Image proxy response "
            f"status: {res_status}, content-type: {content_type}"
        )

        return HttpResponse(
            upstream_response.content,
            status=res_status,
            content_type=content_type,
        )

import logging
from dataclasses import dataclass
from typing import Literal
from urllib.parse import urlparse

from django.conf import settings
from django.http import HttpResponse
from rest_framework.exceptions import UnsupportedMediaType

import aiohttp
import django_redis
from aiohttp.client_exceptions import ClientResponseError
from asgiref.sync import sync_to_async
from redis.exceptions import ConnectionError

from api.utils.aiohttp import get_aiohttp_session
from api.utils.asyncio import do_not_wait_for
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


@dataclass
class MediaInfo:
    media_provider: str
    media_identifier: str
    image_url: str


@dataclass
class RequestConfig:
    accept_header: str = "image/*"
    is_full_size: bool = False
    is_compressed: bool = True


def get_request_params_for_extension(
    ext: str,
    headers: dict[str, str],
    image_url: str,
    parsed_image_url: urlparse,
    request_config: RequestConfig,
) -> tuple[str, dict[str, str], dict[str, str]]:
    """
    Get the request params (url, params, headers) for the thumbnail proxy.
    If the image type is supported by photon, we use photon, and compute the necessary
    request params, if the file can be cached and returned as is (SVG), we do that,
    otherwise we raise UnsupportedMediaType exception.
    """
    if ext in PHOTON_TYPES:
        return get_photon_request_params(
            parsed_image_url,
            request_config.is_full_size,
            request_config.is_compressed,
            headers,
        )
    elif ext in ORIGINAL_TYPES:
        return image_url, {}, headers
    raise UnsupportedMediaType(
        f"Image extension {ext} is not supported by the thumbnail proxy."
    )


@sync_to_async
def _tally_response(
    tallies_conn,
    media_info: MediaInfo,
    month: str,
    domain: str,
    response: aiohttp.ClientResponse,
):
    """
    Tally image proxy response without waiting for Redis to respond.

    Pulled into a separate function to help reduce overload when skimming
    the `get` function, which is complex enough as is.
    """

    logger = parent_logger.getChild("_tally_response")

    with tallies_conn.pipeline() as tallies:
        tallies.incr(f"thumbnail_response_code:{month}:{response.status}")
        tallies.incr(
            f"thumbnail_response_code_by_domain:{domain}:" f"{month}:{response.status}"
        )
        tallies.incr(
            f"thumbnail_response_code_by_provider:{media_info.media_provider}:"
            f"{month}:{response.status}"
        )
        try:
            tallies.execute()
        except ConnectionError:
            logger.warning(
                "Redis connect failed, thumbnail response codes not tallied."
            )


@sync_to_async
def _tally_client_response_errors(tallies, month: str, domain: str, status: int):
    logger = parent_logger.getChild("_tally_client_response_errors")
    try:
        tallies.incr(f"thumbnail_http_error:{domain}:{month}:{status}")
    except ConnectionError:
        logger.warning("Redis connect failed, thumbnail HTTP errors not tallied.")


_UPSTREAM_TIMEOUT = aiohttp.ClientTimeout(15)


async def get(
    media_info: MediaInfo,
    request_config: RequestConfig = RequestConfig(),
) -> HttpResponse:
    """
    Retrieve the proxied image.

    Proxy an image through Photon if its file type is supported, else return the
    original image if the file type is SVG. Otherwise, raise an exception.
    """
    image_url = media_info.image_url
    media_identifier = media_info.media_identifier

    logger = parent_logger.getChild("get")
    tallies = django_redis.get_redis_connection("tallies")
    tallies_incr = sync_to_async(tallies.incr)
    month = get_monthly_timestamp()

    image_extension = await get_image_extension(image_url, media_identifier)

    headers = {"Accept": request_config.accept_header} | HEADERS

    parsed_image_url = urlparse(image_url)
    domain = parsed_image_url.netloc

    upstream_url, params, headers = get_request_params_for_extension(
        image_extension,
        headers,
        image_url,
        parsed_image_url,
        request_config,
    )

    try:
        session = await get_aiohttp_session()

        upstream_response = await session.get(
            upstream_url,
            timeout=_UPSTREAM_TIMEOUT,
            params=params,
            headers=headers,
        )
        do_not_wait_for(
            _tally_response(tallies, media_info, month, domain, upstream_response)
        )
        status_code = upstream_response.status
        content_type = upstream_response.headers.get("Content-Type")
        logger.debug(
            "Image proxy response status: %s, content-type: %s",
            status_code,
            content_type,
        )
        content = await upstream_response.read()
        upstream_response.raise_for_status()
        return HttpResponse(
            content, 
            status = status_code,
            content_type = content_type,
        )
    except ClientResponseError as exc:
        status = exc.status
        do_not_wait_for(
            _tally_client_response_errors(tallies, month, domain, status)
        )
        logger.warning(
            f"Failed to render thumbnail "
            f"{upstream_url=} {status=} "
            f"{media_info.media_provider=} "
            f"{str(exc)=}"
        )
        raise UpstreamThumbnailException(f"Failed to render thumbnail. {exc}") from exc
    except Exception as exc:
        exception_name = f"{exc.__class__.__module__}.{exc.__class__.__name__}"
        key = f"thumbnail_error:{exception_name}:{domain}:{month}"
        try:
            await tallies_incr(key)
        except ConnectionError:
            logger.warning("Redis connect failed, thumbnail errors not tallied.")
        raise UpstreamThumbnailException(f"Failed to render thumbnail. {exc}")

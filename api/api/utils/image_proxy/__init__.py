import asyncio
import time
from dataclasses import dataclass
from datetime import timedelta
from functools import wraps
from typing import Literal, Type
from urllib.parse import urlparse
from uuid import UUID

from django.conf import settings
from django.http import HttpResponse
from rest_framework.exceptions import UnsupportedMediaType

import aiohttp
import django_redis
import structlog
from aiohttp.client_exceptions import ClientResponseError
from asgiref.sync import sync_to_async
from redis.client import Redis
from redis.exceptions import ConnectionError

from api.utils.aiohttp import get_aiohttp_session
from api.utils.image_proxy.exception import UpstreamThumbnailException
from api.utils.image_proxy.extension import get_image_extension
from api.utils.image_proxy.photon import get_photon_request_params
from api.utils.tallies import get_monthly_timestamp


logger = structlog.get_logger(__name__)

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
    media_identifier: UUID
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
    Tally image proxy response.

    Pulled into a separate function to help reduce overload when skimming
    the `get` function, which is complex enough as is.
    """

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
    try:
        tallies.incr(f"thumbnail_http_error:{domain}:{month}:{status}")
    except ConnectionError:
        logger.warning("Redis connect failed, thumbnail HTTP errors not tallied.")


# thmbfail == THuMBnail FAILures; this key path will exist for every thumbnail requested, so it needs to be space efficient
FAILURE_CACHE_KEY_TEMPLATE = "thmbfail:{ident}"


def _cache_repeated_failures(_get):
    """
    Wrap ``image_proxy.get`` to cache repeated upstream failures
    and avoid re-requesting images likely to fail.

    Do this by incrementing a counter for each media identifier each time the inner request
    fails. Before making thumbnail requests, check this counter. If it is above the configured
    threshold, assume the request will fail again, and eagerly return a failed response without
    sending the request upstream.

    Additionally, if the request succeeds and the failure count is not 0, decrement the counter
    to reflect the successful response, accounting for thumbnails that were temporarily flaky,
    while still allowing them to get temporarily cached as a failure if additional requests fail
    and push the counter over the threshold.
    """

    @wraps(_get)
    async def do_cache(*args, **kwargs):
        media_info: MediaInfo = args[0]
        compressed_ident = str(media_info.media_identifier).replace("-", "")
        redis_key = FAILURE_CACHE_KEY_TEMPLATE.format(ident=compressed_ident)
        tallies: Redis = django_redis.get_redis_connection("tallies")

        try:
            cached_failure_count = await sync_to_async(tallies.get)(
                redis_key,
            )
            cached_failure_count = (
                int(cached_failure_count) if cached_failure_count is not None else 0
            )
        except ConnectionError:
            # Ignore the connection error, treat it like it's never been cached
            cached_failure_count = 0

        if cached_failure_count > settings.THUMBNAIL_FAILURE_CACHE_TOLERANCE:
            logger.info(
                "%s thumbnail is too flaky, using cached failure response.",
                media_info.media_identifier,
            )
            raise UpstreamThumbnailException("Thumbnail unavailable from provider.")

        try:
            response = await _get(*args, **kwargs)
            if cached_failure_count > 0:
                # Decrement the key
                # Do not delete it, because if it isn't 0, then it has failed before
                # meaning we should continue to monitor it within the cache window
                # in case the upstream is flaky and eventually goes over the tolerance
                try:
                    await sync_to_async(tallies.decr)(redis_key)
                    await sync_to_async(tallies.expire)(
                        redis_key, settings.THUMBNAIL_FAILURE_CACHE_WINDOW_SECONDS
                    )
                except ConnectionError:
                    logger.warning(
                        "Redis connect failed, thumbnail failure not decremented."
                    )
            return response
        except:
            try:
                await sync_to_async(tallies.incr)(redis_key)
                # Call expire each time the key is incremented
                # This pushes expiration out each time a new failure is cached
                await sync_to_async(tallies.expire)(
                    redis_key, settings.THUMBNAIL_FAILURE_CACHE_WINDOW_SECONDS
                )
            except ConnectionError:
                logger.warning(
                    "Redis connect failed, thumbnail failure not incremented."
                )
            raise

    return do_cache


_UPSTREAM_TIMEOUT = aiohttp.ClientTimeout(settings.THUMBNAIL_UPSTREAM_TIMEOUT)


@_cache_repeated_failures
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

    start_time = time.perf_counter()

    try:
        session = await get_aiohttp_session()

        upstream_response = await session.get(
            upstream_url,
            timeout=_UPSTREAM_TIMEOUT,
            params=params,
            headers=headers,
        )

        await _tally_response(tallies, media_info, month, domain, upstream_response)

        upstream_response.raise_for_status()

        status_code = upstream_response.status
        content_type = upstream_response.headers.get("Content-Type")

        content = await upstream_response.content.read()

        end_time = time.perf_counter()
        logger.info(
            "thumbnail_upstream_timing",
            status=status_code,
            time=end_time - start_time,
            provider=media_info.media_provider,
            content_type=content_type,
            url=image_url,
        )

        return HttpResponse(
            content,
            status=status_code,
            content_type=content_type,
        )
    except Exception as exc:
        # Record timing before tallying to Redis to avoid including
        # the Redis request timing in what is meant to be the upstream
        # request timing.
        end_time = time.perf_counter()

        exception_name = f"{exc.__class__.__module__}.{exc.__class__.__name__}"
        key = f"thumbnail_error:{exception_name}:{domain}:{month}"

        try:
            await tallies_incr(key)
        except ConnectionError:
            logger.warning("Redis connect failed, thumbnail errors not tallied.")

        if isinstance(exc, ClientResponseError):
            status = exc.status
            await _tally_client_response_errors(tallies, month, domain, status)
            logger.warning(
                "thumbnail_upstream_failure",
                url=upstream_url,
                status=status,
                provider=media_info.media_provider,
                exc=exc.message,
            )
        else:
            status = -1

        logger.info(
            "thumbnail_upstream_timing",
            status=status,
            time=end_time - start_time,
            provider=media_info.media_provider,
            content_type=image_extension,
            url=image_url,
        )

        raise UpstreamThumbnailException(f"Failed to render thumbnail. {exc}")

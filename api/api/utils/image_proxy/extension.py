import mimetypes
from os.path import splitext
from urllib.parse import urlparse

from django.conf import settings

import aiohttp
import django_redis
import structlog
from asgiref.sync import sync_to_async
from redis.exceptions import ConnectionError

from api.utils.aiohttp import get_aiohttp_session
from api.utils.image_proxy.dataclasses import MediaInfo
from api.utils.image_proxy.exception import UpstreamThumbnailException


logger = structlog.get_logger(__name__)


_HEAD_TIMEOUT = aiohttp.ClientTimeout(settings.THUMBNAIL_EXTENSION_REQUEST_TIMEOUT)


async def get_image_extension(media_info: MediaInfo) -> str | None:
    image_url = media_info.image_url

    cache = django_redis.get_redis_connection("default")
    key = f"media:{media_info.media_identifier}:thumb_type"

    ext = _get_file_extension_from_url(image_url)

    if not ext:
        # If the extension is not present in the URL, try to get it from the redis cache
        try:
            ext = await sync_to_async(cache.get)(key)
            ext = ext.decode("utf-8") if ext else None
        except ConnectionError:
            logger.warning("Redis connect failed, cannot get cached image extension.")

    if not ext:
        # If the extension is still not present, try getting it from the content type
        try:
            session = await get_aiohttp_session()
            response = await session.head(
                image_url,
                raise_for_status=True,
                timeout=_HEAD_TIMEOUT,
                trace_request_ctx={
                    "timing_event_name": "thumbnail_extension_request_timing",
                    "timing_event_ctx": {"provider": media_info.media_provider},
                },
            )

            if response.headers and "Content-Type" in response.headers:
                content_type = response.headers["Content-Type"]
                ext = _get_file_extension_from_content_type(content_type)
            else:
                ext = None

            await _cache_extension(cache, key, ext)
        except Exception as exc:
            logger.error("upstream_thumbnail_exception", exc=exc, exc_info=True)
            raise UpstreamThumbnailException(
                "Failed to render thumbnail due to inability to check media "
                f"type. {exc}"
            )

    return ext


@sync_to_async
def _cache_extension(cache, key, ext):
    try:
        cache.set(key, ext if ext else "unknown")
    except ConnectionError:
        logger.warning("Redis connect failed, cannot cache image extension.")


def _get_file_extension_from_url(image_url: str) -> str:
    """Return the image extension if present in the URL."""
    parsed = urlparse(image_url)
    _, ext = splitext(parsed.path)
    return ext[1:].lower()  # remove the leading dot


def _get_file_extension_from_content_type(content_type: str) -> str | None:
    """
    Return the image extension if present in the Response's content type
    header.
    """
    if (
        content_type
        and "/" in content_type
        and (ext := mimetypes.guess_extension(content_type.split(";")[0], strict=False))
    ):
        return ext.strip(".")
    return None

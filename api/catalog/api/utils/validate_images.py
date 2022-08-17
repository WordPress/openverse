import logging
import time

from django.conf import settings

import django_redis
import grequests
from decouple import config

from catalog.api.utils.dead_link_mask import get_query_mask, save_query_mask


parent_logger = logging.getLogger(__name__)


CACHE_PREFIX = "valid:"
HEADERS = {
    "User-Agent": settings.OUTBOUND_USER_AGENT_TEMPLATE.format(purpose="LinkValidation")
}


def _get_cached_statuses(redis, image_urls):
    cached_statuses = redis.mget([CACHE_PREFIX + url for url in image_urls])
    return [int(b.decode("utf-8")) if b is not None else None for b in cached_statuses]


def _get_expiry(status, default):
    return config(f"LINK_VALIDATION_CACHE_EXPIRY__{status}", default=default, cast=int)


def validate_images(query_hash, start_slice, results, image_urls):
    """
    Make sure images exist before we display them. Treat redirects as broken
    links since 99% of the time the redirect leads to a generic "not found"
    placeholder.

    Results are cached in redis and shared amongst all API servers in the
    cluster.
    """
    logger = parent_logger.getChild("validate_images")
    if not image_urls:
        logger.info("no image urls to validate")
        return

    logger.debug("starting validation")
    start_time = time.time()
    # Pull matching images from the cache.
    redis = django_redis.get_redis_connection("default")
    cached_statuses = _get_cached_statuses(redis, image_urls)
    logger.debug(f"len(cached_statuses)={len(cached_statuses)}")
    # Anything that isn't in the cache needs to be validated via HEAD request.
    to_verify = {}
    for idx, url in enumerate(image_urls):
        if cached_statuses[idx] is None:
            to_verify[url] = idx
    logger.debug(f"len(to_verify)={len(to_verify)}")
    reqs = (
        grequests.head(
            url, headers=HEADERS, allow_redirects=False, timeout=2, verify=False
        )
        for url in to_verify.keys()
    )
    verified = grequests.map(reqs, exception_handler=_validation_failure)
    # Cache newly verified image statuses.
    to_cache = {}
    for idx, url in enumerate(to_verify.keys()):
        cache_key = CACHE_PREFIX + url
        if verified[idx]:
            status = verified[idx].status_code
        # Response didn't arrive in time. Try again later.
        else:
            status = -1
        to_cache[cache_key] = status

    thirty_minutes = 60 * 30
    twenty_four_hours_seconds = 60 * 60 * 24
    pipe = redis.pipeline()
    if len(to_cache) > 0:
        pipe.mset(to_cache)
    for key, status in to_cache.items():
        # Cache successful links for a day, and broken links for 120 days.
        if status == 200:
            logger.debug("healthy link " f"key={key} ")
            expiry = _get_expiry(200, twenty_four_hours_seconds * 30)
        elif status == -1:
            logger.debug("no response from provider " f"key={key}")
            # Content provider failed to respond; try again in a short interval
            expiry = _get_expiry("_1", thirty_minutes)
        else:
            logger.debug("broken link " f"key={key} ")
            expiry = _get_expiry("DEFAULT", twenty_four_hours_seconds * 120)

        pipe.expire(key, expiry)

    pipe.execute()

    # Merge newly verified results with cached statuses
    for idx, url in enumerate(to_verify):
        cache_idx = to_verify[url]
        if verified[idx] is not None:
            cached_statuses[cache_idx] = verified[idx].status_code
        else:
            cached_statuses[cache_idx] = -1

    # Create a new dead link mask
    new_mask = [1] * len(results)
    # Delete broken images from the search results response.
    for idx, _ in enumerate(cached_statuses):
        del_idx = len(cached_statuses) - idx - 1
        status = cached_statuses[del_idx]
        if status == 429 or status == 403:
            logger.warning(
                "Image validation failed due to rate limiting or blocking. "
                f"url={image_urls[idx]} "
                f"status={status} "
            )
        elif status != 200:
            logger.info(
                "Deleting broken image from results "
                f"id={results[del_idx]['identifier']} "
                f"status={status} "
            )
            del results[del_idx]
            new_mask[del_idx] = 0

    # Merge and cache the new mask
    mask = get_query_mask(query_hash)
    if mask:
        new_mask = mask[:start_slice] + new_mask
    save_query_mask(query_hash, new_mask)

    end_time = time.time()
    logger.debug(
        "end validation "
        f"end_time={end_time} "
        f"start_time={start_time} "
        f"delta={end_time - start_time} "
    )


def _validation_failure(request, exception):
    logger = parent_logger.getChild("_validation_failure")
    logger.warning(f"Failed to validate image! Reason: {exception}")

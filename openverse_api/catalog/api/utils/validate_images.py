import time
import grequests
import logging
from django_redis import get_redis_connection
from catalog.api.utils.dead_link_mask import get_query_mask, save_query_mask

log = logging.getLogger(__name__)


def validate_images(query_hash, start_slice, results, image_urls):
    """
    Make sure images exist before we display them. Treat redirects as broken
    links since 99% of the time the redirect leads to a generic "not found"
    placeholder.

    Results are cached in redis and shared amongst all API servers in the
    cluster.
    """
    if not image_urls:
        return
    start_time = time.time()
    # Pull matching images from the cache.
    redis = get_redis_connection("default")
    cache_prefix = 'valid:'
    cached_statuses = redis.mget([cache_prefix + url for url in image_urls])
    cached_statuses = [
        int(b.decode('utf-8'))
        if b is not None else None for b in cached_statuses
    ]
    # Anything that isn't in the cache needs to be validated via HEAD request.
    to_verify = {}
    for idx, url in enumerate(image_urls):
        if cached_statuses[idx] is None:
            to_verify[url] = idx
    reqs = (
        grequests.head(u, allow_redirects=False, timeout=2, verify=False)
        for u in to_verify.keys()
    )
    verified = grequests.map(reqs, exception_handler=_validation_failure)
    # Cache newly verified image statuses.
    to_cache = {}
    for idx, url in enumerate(to_verify.keys()):
        cache_key = cache_prefix + url
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
            pipe.expire(key, twenty_four_hours_seconds)
        elif status == -1:
            # Content provider failed to respond; try again in a short interval
            pipe.expire(key, thirty_minutes)
        else:
            pipe.expire(key, twenty_four_hours_seconds * 120)
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
            log.warning(
                'Image validation failed due to rate limiting or blocking. '
                f'Affected URL: {image_urls[idx]}'
            )
        elif status != 200:
            log.info(
                f"Deleting broken image with ID "
                f"{results[del_idx]['identifier']} from results."
            )
            del results[del_idx]
            new_mask[del_idx] = 0

    # Merge and cache the new mask
    mask = get_query_mask(query_hash)
    if mask:
        new_mask = mask[:start_slice] + new_mask
    save_query_mask(query_hash, new_mask)

    end_time = time.time()
    log.info(f'Validated images in {end_time - start_time} ')


def _validation_failure(request, exception):
    log.warning(f'Failed to validate image! Reason: {exception}')

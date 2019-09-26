import time
import grequests
import logging
from django_redis import get_redis_connection

log = logging.getLogger(__name__)


def validate_images(image_urls, image_ids):
    """
    Return a list of image IDs that are no longer valid due to link rot.
    """
    if not image_urls:
        return []
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
        if verified[idx] is not None:
            status = verified[idx].status_code
        # Response didn't arrive in time. Try again later.
        else:
            status = -1
        to_cache[cache_key] = status

    five_minutes = 60 * 5
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
            pipe.expire(key, five_minutes)
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

    # Delete broken images from the search results response.
    broken_ids = []
    for idx, _ in enumerate(cached_statuses):
        status = cached_statuses[idx]
        if status == 429 or status == 403:
            log.warning(
                'Image validation failed due to rate limiting or blocking. '
                'Affected URL: {}'.format(image_urls[idx])
            )
        elif status != 200:
            log.info(
                'Broken link with id {} detected.'
                .format(image_ids[idx])
            )
            broken_ids.append(image_ids[idx])
    end_time = time.time()
    log.info('Validated images in {} '.format(end_time - start_time))
    return broken_ids


def _validation_failure(request, exception):
    log.warning('Failed to validate image! Reason: {}'.format(exception))

from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist
from django_redis import get_redis_connection
import logging as log
import time
"""
Decorators for tracking usage and page view statistics.

In order to protect the privacy of our users, special care must be taken to
ensure that IPs are retained for the minimum possible amount of time. These
statistics must only be used in aggregate and never to identify an individual
user.
"""


def track_model_views(model):
    """
    A decorator for tracking the number of times that a model is viewed. To
    prevent overcounting and abuse, repeated requests over a short interval
    from the same IP are not counted. Intended to be used on Django view
    functions.

    It is assumed that the model has a view_count field.

    Expects decorated function to have arguments 'request' and 'id'. The
    decorated function will then be passed a `view_count` as a keyword argument.

    :arg model: The type of object to track.
    :return:
    """
    def func_wrap(django_view):
        def decorated(*args, **kwargs):
            request = args[1]
            model_id = kwargs.get('id')
            view_count = _increment_viewcount(model, model_id, request)
            return django_view(*args, **kwargs, view_count=view_count)
        return decorated
    return func_wrap


def _increment_viewcount(model, model_id: int, request):
    """
    Increment the viewcount. Cache the result for at least 24 hours. When
    the key expires, it is evicted from the cache and stored in Postgres by a
    cache persistence worker.

    This strategy minimizes write load on the database while providing
    accurate real-time view statistics. The cache is also kept small as
    infrequently used data is evicted, reducing the need for memory.

    :return: The view count AFTER incrementing.
    """
    object_key = model.__name__ + ':' + str(model_id)

    redis = get_redis_connection('traffic_stats')
    view_count = redis.get(object_key)
    if not view_count:
        # Cache miss. Get the view count from the database and cache it.
        try:
            view_count = int(model.objects.get(id=model_id).view_count)
        except ObjectDoesNotExist:
            # If the object doesn't even exist in the database, don't track it.
            return
        except FieldDoesNotExist:
            log.error(
                'Cannot track model {} because it has no view_count field. '
                'Views for this model will be lost.'.format(model.__name__)
            )
            return -1
        redis.set(object_key, view_count)
    else:
        view_count = int(view_count)

    # Only increment the view count if the user has not visited the resource in
    # the last few minutes. Prevents metrics gaming shenanigans.
    ip = _get_user_ip(request)
    if not _is_recent_visitor(ip, object_key):
        redis.incr(object_key)
        view_count += 1
    _mark_recent_visitor(ip, object_key)

    # Update the last access time of the model.
    # Store in a sorted set so we can easily find the oldest keys.
    timestamp = time.time()
    redis.execute_command(
        'ZADD model-last-accessed {} {}'.format(timestamp, object_key)
    )
    return view_count


def _get_user_ip(request):
    """
    Read request headers to find the correct IP address.

    It is assumed that X-Forwarded-For has been sanitized by the load balancer
    and thus cannot be rewritten by malicious users.

    :param request: A Django request object.
    :return: An IP address.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def _is_recent_visitor(ip, object_key):
    """
    Return True if a given `ip` was seen accessing an `object_key` in the last
    10 hours.

    Cleans out old IPs.
    :return: bool
    """
    redis = get_redis_connection('traffic_stats')
    recent_ips_key = object_key + '-recent-ips'
    # Delete all IPs that haven't visited the resource in the last 10 hours.
    ten_hours_ago = time.time() - (60 * 60 * 10)
    redis.zremrangebyscore(recent_ips_key, '-inf', ten_hours_ago)
    is_recent = bool(redis.zscore(recent_ips_key, ip))
    return is_recent


def _mark_recent_visitor(ip, object_key):
    """
    Mark a given IP as a recent visitor to a specific resource (such as an
    Image).

    A recent visitor is an IP address that has hit a resource in the last 10
    hours.
    """
    redis = get_redis_connection('traffic_stats')
    recent_ips_key = object_key + '-recent-ips'
    current_timestamp = time.time()
    redis.execute_command(
        'ZADD {} {} {}'.format(recent_ips_key, current_timestamp, ip)
    )

    # The visitor set will be automatically deleted if nobody has visited the
    # resource in the last 24 hours.
    one_day_seconds = 60 * 60 * 24
    redis.expire(recent_ips_key, one_day_seconds)

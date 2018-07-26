from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist
from django_redis import get_redis_connection
import logging as log
"""
Decorators for tracking usage and page view statistics.
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
            request = kwargs.get('request')
            model_id = kwargs.get('id')
            view_count = _increment_viewcount(model, model_id)
            return django_view(*args, **kwargs, view_count=view_count)
        return decorated
    return func_wrap


def _increment_viewcount(model, model_id: int):
    """
    Increment the viewcount. Cache the result for at least six hours. When
    the key expires, it is evicted from the cache and stored in Postgres by a
    cache persistence worker.

    This strategy minimizes write load on the database while providing
    accurate view statistics. The cache is also kept small as infrequently used
    data is evicted, reducing the need for memory.

    :return: The view count AFTER incrementing.
    """
    expire_seconds = 60 * 60 * 6
    view_count_key = model.__name__ + '$' + str(model_id)

    redis = get_redis_connection('traffic_stats')
    view_count = redis.get(view_count_key)
    if not view_count:
        # Cache miss. Get the view count from the database.
        try:
            view_count = model.objects.get(id=model_id).view_count
        except ObjectDoesNotExist:
            # If the object doesn't even exist in the database, don't track it.
            return
        except FieldDoesNotExist:
            log.error('Cannot track model ' + model.__name__ +
                      'because it has no view_count field. Page views for this' +
                      'model will be lost.')
            return
        redis.set(view_count_key, view_count + 1)
    else:
        # Cache hit.
        redis.incr(view_count_key)

    # Always reset cache expiry when the key is accessed.
    redis.expire(view_count_key, expire_seconds)
    return view_count


def _is_recent_visitor(ip, recent_seconds):
    """
    Return True if a given `ip` was seen in the last `recent_seconds`.
    :return: bool
    """
    pass


def _mark_recent_visitor(ip, recent_seconds):
    """
    Mark a given IP as a recent visitor. If it has already been marked, reset
    its expiration time.
    """
    pass

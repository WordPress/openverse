from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist
from django_redis import get_redis_connection
import logging as log
"""
Decorators for tracking usage and page view statistics.
"""


def track_model_views(model):
    """
    Track the number of times that a model is viewed. To prevent overcounting
    and abuse, don't count repeated requests over a short interval from the
    same IP. Intended to be used on Django view functions.

    Expects decorated function to have arguments 'request' and 'id'.

    :arg model: The type of object to track.
    :return:
    """
    def func_wrap(django_view):
        def decorated(*args, **kwargs):
            try:
                model._meta.get_field('view_count')
            except FieldDoesNotExist:
                log.error('Cannot track views on model ' + model.__name__ +
                          ': missing view_count field in database schema')
                django_view(*args, **kwargs)

            request = kwargs.get('request')
            model_id = kwargs.get('id')
            _increment_viewcount(model, model_id)
            return django_view(*args, **kwargs)
        return decorated
    return func_wrap


def _increment_viewcount(model, model_id: int):
    """
    Increment the viewcount. Cache the result for at least six hours. When
    the key expires, it is evicted from the cache and stored in Postgres by a
    cache persistence worker.
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
        redis.set(view_count_key, view_count + 1)
    else:
        # Cache hit.
        redis.incr(view_count_key)

    # Always reset cache expiry when the key is accessed.
    redis.expire(view_count_key, expire_seconds)


def is_recent_visitor(ip, recent_seconds):
    """
    Return True if a given `ip` was seen in the last `recent_seconds`.

    Mark the IP as a recent visitor.
    :param ip:
    :param recent_seconds:
    :return:
    """
    pass

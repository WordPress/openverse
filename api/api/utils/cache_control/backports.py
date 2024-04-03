"""
Backport Django 5 async route support for cache control decorator.

Delete me after updating the API to Django 5.

Code in this file is under the Django BSD 3-Clause license.

https://github.com/django/django/blob/main/LICENSE
"""
from asgiref.sync import iscoroutinefunction
from functools import wraps

from django.utils.cache import patch_cache_control, add_never_cache_headers


def _check_request(request, decorator_name):
    """
    Check view return type looks correct.

    Upstream version of the backported code:
    https://github.com/django/django/blob/8665cf03d79c4b6222514c5943ccf3863a19cf08/django/views/decorators/cache.py#L31-L37
    """
    # Ensure argument looks like a request.
    if not hasattr(request, "META"):
        raise TypeError(
            f"{decorator_name} didn't receive an HttpRequest. If you are "
            "decorating a classmethod, be sure to use @method_decorator."
        )


def cache_control(**kwargs):
    """
    Add `cache-control` headers to response from decorated views.

    Upstream version of the backported code:
    https://github.com/django/django/blob/8665cf03d79c4b6222514c5943ccf3863a19cf08/django/views/decorators/cache.py#L40-L60
    """
    def _cache_controller(viewfunc):
        if iscoroutinefunction(viewfunc):

            async def _view_wrapper(request, *args, **kw):
                _check_request(request, "cache_control")
                response = await viewfunc(request, *args, **kw)
                patch_cache_control(response, **kwargs)
                return response

        else:

            def _view_wrapper(request, *args, **kw):
                _check_request(request, "cache_control")
                response = viewfunc(request, *args, **kw)
                patch_cache_control(response, **kwargs)
                return response

        return wraps(viewfunc)(_view_wrapper)

    return _cache_controller


def never_cache(view_func):
    """
    Decorator that adds headers to a response so that it will never be cached.

    Upstream version of the backported code:
    https://github.com/django/django/blob/8665cf03d79c4b6222514c5943ccf3863a19cf08/django/views/decorators/cache.py#L63-L84
    """

    if iscoroutinefunction(view_func):

        async def _view_wrapper(request, *args, **kwargs):
            _check_request(request, "never_cache")
            response = await view_func(request, *args, **kwargs)
            add_never_cache_headers(response)
            return response

    else:

        def _view_wrapper(request, *args, **kwargs):
            _check_request(request, "never_cache")
            response = view_func(request, *args, **kwargs)
            add_never_cache_headers(response)
            return response

    return wraps(view_func)(_view_wrapper)

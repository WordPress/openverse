from functools import wraps

from api.utils.cache_control.backports import cache_control, never_cache  # noqa: E501


def async_method_cache_control(**cache_control_kwargs):
    """
    Decorate an async method with `cache_control`.

    Only necessary for async view methods because Django's `method_decorator`
    does not work for async methods.
    """

    def do(async_method_view):

        @wraps(async_method_view)
        async def wrapper(self, *args, **kwargs):
            @cache_control(**kwargs)
            async def selfless_view_func(*inner_args, **inner_kwargs):
                return await async_method_view(self, *inner_args, **inner_kwargs)

            return await selfless_view_func(*args, **kwargs)

        return wrapper

    return do

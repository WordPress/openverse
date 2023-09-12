import functools
from inspect import _ParameterKind, signature
from typing import Any

from common.constants import SQL_INFO_BY_MEDIA_TYPE


def setup_kwargs_for_media_type(
    values_by_media_type: dict[str, Any], kwarg_name: str
) -> callable:
    """
    Create a decorator which provides media_type-specific information as parameters
    for the called function. The called function must itself have a media_type kwarg,
    which is used to select values.

    Required arguments:

    values_by_media_type: A dict mapping media types to arbitrary values, which may
                          themselves be of any type
    kwarg_name:           The name of the kwarg that will be passed to the called
                          function

    Usage example:

    @setup_kwargs_for_media_type(MY_VALS_BY_MEDIA_TYPE, 'foo')
    def my_fun(media_type, foo = None):
        ...

    When `my_fun` is called, if the `foo` kwarg is not passed explicitly, it will be set
    to the value of MY_VALS_BY_MEDIA_TYPE[media_type]. An error is raised for an invalid
    media type.
    """

    def wrap(func: callable) -> callable:
        """
        Provide the appropriate value for the media_type passed in the called function.
        If the called function is already explicitly passed a value for `kwarg_name`,
        use that value instead.
        """

        # The called function must be supplied a `media_type` keyword-only argument. It
        # cannot allow the value to be supplied as a positional argument.
        if (
            media_type := signature(func).parameters.get("media_type")
        ) is None or media_type.kind != _ParameterKind.KEYWORD_ONLY:
            raise Exception(
                f"Improperly configured function `{func.__qualname__}`:"
                " `media_type` must be a keyword-only argument."
            )

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            # First check to see if the called function was already passed a value
            # for the given kwarg name. If so, simply use this.
            if (media_info := kwargs.pop(kwarg_name, None)) is None:
                # The called function should be passed a `media_type`, whose value
                # is a key in the values dict
                media_type = kwargs.get("media_type", None)

                if media_type not in values_by_media_type.keys():
                    raise ValueError(
                        f"{func.__qualname__}: No values matching media type"
                        f" `{media_type}`"
                    )

                # Get the value corresponding to the media type
                media_info = values_by_media_type.get(media_type)

            # Add the media-type-specific info to kwargs, using the passed kwarg name
            kwargs[kwarg_name] = media_info
            return func(*args, **kwargs)

        return wrapped

    return wrap


def setup_sql_info_for_media_type(func: callable) -> callable:
    """Provide media-type-specific SQLInfo as a kwarg to the decorated function."""
    return setup_kwargs_for_media_type(SQL_INFO_BY_MEDIA_TYPE, "sql_info")(func)

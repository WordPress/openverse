from django import template

from api.utils.url import add_protocol


register = template.Library()


@register.filter
def safe_href(value):
    """Return a provider URL fit for an ``href``, or an empty string if it is not."""

    return add_protocol(value) or ""

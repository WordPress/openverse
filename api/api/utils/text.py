"""
Strip HTML markup from provider-supplied text.

This module is kept byte-identical in the catalog and the API so both sides
apply exactly the same rule.
"""

import html
import re
from html.parser import HTMLParser


# A tag opener that never closes is still a tag once the value is embedded in a
# page, so it is removed rather than kept as text.
_UNTERMINATED_TAG = re.compile(r"<(?=[A-Za-z/!?])[^>]*\Z")


class _TagStripper(HTMLParser):
    """Drop every tag, comment and declaration, keeping only the decoded text."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data):
        self.parts.append(data)


def _strip_tags(value: str) -> str:
    while "<" in value and ">" in value:
        stripper = _TagStripper()
        stripper.feed(value)
        stripper.close()
        stripped = "".join(stripper.parts)
        if stripped == value:
            break
        value = stripped
    return _UNTERMINATED_TAG.sub("", value)


def _decode_entities(value: str) -> str:
    previous = None
    while value != previous:
        previous = value
        value = html.unescape(value)
    return value


def strip_markup(value: str | None) -> str | None:
    """
    Remove HTML markup from a free-text metadata value such as a title or creator.

    Entities are decoded and tags stripped repeatedly until the value is stable,
    so entity-encoded markup is removed the same way as literal markup.

    A value that contains no markup is returned unchanged, entities included.
    Exact-match lookups against stored values, such as creator collections,
    depend on a value only being rewritten when markup was actually removed.
    """
    if not value:
        return value
    decoded = _decode_entities(value)
    plain = decoded
    previous = None
    while plain != previous:
        previous = plain
        plain = _strip_tags(html.unescape(plain))
    if plain == decoded:
        return value
    return " ".join(plain.split())

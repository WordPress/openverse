import re
from urllib.parse import quote, unquote


def convert_grp(grp: str) -> str | None:
    """
    Convert a hex value into a character. Return None if the conversion results in
    a character that cannot be used as a URI component.
    """
    try:
        converted = chr(int(grp, 16))
        # Decoded strings should be usable as URI components
        quote(converted)
        return converted
    except UnicodeEncodeError:
        return None


def decode_data(data: str | None = "") -> str:
    if not data:
        return ""

    regexes = [
        r"\\(x)([\da-f]{2})",  # \\xe9 - é
        r"\\(u)([\da-f]{4})",  # \\u00e9 - é
        r"(u)([\da-f]{4})",  # u00e9 - é
    ]

    def replace_func(match):
        """Replace the matched group with the converted character if possible, otherwise return the original string."""
        prefix, grp = match.groups()
        if converted := convert_grp(grp):
            return converted
        return f"{prefix}{grp}"

    for regex in regexes:
        data = re.sub(regex, replace_func, data, flags=re.IGNORECASE)

    return unquote(data)


def clean_tags(tags: list[dict]) -> list[dict]:
    """Decode tag names and then remove duplicate tags."""
    for tag in tags:
        tag["name"] = decode_data(tag["name"])
    seen = set()
    unique_tags = []
    for i, tag in enumerate(tags):
        tag_tuple = (tag["name"], tag.get("provider"), tag.get("accuracy"))
        if tag_tuple not in seen:
            seen.add(tag_tuple)
            unique_tags.append(tag)
    return unique_tags

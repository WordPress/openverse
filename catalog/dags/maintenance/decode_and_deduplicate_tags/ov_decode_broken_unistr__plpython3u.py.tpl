import re
from typing import Union
from urllib.parse import quote, unquote


DOUBLE_BACKSLASH_ESCAPE = re.compile(
    r"{DOUBLE_BACKSLASH_ESCAPE}", re.IGNORECASE
)
NO_BACKSLASH_ESCAPE = re.compile(r"{NO_BACKSLASH_ESCAPE}", re.IGNORECASE)


def convert_grp(grp: str) -> Union[str, None]:
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


def replace_func(match):
    """Replace the matched group with the converted character if possible, otherwise return the original string."""
    prefix, grp = match.groups()
    if converted := convert_grp(grp):
        return converted
    return f"{{prefix}}{{grp}}"


def decode_data(data: Union[str, None] = "") -> str:
    if not data:
        return ""

    # Handle characters encoded with double backslashes
    if DOUBLE_BACKSLASH_ESCAPE.search(data):
        try:
            decoded_data = data.encode().decode("unicode_escape")
            data = decoded_data
        except (UnicodeDecodeError, UnicodeEncodeError):
            plpy.debug(f"Failed to decode data with double backslash: {{data}}")
    # Handle characters encoded without backslashes
    data = re.sub(NO_BACKSLASH_ESCAPE, replace_func, data)

    return unquote(data)


return decode_data({ARGUMENT_NAME})

from urllib.parse import urlparse


def add_protocol(url: str) -> str:
    """
    Add protocol to URLs that lack them.

    Some fields in the database contain incomplete URLs, leading to unexpected
    behavior in downstream consumers. This helper verifies that we always
    return fully formed URLs in such situations.

    :param url: the URL to check and add scheme
    :return: the URL with the existing scheme, or ``https`` if one did not exist
    """

    parsed = urlparse(url)
    if parsed.scheme == "":
        return f"https://{url}"
    else:
        return url

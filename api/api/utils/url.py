from urllib.parse import urlparse


SAFE_SCHEMES = {"http", "https", "mailto"}


def add_protocol(url: str | None) -> str | None:
    """
    Add protocol to URLs that lack them and drop URLs with unsafe schemes.

    Some fields in the database contain incomplete URLs, leading to unexpected
    behavior in downstream consumers. This helper verifies that we always
    return fully formed URLs in such situations. Consumers place these URLs
    in ``href`` attributes, so anything other than ``http``, ``https`` and
    ``mailto``, such as ``javascript:``, is dropped rather than passed through.

    :param url: the URL to check and add scheme
    :return: the URL with the existing scheme, ``https`` if one did not exist,
        or ``None`` if the scheme is not safe to link to
    """

    url = url.strip() if url else ""
    if not url:
        return None
    if url.startswith("//"):
        return f"https:{url}"
    scheme = urlparse(url).scheme
    # A host with a port but no scheme, like ``example.com:8080/a``, parses with
    # the host as its scheme.
    if scheme == "" or "." in scheme:
        return f"https://{url}"
    if scheme not in SAFE_SCHEMES:
        return None
    return url

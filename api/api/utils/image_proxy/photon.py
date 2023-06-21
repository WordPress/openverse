from django.conf import settings


def get_photon_request_params(
    parsed_image_url,
    is_full_size: bool,
    is_compressed: bool,
    headers: dict,
):
    """
    Photon options documented here:
    https://developer.wordpress.com/docs/photon/api/
    """
    params = {}

    if not is_full_size:
        params["w"] = settings.THUMBNAIL_WIDTH_PX

    if is_compressed:
        params["quality"] = settings.THUMBNAIL_QUALITY

    if parsed_image_url.query:
        # No need to URL encode this string because requests will already
        # pass the `params` object to `urlencode` before it appends it to the
        # request URL.
        params["q"] = parsed_image_url.query

    if parsed_image_url.scheme == "https":
        # Photon defaults to HTTP without this parameter
        # which will cause some providers to fail (if they
        # do not serve over HTTP and do not have a redirect)
        params["ssl"] = "true"

    # Photon excludes the protocol, so we need to reconstruct the url + port + path
    # to send as the "path" of the Photon request
    domain = parsed_image_url.netloc
    path = parsed_image_url.path
    upstream_url = f"{settings.PHOTON_ENDPOINT}{domain}{path}"

    if settings.PHOTON_AUTH_KEY:
        headers["X-Photon-Authentication"] = settings.PHOTON_AUTH_KEY

    return upstream_url, params, headers

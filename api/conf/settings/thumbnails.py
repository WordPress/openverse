from datetime import timedelta

from decouple import config


# If key is not present then the authentication header won't be sent
# and query forwarding will not work as expected. Lack of query forwarding
# is not an issue for local development so this compromise is okay.
PHOTON_AUTH_KEY = config("PHOTON_AUTH_KEY", default=None)

# Produce CC-hosted thumbnails dynamically through a proxy.
PHOTON_ENDPOINT = config("PHOTON_ENDPOINT", default="https://i0.wp.com/")

# These do not need to be cast to int because we don't use them directly,
# they're just passed through to Photon's API
# Keeping them as strings makes the tests slightly less verbose (for not needing
# to cast them in assertions to match the parsed param types)
THUMBNAIL_WIDTH_PX = config("THUMBNAIL_WIDTH_PX", default="600", cast=int)
THUMBNAIL_QUALITY = config("THUMBNAIL_JPG_QUALITY", default="80")

# The length of time to cache repeated thumbnail failures
THUMBNAIL_FAILURE_CACHE_WINDOW_SECONDS = config(
    "THUMBNAIL_FAILURE_CACHE_WINDOW_SECONDS",
    default=int(timedelta(days=2).total_seconds()),
    cast=int,
)

# The number of times to try a thumbnail request before caching a failure
THUMBNAIL_FAILURE_CACHE_TOLERANCE = config(
    "THUMBNAIL_FAILURE_CACHE_TOLERANCE", default=2, cast=int
)

# Timeout when requesting the thumbnail from the upstream image proxy
THUMBNAIL_UPSTREAM_TIMEOUT = config("THUMBNAIL_UPSTREAM_TIMEOUT", default=4, cast=int)

# Timeout when trying to determine the filetype based on a HEAD request to the upstream image provider
THUMBNAIL_EXTENSION_REQUEST_TIMEOUT = config(
    "THUMBNAIL_EXTENSION_REQUEST_TIMEOUT", default=4, cast=int
)

# Use Wikimedia's thumbnail endpoint when requesting thumbnails from Site Accelerator (formerly Photon)
USE_WIKIMEDIA_THUMBNAIL_ENDPOINT = config(
    "USE_WIKIMEDIA_THUMBNAIL_ENDPOINT", default=True, cast=bool
)

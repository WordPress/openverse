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
THUMBNAIL_WIDTH_PX = config("THUMBNAIL_WIDTH_PX", default="600")
THUMBNAIL_QUALITY = config("THUMBNAIL_JPG_QUALITY", default="80")

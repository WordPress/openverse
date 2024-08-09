from math import inf
from urllib.parse import ParseResult

from django.conf import settings

from api.utils.image_proxy.dataclasses import MediaInfo, RequestConfig


# e.g.:
# https://upload.wikimedia.org/wikipedia/commons/9/9e/Color_icon_yellow.svg
# https://upload.wikimedia.org/wikipedia/commons/f/f3/Open_book_01.svg
# The length of the hashes is constant
# For each example, the thumbnail URL is:
# https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Color_icon_yellow.svg/<WIDTH>px-Color_icon_yellow.svg.jpg
# https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Open_book_01.svg/<WIDTH>px-Open_book_01.svg.jpg
WIKIMEDIA_PATH_PREFIX = "/wikimedia/commons/"


def get_wikimedia_thumbnail_url(
    media_info: MediaInfo, url: ParseResult, request_config: RequestConfig
) -> ParseResult:
    hash_a, hash_b, filename = url.path[len(WIKIMEDIA_PATH_PREFIX) :].split(
        "/", maxsplit=2
    )

    if request_config.is_full_size and media_info.width:
        width = media_info.width
    else:
        # either not full size or there is no width defined
        # if no width is defined, use the default thumbnail size (by falling back to infinity for the media_info.width)
        # otherwise, use whichever is smallest, so that Wikimedia does not upscale the image
        width = min(settings.THUMBNAIL_WIDTH_PX, media_info.width or inf)

    params = f"{width}px"

    if request_config.is_compressed:
        params = f"lossy-{params}"

    # always retrieve a PNG, and Site Accelerator will convert it as necessary based on the accept headers
    return url._replace(
        path=f"{WIKIMEDIA_PATH_PREFIX}thumb/{hash_a}/{hash_b}/{filename}/{params}-{filename}.png"
    )

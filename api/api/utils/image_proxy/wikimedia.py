import re
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
# A regex is slightly more reliable for this in case for some reason wikipedia/commons is not a constant prefix
# or the filename somehow has an additional `/` in it (though that does not appear to be possible)
WIKIMEDIA_PATH_PARSE = re.compile(
    r"^(?P<path_prefix>.*?)(?P<hash>/[a-z0-9]{1}/[a-z0-9]{2}/)(?P<filename>.*)$"
)


def get_wikimedia_thumbnail_url(
    media_info: MediaInfo, url: ParseResult, request_config: RequestConfig
) -> ParseResult | None:
    path_match = WIKIMEDIA_PATH_PARSE.match(url.path)
    if path_match is None:
        return None

    groups = path_match.groupdict()

    if request_config.is_full_size:
        width = media_info.width or settings.THUMBNAIL_WIDTH_PX
    else:
        # If not full size, prevent Wikimedia from upscaling the image by using the smaller of
        # the default thumbnail size or media_info.width
        # Wikimedia _requires_ sending a width, so there's no other fallback than the default thumbnail size
        width = min(settings.THUMBNAIL_WIDTH_PX, media_info.width or inf)

    params = f"{width}px"

    if request_config.is_compressed:
        params = f"lossy-{params}"

    # always retrieve a PNG, and Site Accelerator will convert it as necessary based on the accept headers
    return url._replace(
        path=f"{groups['path_prefix']}/thumb{groups['hash']}{groups['filename']}/{params}-{groups['filename']}.png"
    )

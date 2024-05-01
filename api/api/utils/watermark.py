import logging
import os
from enum import Flag, auto
from io import BytesIO
from textwrap import wrap

from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import APIException

import requests
from openverse_attribution.license import License
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
from sentry_sdk import capture_exception


parent_logger = logging.getLogger(__name__)


BREAKPOINT_DIMENSION = 400  # 400px
MARGIN_RATIO = 0.04  # 4%
FONT_RATIO = 0.04  # 4%

FRAME_COLOR = "#fff"  # White frame
TEXT_COLOR = "#000"  # Black text
HEADERS = {
    "User-Agent": settings.OUTBOUND_USER_AGENT_TEMPLATE.format(purpose="Watermark")
}


class UpstreamWatermarkException(APIException):
    status_code = status.HTTP_424_FAILED_DEPENDENCY
    default_detail = (
        "Could not render watermarked image due to upstream provider error."
    )
    default_code = "upstream_watermark_failure"


class Dimension(Flag):
    """This enum represents the two dimensions of an image."""

    HEIGHT = auto()
    WIDTH = auto()
    BOTH = HEIGHT | WIDTH
    NONE = 0


# Utils


def _smaller_dimension(width, height):
    """
    Determine which image dimensions are below the breakpoint dimensions.

    :param width: the width of the image
    :param height: the height of the image
    :return: True if the image is small, False otherwise
    """

    smaller_dimension = Dimension.NONE
    if width < BREAKPOINT_DIMENSION:
        smaller_dimension = smaller_dimension | Dimension.WIDTH
    if height < BREAKPOINT_DIMENSION:
        smaller_dimension = smaller_dimension | Dimension.HEIGHT
    return smaller_dimension


def _get_font_path(monospace=False):
    """
    Return the path to the TTF font file.

    :param monospace: True for monospaced font, False for variable-width font
    :return: the path to the TTF font file
    """

    font_name = "SourceCodePro-Bold.ttf" if monospace else "SourceSansPro-Bold.ttf"
    font_path = os.path.join(os.path.dirname(__file__), "fonts", font_name)

    return font_path


def _fit_in_width(text, font, max_width):
    """
    Break the given text so that it fits in the given space.

    :param text: the text to fit in the limited width
    :param font: the font containing size and other info
    :param max_width: the maximum width the text is allowed to take
    :return: the fitted text
    """

    char_length = font.getlength("x")  # x has the closest to average width
    max_chars = int(
        max_width // char_length
    )  # Must be an integer to be used with `wrap` below

    text = "\n".join(["\n".join(wrap(line, max_chars)) for line in text.split("\n")])

    return text


# Framing


def _create_frame(dimensions):
    """
    Create a frame with the given dimensions.

    :param dimensions: a tuple containing the width and height of the frame
    :return: a white frame with the given dimensions
    """

    return Image.new("RGB", dimensions, FRAME_COLOR)


def _frame_image(image, frame, left_margin, top_margin):
    """
    Fix the image in the frame with the specified spacing.

    :param image: the image to frame
    :param frame: the frame in which to fit the image
    :param left_margin: the margin to the left of the image
    :param top_margin: the margin to the top of the image
    :return: the framed image
    """

    frame.paste(image, (left_margin, top_margin))
    return frame


# Attribution


def _get_attribution_height(text, font):
    draw = ImageDraw.Draw(Image.new("RGB", (0, 0)))
    _, _, _, height = draw.multiline_textbbox((0, 0), text, font)
    return height


# Actions


def _open_image(url):
    """
    Read an image from a URL and convert it into a PIL Image object.

    :param url: the URL from where to read the image
    :return: the PIL image object with the EXIF data
    """
    logger = parent_logger.getChild("_open_image")
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        img_bytes = BytesIO(response.content)
        img = Image.open(img_bytes)
    except requests.exceptions.RequestException as e:
        capture_exception(e)
        logger.error(f"Error requesting image: {e}")
        raise UpstreamWatermarkException(f"{e}")
    except UnidentifiedImageError as e:
        capture_exception(e)
        logger.error(f"Error loading image data: {e}")
        raise UpstreamWatermarkException(f"{e}")

    return img, img.getexif()


def _print_attribution_on_image(img: Image.Image, image_info):
    """
    Add a frame around the image and put the attribution text on the bottom.

    :param img: the image to frame and attribute
    :param image_info: the information about a particular image
    :return: return the framed and attributed image
    """

    try:
        lic = License(image_info["license"], image_info["license_version"])
    except ValueError:
        return img

    width, height = img.size
    smaller_dimension = _smaller_dimension(width, height)

    if smaller_dimension is Dimension.NONE:
        margin = round(MARGIN_RATIO * min(width, height))
        font_size = round(FONT_RATIO * min(width, height))
        new_width = width
    else:
        margin = round(MARGIN_RATIO * BREAKPOINT_DIMENSION)
        font_size = round(FONT_RATIO * BREAKPOINT_DIMENSION)
        new_width = (
            BREAKPOINT_DIMENSION if Dimension.WIDTH in smaller_dimension else width
        )

    font = ImageFont.truetype(_get_font_path(), size=font_size)

    text = lic.get_attribution_text(
        image_info["title"],
        image_info["creator"],
        url=False,
    )
    text = _fit_in_width(text, font, new_width)
    attribution_height = _get_attribution_height(text, font)

    frame_width = margin + new_width + margin
    frame_height = margin + height + margin + attribution_height + margin
    left_margin = (frame_width - width) // 2

    frame = _create_frame(
        (
            frame_width,
            frame_height,
        )
    )
    _frame_image(img, frame, left_margin, margin)

    draw = ImageDraw.Draw(frame)
    text_position_x = margin
    text_position_y = margin + height + margin
    draw.text(
        xy=(
            text_position_x,
            text_position_y,
        ),
        text=text,
        font=font,
        fill=TEXT_COLOR,
    )

    return frame


def watermark(image_url, info, draw_frame=True):
    """
    Return a PIL Image with a watermark and embedded metadata.

    :param image_url: The URL of the image.
    :param info: A dictionary with keys title, creator, license, and
    license_version
    :param draw_frame: Whether to draw an attribution frame.
    :returns: A PIL Image and its EXIF data, if included.
    """

    img, exif = _open_image(image_url)
    if not draw_frame:
        return img, exif
    frame = _print_attribution_on_image(img, info)
    return frame, exif

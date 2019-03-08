import requests
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw

horizontal_margin = 100
vertical_margin = 200
frame_color = '#fff'
text_color = '#000'


def _open_image(url):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img
    except requests.exceptions.RequestException:
        print('Error loading image data')


def _create_frame_for_image(image):
    """
    creates an image as a frame for another image
    """
    size = image.size
    width = size[0]
    height = size[1]
    img = Image.new(
        "RGB",
        (width + horizontal_margin, height + vertical_margin),
        frame_color
    )
    return img


def _place_image_inside_frame(image):
    frame = _create_frame_for_image(image)
    copy = image.copy()
    top_margin = int(vertical_margin / 4)
    left_margin = int(horizontal_margin / 2)
    frame.paste(copy, (left_margin, top_margin))

    return frame


def _full_license(image_info):
    _license = image_info['license'].upper()
    license_version = image_info['license_version'].upper()
    license_text = "{0} {1}".format(_license, license_version)
    return license_text if _license == "cc0" else "CC {0}".format(license_text)


def _print_attribution_for_image_on_frame(image_info, image, frame):
    vertical_margin_to_image = 16 # vertical margin between image and text

    font = ImageFont.truetype('DejaVuSans-Bold.ttf', size=18)
    draw = ImageDraw.Draw(frame)
    text_position_x = int(horizontal_margin / 2)
    text_position_y = \
        int(vertical_margin / 4) + image.size[1] + vertical_margin_to_image

    title = image_info['title']
    creator = image_info['creator']
    _license = _full_license(image_info)
    text = "{0}\nBy: {1}\nLicensed under: {2}".format(title, creator, _license)
    draw.text(
        xy=(text_position_x, text_position_y),
        text=text,
        font=font,
        fill=(0, 0, 0)
    )


def watermark(image_url, info):
    """
    creates the watermark for the image.
    Returns a BytesIO object with the image contents

    image: Image DB model
    """
    img = _open_image(image_url)
    frame = _place_image_inside_frame(img)
    _print_attribution_for_image_on_frame(info, img, frame)
    return frame


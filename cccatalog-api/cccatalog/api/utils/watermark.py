import json
import requests
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw

horizontal_margin = 100
vertical_margin = 200
frame_color = '#fff'
text_color = '#000'
base_url = 'https://api.creativecommons.engineering/image/'

def get_image_info(image_id):
    """
    gets the image data from the API, if necessary
    """
    try:
        r = requests.get(base_url + image_id, verify=False)
        response = json.loads(r.text)
        return response
    except requests.exceptions.RequestException:
        print('Error loading image data')

def open_image(url):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img
    except requests.exceptions.RequestException:
        print('Error loading image data')

def create_frame_for_image(image):
    """
    creates an image as a frame for another image
    """
    size = image.size
    width = size[0]
    height = size[1]
    img = Image.new("RGB", (width + horizontal_margin, height + vertical_margin), frame_color)
    return img

def place_image_inside_frame(image):
    frame = create_frame_for_image(img)
    copy = image.copy()
    top_margin = int(vertical_margin / 4)
    left_margin = int(horizontal_margin / 2)
    frame.paste(copy, (left_margin, top_margin))

    return frame

def full_license(image_info):
    license = image_info.license.upper()
    license_version = image_info.license_version.upper()
    license_text = "{0} {1}".format(license, license_version)
    return license_text if license == "cc0" else "CC {0}".format(license_text)

def print_attribution_for_image_on_frame(image_info, image, frame):
    vertical_margin_to_image = 16 # vertical margin between image and text

    font = ImageFont.truetype('SourceSansPro-Bold.ttf', size=18)
    draw = ImageDraw.Draw(frame)
    text_position_x = int(horizontal_margin / 2)
    text_position_y = int(vertical_margin / 4) + image.size[1] + vertical_margin_to_image

    title = image_info.title
    creator = image_info.creator
    license = full_license(image_info)

    draw.text(
        xy = (text_position_x, text_position_y),
        text = "{0}\nBy: {1}\nLicensed under: {2}".format(title, creator, license),
        font = font,
        fill = (0, 0, 0)
    )

def watermark(image):
    """
    creates the watermark for the image
    image: Image DB model
    """
    img = open_image(image.url)
    frame = place_image_inside_frame(img)
    print_attribution_for_image_on_frame(info, img, frame)
    io = BytesIO()
    frame.save(io, format="JPEG")


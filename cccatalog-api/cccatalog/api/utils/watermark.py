from PIL import Image, ImageFont, ImageDraw

images = ['portrait.jpg', 'square.jpg', 'panorama.jpg']

horizontal_margin = 100
vertical_margin = 200
frame_color = '#fff'
text_color = '#000'

def open_image(path):
    return Image.open(path)

def create_frame_for_image(image):
    """
    creates an image as a frame for another image
    """
    size = image.size
    width = size[0]
    height = size[1]
    img = Image.new("RGB", (width + horizontal_margin, height + vertical_margin), frame_color)
    return img

def place_image_inside_frame(image, frame):
    copy = image.copy()
    top_margin = int(vertical_margin / 4)
    left_margin = int(horizontal_margin / 2)
    frame.paste(copy, (left_margin, top_margin))

def print_attribution_for_image_on_frame(image, frame):
    vertical_margin_to_image = 16 # vertical margin between image and text

    font = ImageFont.truetype('SourceSansPro-Bold.ttf', size=18)
    draw = ImageDraw.Draw(frame)
    text_position_x = int(horizontal_margin / 2)
    text_position_y = int(vertical_margin / 4) + image.size[1] + vertical_margin_to_image

    draw.text(
        xy = (text_position_x, text_position_y),
        text = "Released to Public: Space Shuttle Discovery Catches a Ride by Lori Losey/NASA, August 19, 2005 (NASA))\npingnews.com\nCC pdm 1.0",
        font = font,
        fill = (0, 0, 0)
    )

for image_path in images:
    img = open_image(image_path)
    frame = create_frame_for_image(img)
    place_image_inside_frame(img, frame)
    print_attribution_for_image_on_frame(img, frame)
    frame.show()

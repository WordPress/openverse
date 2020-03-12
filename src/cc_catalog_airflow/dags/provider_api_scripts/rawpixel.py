from common.storage.image import ImageStore
from common.requester import DelayedRequester
import requests
import time
import logging
import json
from urllib.parse import urlparse, parse_qs

DELAY = 1.0  # time delay (in seconds)
PROVIDER = "rawpixel"
FILE = "rawpixel_{}.tsv".format(int(time.time()))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

delayed_requester = DelayedRequester(DELAY)
image_store = ImageStore(provider=PROVIDER, output_file=FILE)


def request_content(_url, _query_params=None, _headers=None):
    logging.info("Processing request: {}".format(_url))

    response = delayed_requester.get(
        _url, params=_query_params, headers=_headers
    )

    try:
        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            logging.warning(
                "Unable to request URL: {}. Status code: {}".format(
                    _url, response.status_code
                )
            )
            return None

    except Exception as e:
        logging.error("There was an error with the request.")
        logging.info("{}: {}".format(type(e).__name__, e))
        return None


def get_image_list(_page=1):
    endpoint = "https://api.rawpixel.com/api/v1/search"
    query_params = {"freecc0": 1, "html": 0, "page": _page}
    request = request_content(endpoint, _query_params=query_params)

    if request.get("results"):
        return [request.get("total"), request.get("results")]

    else:
        return [None, None]


def get_foreign_id_url(_image):
    if _image.get("freecc0"):
        # get the image identifier
        foreign_id = _image.get("id", "")

        # get the landing page
        foreign_url = _image.get("url")

        if not foreign_url:
            logging.warning(
                "Landing page not detected for image ID: {}".format(foreign_id)
            )
        return [foreign_id, foreign_url]
    else:
        return [None, None]


def get_image_properties(_image, foreign_url):
    img_url = _image.get("image_opengraph")
    if img_url:
        # extract the dimensions from the query params because
        # the dimensions in the metadata are at times
        # inconsistent with the rescaled images
        query_params = urlparse(img_url)
        width = parse_qs(query_params.query).get("w", [])[0]  # width
        height = parse_qs(query_params.query).get("h", [])[0]  # height
        thumbnail = _image.get("image_400", "")
        return [img_url, width, height, thumbnail]
    else:
        logging.warning(f"Image not detected in URL: {foreign_url}")
        return [None, None, None, None]


def get_title_owner(_image):
    title = _image.get("image_title", "")
    owner = _image.get("artist_names", "")
    owner = owner.replace("(Source)", "").strip()
    return [title, owner]


def get_tags(_image):
    keywords = _image.get("keywords_raw")
    if keywords:
        keyword_list = keywords.split(",")
        keyword_list = [
            word.strip()
            for word in keyword_list
            if word.strip()
            not in ["cc0", "creative commons", "creative commons 0"]
        ]
        tags = [
            {"name": tag, "provider": "rawpixel"} for tag in keyword_list
        ]
        return tags
    else:
        return {}


def process_image_data(_image):
    start_time = time.time()

    # verify the license and extract the metadata
    license = "cc0"
    version = "1.0"

    foreign_id, foreign_url = get_foreign_id_url(_image)
    if not foreign_url:
        return None
    img_url, width, height, thumbnail = get_image_properties(_image, foreign_url)
    if not img_url:
        return None
    title, owner = get_title_owner(_image)
    tags = get_tags(_image)

    # TODO: How to get license_url, creator, creator_url, source?
    return image_store.add_item(
        foreign_landing_url=foreign_url,
        image_url=img_url,
        license_=license,
        license_version=str(version),
        foreign_identifier=str(foreign_id),
        width=str(width) if width else None,
        height=str(height) if height else None,
        title=title if title else None,
        raw_tags=json.dumps(tags, ensure_ascii=False) if bool(tags) else None,
    )


def main():
    page = 1
    img_ctr = 0
    is_valid = True

    logging.info("Begin: RawPixel API requests")

    total, result = get_image_list(page)

    while (img_ctr < total) and is_valid:
        logging.info("Processing page: {}".format(page))

        start_time = time.time()
        for img in result:
            total_images = process_image_data(img)
            img_ctr = total_images if total_images else img_ctr

        total_images = image_store.commit()

        page += 1
        total, result = get_image_list(page)

        if not result:
            is_valid = False

        if not total:
            total = 0
            is_valid = False

    logging.info("Total images: {}".format(img_ctr))
    logging.info("Terminated!")


if __name__ == "__main__":
    main()

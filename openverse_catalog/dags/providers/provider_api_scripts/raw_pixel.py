import logging
from urllib.parse import parse_qs, urlparse

import requests
from common.licenses import get_license_info
from common.loader import provider_details as prov
from common.requester import DelayedRequester
from common.storage.image import ImageStore


DELAY = 1.0  # time delay (in seconds)
PROVIDER = prov.RAWPIXEL_DEFAULT_PROVIDER

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

delayed_requester = DelayedRequester(DELAY)
image_store = ImageStore(provider=PROVIDER)


def _request_content(url, query_params=None, headers=None):
    logger.info(f"Processing request: {url}")

    response = delayed_requester.get(url, params=query_params, headers=headers)
    try:
        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            logger.warning(
                f"Unable to request URL: {url}. Status code: " f"{response.status_code}"
            )
            return None

    except Exception as e:
        logger.error("There was an error with the request.")
        logger.info(f"{type(e).__name__}: {e}")
        return None


def _get_image_list(page=1):
    endpoint = "https://api.rawpixel.com/api/v1/search"
    query_params = {"freecc0": 1, "html": 0, "page": page}
    request = _request_content(endpoint, query_params=query_params)

    if request and request.get("results"):
        return [request.get("total"), request.get("results")]

    else:
        return [None, None]


def _get_foreign_id_url(image):
    if image.get("freecc0"):
        # get the image identifier
        foreign_id = image.get("id", "")

        # get the landing page
        foreign_url = image.get("url")

        if not foreign_url:
            logger.warning(f"Landing page not detected for image ID: {foreign_id}")
        return [foreign_id, foreign_url]
    else:
        return [None, None]


def _get_image_properties(image, foreign_url):
    img_url = image.get("image_opengraph")
    if img_url:
        # extract the dimensions from the query params because
        # the dimensions in the metadata are at times
        # inconsistent with the rescaled images
        query_params = urlparse(img_url)
        width = parse_qs(query_params.query).get("w", [])[0]
        height = parse_qs(query_params.query).get("h", [])[0]
        thumbnail = image.get("image_400", "")
        return [img_url, width, height, thumbnail]
    else:
        logger.warning(f"Image not detected in URL: {foreign_url}")
        return [None, None, None, None]


def _get_title_owner(image):
    title = image.get("image_title", "")
    owner = image.get("artist_names", "")
    owner = owner.replace("(Source)", "").strip()
    return [title, owner]


def _get_meta_data(image):
    description = image.get("pinterest_description")
    meta_data = {}
    if description:
        meta_data["description"] = description
    return meta_data


def _get_tags(image):
    keywords = image.get("keywords_raw")
    if keywords:
        keyword_list = keywords.split(",")
        keyword_list = [
            word.strip()
            for word in keyword_list
            if word.strip() not in ["cc0", "creative commons", "creative commons 0"]
        ]
        return keyword_list
    else:
        return []


def _process_image_data(image):
    # verify the license and extract the metadata
    license_ = "cc0"
    version = "1.0"

    foreign_id, foreign_url = _get_foreign_id_url(image)
    if not foreign_url:
        return None
    img_url, width, height, thumbnail = _get_image_properties(image, foreign_url)
    if not img_url:
        return None
    title, owner = _get_title_owner(image)
    meta_data = _get_meta_data(image)
    tags = _get_tags(image)

    # TODO:How to get license_url, creator_url, source, watermarked?
    license_info = get_license_info(
        license_=license_,
        license_version=version,
    )
    return image_store.add_item(
        foreign_landing_url=foreign_url,
        image_url=img_url,
        license_info=license_info,
        foreign_identifier=str(foreign_id),
        width=str(width) if width else None,
        height=str(height) if height else None,
        title=title if title else None,
        meta_data=meta_data,
        raw_tags=tags,
        creator=owner,
        thumbnail_url=thumbnail,
    )


def _process_pages(total, result, page):
    img_ctr = 0
    is_valid = True

    if not total:
        total = 0
        is_valid = False

    while (img_ctr < total) and is_valid:
        logger.info(f"Processing page: {page}")

        for img in result:
            total_images = _process_image_data(img)
            img_ctr = total_images if total_images else img_ctr

        page += 1
        total, result = _get_image_list(page)

        if not result:
            is_valid = False

        if not total:
            total = 0
            is_valid = False

    return img_ctr


def main():
    page = 1

    logger.info("Begin: RawPixel API requests")

    total, result = _get_image_list(page)

    img_ctr = _process_pages(total, result, page=page)

    logger.info(f"Total images: {img_ctr}")

    image_store.commit()

    logger.info("Terminated!")


if __name__ == "__main__":
    main()

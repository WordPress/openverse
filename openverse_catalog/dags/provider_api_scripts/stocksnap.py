"""
Content Provider:       StockSnap

ETL Process:            Use the API to identify all CC-licensed images.

Output:                 TSV file containing the image, the respective
                        meta-data.

Notes:                  https://stocksnap.io/api/
                        No rate limit specified. No authentication required.
                        All images are licensed under CC0.
"""
import json
import logging

from common.licenses.licenses import get_license_info
from common.requester import DelayedRequester
from storage.image import ImageStore
from util.loader import provider_details as prov


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

DELAY = 1  # in seconds
RETRIES = 3
HOST = "stocksnap.io"
ENDPOINT = f"https://{HOST}/api/load-photos/date/desc"
CDN = "https://cdn.stocksnap.io/img-thumbs/960w"
PROVIDER = prov.STOCKSNAP_DEFAULT_PROVIDER
HEADERS = {
    "Accept": "application/json",
}
DEFAULT_QUERY_PARAMS = {}

delayed_requester = DelayedRequester(DELAY)
image_store = ImageStore(provider=PROVIDER)

license_url = "https://creativecommons.org/publicdomain/zero/1.0/"
license_info = get_license_info(license_url=license_url)


def main():
    """
    This script pulls all the data from the StockSnap and writes it into a
    .TSV file to be eventually read into our DB.
    """

    logger.info("Begin: StockSnap script")
    image_count = _get_items()
    image_store.commit()
    logger.info(f"Total images pulled: {image_count}")
    logger.info("Terminated!")


def _get_items():
    item_count = 0
    page_number = 1
    should_continue = True
    while should_continue:
        page_endpoint = f"{ENDPOINT}/{page_number}"
        batch_data = _get_batch_json(endpoint=page_endpoint)
        if isinstance(batch_data, list) and len(batch_data) > 0:
            item_count = _process_item_batch(batch_data)
            page_number += 1
        else:
            should_continue = False
    return item_count


def _get_batch_json(
    endpoint=ENDPOINT, headers=None, retries=RETRIES, query_params=None
):
    if headers is None:
        headers = HEADERS.copy()
    response_json = delayed_requester.get_response_json(
        endpoint, retries, query_params, headers=headers
    )
    if response_json is None:
        return None
    else:
        data = response_json.get("results")
        return data


def _process_item_batch(items_batch):
    for item in items_batch:
        item_meta_data = _extract_item_data(item)
        if item_meta_data is None:
            continue
        image_store.add_item(**item_meta_data)
    return image_store.total_items


def _extract_item_data(media_data):
    """
    Extract data for individual image.
    """
    try:
        foreign_id = media_data["img_id"]
    except (TypeError, KeyError, AttributeError):
        return None
    foreign_landing_url = f"https://{HOST}/photo/{foreign_id}"
    image_url, width, height = _get_image_info(media_data)
    if image_url is None:
        logger.info("Found no image url.")
        logger.info(f"{json.dumps(media_data, indent=2)}")
        return None
    title = _get_title(media_data)
    if title is None:
        logger.info("Found no image title.")
        logger.info(f"{json.dumps(media_data, indent=2)}")
        return None
    creator, creator_url = _get_creator_data(media_data)
    thumbnail = image_url
    metadata = _get_metadata(media_data)
    tags = _get_tags(media_data)

    return {
        "title": title,
        "creator": creator,
        "creator_url": creator_url,
        "foreign_identifier": foreign_id,
        "foreign_landing_url": foreign_landing_url,
        "image_url": image_url,
        "height": height,
        "width": width,
        "thumbnail_url": thumbnail,
        "license_info": license_info,
        "meta_data": metadata,
        "raw_tags": tags,
    }


def _get_image_info(item):
    width = item.get("img_width")
    height = item.get("img_height")
    img_id = item.get("img_id")
    image_url = f"{CDN}/{img_id}.jpg"
    return image_url, width, height


def _get_creator_data(item):
    """
    Get the author's name and website preferring their custom link over the
    StockSnap profile. The latter is used if the first is not found.
    """
    creator_name = item.get("author_name")
    if creator_name is None:
        return None, None
    creator_url = item.get("author_website")
    if creator_url is None or creator_url in [
        "https://stocksnap.io/",
        "https://stocksnap.io/author/undefined/",
    ]:
        creator_url = item.get("author_profile")
    return creator_name, creator_url


def _get_title(item):
    """
    Get the first two photo's tags/keywords to make the title and transform it
    to title case, as shown on its page.
    """
    tags = item.get("keywords", [])[:2]
    if len(tags) > 0:
        tags.append("Photo")
        img_title = " ".join(tags)
        return img_title.title()


def _get_metadata(item):
    """
    Include popularity statistics.
    """
    extras = ["downloads", "page_views", "favorites"]
    metadata = {}
    for key in extras:
        value = item.get(key)
        if value is not None:
            metadata[key] = value
    return metadata


def _get_tags(item):
    return item.get("keywords")


if __name__ == "__main__":
    main()

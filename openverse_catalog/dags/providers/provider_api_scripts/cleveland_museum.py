import logging
from typing import Dict, List

from common.licenses import get_license_info
from common.loader import provider_details as prov
from common.requester import DelayedRequester
from common.storage.image import ImageStore


LIMIT = 1000
DELAY = 5.0
RETRIES = 3
PROVIDER = prov.CLEVELAND_DEFAULT_PROVIDER
ENDPOINT = "http://openaccess-api.clevelandart.org/api/artworks/"
CC0_LICENSE = get_license_info(license_="cc0", license_version="1.0")

delay_request = DelayedRequester(delay=DELAY)
image_store = ImageStore(provider=PROVIDER)

DEFAULT_QUERY_PARAMS = {"cc": "1", "has_image": "1", "limit": LIMIT, "skip": 0}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Begin: Cleveland Museum API requests")
    condition = True
    offset = 0

    while condition:
        query_param = _build_query_param(offset)
        response_json, total_images = _get_response(query_param)
        if response_json is not None and total_images != 0:
            batch = response_json["data"]
            image_count = _handle_response(batch)
            logger.info(f"Total images till now {image_count}")
            offset += LIMIT
        else:
            logger.error("No more images to process")
            logger.info("Exiting")
            condition = False
    image_count = image_store.commit()
    logger.info(f"Total number of images received {image_count}")


def _build_query_param(offset=0, default_query_param=None):
    if default_query_param is None:
        default_query_param = DEFAULT_QUERY_PARAMS
    query_param = default_query_param.copy()
    query_param.update(skip=offset)
    return query_param


def _get_response(query_param, endpoint=ENDPOINT, retries=RETRIES):
    response_json, total_images, tries = None, 0, 0
    for tries in range(retries):
        response = delay_request.get(endpoint, query_param)
        if response is not None and response.status_code == 200:
            try:
                response_json = response.json()
                total_images = len(response_json["data"])
            except Exception as e:
                logger.warning(f"response not captured due to {e}")
                response_json = None
            if response_json is not None and total_images is not None:
                break

        logger.info(
            "Retrying \n"
            f"endpoint -- {endpoint} \t"
            f" with parameters -- {query_param} "
        )
    if tries == retries - 1 and ((response_json is None) or (total_images is None)):
        logger.warning("No more tries remaining. Returning Nonetypes.")
        return None, 0
    else:
        return response_json, total_images


def get_int_value(data: Dict, key: str) -> int | None:
    """
    Converts the value of the key `key` in `data` to an integer.
    Returns None if the value is not convertible to an integer, or
    if the value doesn't exist.
    """
    value = data.get(key)
    if bool(value):
        if isinstance(value, str) and value.isdigit():
            return int(value)
        elif isinstance(value, int):
            return value
    return None


def _handle_batch_item(data: Dict) -> Dict | None:
    license_ = data.get("share_license_status", "").lower()
    if license_ != "cc0":
        return None
    foreign_id = data.get("id")
    if foreign_id is None:
        return None
    image = _get_image_type(data.get("images", {}))
    if image is None or image.get("url") is None:
        return None

    if data.get("creators"):
        creator_name = data.get("creators")[0].get("description", "")
    else:
        creator_name = ""

    return {
        "foreign_identifier": f"{foreign_id}",
        "foreign_landing_url": data.get("url"),
        "title": data.get("title", None),
        "creator": creator_name,
        "image_url": image["url"],
        "width": get_int_value(image, "width"),
        "height": get_int_value(image, "height"),
        "filesize": get_int_value(image, "filesize"),
        "license_info": CC0_LICENSE,
        "meta_data": _get_metadata(data),
    }


def _handle_response(batch: List):
    total_images = 0
    for data in batch:
        item = _handle_batch_item(data)
        if item is not None:
            total_images = image_store.add_item(**item)

    return total_images


def _get_image_type(image_data):
    # Returns the image url and key for the image in `image_data` dict.
    for key in ["web", "print", "full"]:
        if keyed_image := image_data.get(key):
            return keyed_image
    return None


def _get_metadata(data):
    metadata = {
        "accession_number": data.get("accession_number", ""),
        "technique": data.get("technique", ""),
        "date": data.get("creation_date", ""),
        "credit_line": data.get("creditline", ""),
        "classification": data.get("type", ""),
        "tombstone": data.get("tombstone", ""),
        "culture": ",".join([i for i in data.get("culture", []) if i is not None]),
    }
    metadata = {k: v for k, v in metadata.items() if v is not None}
    return metadata


if __name__ == "__main__":
    main()

import os
import re
import logging
from common.requester import DelayedRequester
from common.storage.image import ImageStore

LIMIT = 35
DELAY = 5.0
RETRIES = 3
PROVIDER = "brooklynmuseum"
ENDPOINT = "https://www.brooklynmuseum.org/api/v2/object/"
API_KEY = os.environ["BROOKLYN_MUSEUM_API_KEY"]

delay_request = DelayedRequester(delay=DELAY)
image_store = ImageStore(provider=PROVIDER)

HEADERS = {
    "api_key": API_KEY
}

DEFAULT_QUERY_PARAM = {
    "has_images": 1,
    "rights_type_permissive": 1,
    "limit": LIMIT,
    "offset": 0
}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Begin: Brooklyn museum provider script")
    object_ids = []
    offset = 0
    condition = True
    while condition:
        query_param = _get_query_param(offset)
        data = _get_response(query_param=query_param)
        logger.debug(len(data))
        if len(data) > 0:
            for obj in data:
                object_ids.append(obj.get("id", ""))
            offset += LIMIT
        else:
            condition = False
    if len(object_ids) > 0:
        for id in object_ids:
            data = _get_response(endpoint=ENDPOINT+str(id))
            image_count = _handle_response(data)
            logger.debug(image_count)
        total_images = image_store.commit()
        logger.info(f"Total images recieved {total_images}")
    else:
        logger.warning("No images recieved")


def _get_query_param(offset=0,
                     default_query_param=DEFAULT_QUERY_PARAM):
    query_param = default_query_param.copy()
    query_param.update(
        offset=offset
    )
    return query_param


def _get_response(headers=HEADERS,
                  endpoint=ENDPOINT,
                  retries=RETRIES,
                  query_param=None):
    for tries in range(retries):
        try:
            response = delay_request.get(
                endpoint,
                query_param,
                headers=headers
            )
            data = response.json()
            if data and data.get("message", "").lower() == "success.":
                return data.get("data", "")
        except Exception as e:
            logger.warning(f"response not captured due to {e}")
    return None


def _handle_response(data):
    image_count = 0
    if data is None:
        return 0

    rights_info = data.get("rights_type")
    license_url = _get_license_url(rights_info)
    if license_url is None:
        return None

    id = data.get("id", "")
    title = data.get("title", "")
    foreign_url = f"https://www.brooklynmuseum.org/opencollection/objects/{id}"
    metadata = _get_metadata(data)
    creators = _get_creators(data)
    image_info = data.get("images", None)
    if image_info is None:
        return None

    for image in image_info:
        foreign_id = image.get("id", "")
        image_url, thumbnail_url = _get_images(image)
        if image_url is None:
            continue
        height, width = _get_image_sizes(image)

        image_count = image_store.add_item(
                foreign_landing_url=foreign_url,
                image_url=image_url,
                license_url=license_url,
                foreign_identifier=foreign_id,
                width=width,
                height=height,
                title=title,
                thumbnail_url=thumbnail_url,
                meta_data=metadata,
                creator=creators
            )
        logger.debug(image_count)

    return image_count


def _get_image_sizes(image):
    size_list = image.get("derivatives", "")
    if type(size_list) is not list:
        return None, None
    size_type = image.get("largest_derivative", "")
    for size in size_list:
        if size.get("size", "") == size_type:
            height = size.get("height", None)
            width = size.get("width", None)
    return height, width


def _get_license_url(data):
    if "creative commons" not in data.get("name").lower():
        return None
    license_url = re.search('https://creativecommons.org/licenses/[^\s]+',
                            data.get('description'))
    license_url = license_url.group(0).strip()
    return license_url


def _get_metadata(data):
    metadata = {}
    metadata["accession_number"] = data.get("accession_number", "")
    metadata["date"] = data.get("object_date", "")
    metadata["description"] = data.get("description", "")
    metadata["medium"] = data.get("medium", "")
    metadata["credit_line"] = data.get("credit_line", "")
    metadata["classification"] = data.get("classification", "")
    return metadata


def _get_creators(data):
    creators = ""
    artists_info = data.get("artists", None)
    if artists_info is None:
        return None
    for artists in artists_info:
        creators += artists.get("name") + ","
    return creators[:-1]


def _get_images(image):
    image_url = image.get("largest_derivative_url", "")
    if not image_url:
        return None, None
    if "http" not in image_url:
        image_url = "https://" + image_url
    thumbnail_url = image.get("thumbnail_url", "")
    if "http" not in thumbnail_url and thumbnail_url:
        thumbnail_url = "https://" + thumbnail_url
    return image_url, thumbnail_url


if __name__ == "__main__":
    main()

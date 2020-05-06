import os
import logging
import lxml.html as html
from common.requester import DelayedRequester
from common.storage.image import ImageStore

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

LIMIT = 35
DELAY = 5.0
RETRIES = 3
PROVIDER = "brooklynmuseum"
ENDPOINT = "https://www.brooklynmuseum.org/api/v2/object/"
API_KEY = os.getenv("BROOKLYN_MUSEUM_API_KEY", "nokeyprovided")

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


def main():
    logger.info("Begin: Brooklyn museum provider script")
    offset = 0
    condition = True
    while condition:
        query_param = _get_query_param(offset)
        objects_batch = _get_object_json(query_param=query_param)
        logger.debug(len(objects_batch))
        if len(objects_batch) > 0:
            image_count = _process_objects_batch(objects_batch)
            logger.debug(f"Images till now {image_count}")
            offset += LIMIT
        else:
            condition = False
    total_images = image_store.commit()
    logger.info(f"Total images recieved {total_images}")


def _get_query_param(offset=0,
                     default_query_param=DEFAULT_QUERY_PARAM):
    query_param = default_query_param.copy()
    query_param.update(
        offset=offset
    )
    return query_param


def _get_object_json(headers=HEADERS,
                     endpoint=ENDPOINT,
                     retries=RETRIES,
                     query_param=None):
    for tries in range(retries):
        response = delay_request.get(
                    endpoint,
                    query_param,
                    headers=headers
                    )
        data = response.json()
        if data and data.get("message", "").lower() == "success.":
            response_json = data.get("data", None)
            break
        else:
            response_json = None
    return response_json


def _process_objects_batch(objects_batch):
    image_count = None
    for object_ in objects_batch:
        rights_info = object_.get("rights_type")
        license_url = _get_license_url(rights_info)
        logger.debug(license_url)
        if license_url is not None:
            id_ = object_.get("id", "")
            complete_object_data = _get_object_json(
                endpoint=ENDPOINT+str(id_)
                )
            if complete_object_data is None:
                continue
            image_count = _handle_object_data(
                data=complete_object_data,
                license_url=license_url
                )

    return image_count


def _handle_object_data(data, license_url):
    image_count = None
    image_info = data.get("images", None)
    if image_info is not None:
        id_ = data.get("id", "")
        title = data.get("title", "")
        foreign_url = f"https://www.brooklynmuseum.org/opencollection/objects/{id_}"
        metadata = _get_metadata(data)
        creators = _get_creators(data)

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

    return image_count


def _get_image_sizes(image):
    height, width = None, None
    size_list = image.get("derivatives", "")
    if type(size_list) is list:
        size_type = image.get("largest_derivative", "")
        for size in size_list:
            if size.get("size", "") == size_type:
                height = size.get("height", None)
                width = size.get("width", None)
    return height, width


def _get_license_url(rights_info):
    if "creative commons" in rights_info.get("name").lower():
        elements = html.fromstring(rights_info.get("description", ""))
        cc_links = [
            elm[2]
            for elm in elements.iterlinks()
            if "https://creativecommons.org/licenses/" in elm[2]
        ]
        if len(cc_links) == 1:
            (license_url,) = cc_links
        else:
            license_url = None
    else:
        license_url = None
    return license_url


def _get_metadata(data):
    metadata = {}
    metadata["accession_number"] = data.get("accession_number", None)
    metadata["date"] = data.get("object_date", None)
    metadata["description"] = data.get("description", None)
    metadata["medium"] = data.get("medium", None)
    metadata["credit_line"] = data.get("credit_line", None)
    metadata["classification"] = data.get("classification", None)
    return metadata


def _get_creators(data):
    creators = None
    artists_info = data.get("artists", None)
    if artists_info is not None:
        creators = ""
        for artists in artists_info:
            creators += artists.get("name") + ","
        creators = creators[:-1]
    return creators


def _get_images(image):
    image_url, thumbnail_url = None, None
    image_url = image.get("largest_derivative_url", None)
    if image_url:
        if "http" not in image_url:
            image_url = "https://" + image_url
        thumbnail_url = image.get("thumbnail_url", "")
        if "http" not in thumbnail_url and thumbnail_url:
            thumbnail_url = "https://" + thumbnail_url
    return image_url, thumbnail_url


if __name__ == "__main__":
    main()

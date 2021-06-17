import os
import logging
import lxml.html as html

from common import DelayedRequester, ImageStore
from util.loader import provider_details as prov

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

LIMIT = 35
DELAY = 1.0
RETRIES = 3
PROVIDER = prov.BROOKLYN_DEFAULT_PROVIDER
ENDPOINT = "https://www.brooklynmuseum.org/api/v2/object/"
API_KEY = os.getenv("BROOKLYN_MUSEUM_API_KEY", "nokeyprovided")

delay_request = DelayedRequester(delay=DELAY)
image_store = ImageStore(provider=PROVIDER)

HEADERS = {
    "api_key": API_KEY
}

DEFAULT_QUERY_PARAMS = {
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
        query_param = _get_query_param(offset=offset)
        objects_batch = _get_object_json(
            query_param=query_param
            )
        logger.debug(len(objects_batch))
        if type(objects_batch) == list and len(objects_batch) > 0:
            _process_objects_batch(objects_batch)
            logger.debug(f"Images till now {image_store.total_images}")
            offset += LIMIT
        else:
            condition = False
    image_store.commit()
    logger.info(f"Total images recieved {image_store.total_images}")


def _get_query_param(
        offset=0,
        default_query_param=None
        ):
    if default_query_param is None:
        default_query_param = DEFAULT_QUERY_PARAMS
    query_param = default_query_param.copy()
    query_param.update(offset=offset)
    return query_param


def _get_object_json(
        headers=None,
        endpoint=ENDPOINT,
        retries=RETRIES,
        query_param=None
        ):
    if headers is None:
        headers = HEADERS.copy()
    data = None
    for tries in range(retries):
        response = delay_request.get(
                    endpoint,
                    query_param,
                    headers=headers
                    )
        try:
            response_json = response.json()
            if (response_json and
                    response_json.get("message", "").lower() == "success."):
                data = response_json.get("data")
                break
        except Exception as e:
            logger.error(f"Error due to {e}")
    return data


def _process_objects_batch(objects_batch):
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
            _handle_object_data(
                data=complete_object_data,
                license_url=license_url
                )


def _handle_object_data(data, license_url):
    image_info = data.get("images")
    if image_info is not None:
        id_ = data.get("id", "")
        title = data.get("title", "")
        foreign_url = (
            f"https://www.brooklynmuseum.org/opencollection/objects/{id_}"
        )
        metadata = _get_metadata(data)
        creators = _get_creators(data)

        for image in image_info:
            foreign_id = image.get("id", "")
            image_url, thumbnail_url = _get_images(image)
            if image_url is None:
                continue
            height, width = _get_image_sizes(image)

            image_store.add_item(
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


def _get_image_sizes(image):
    height, width = None, None
    size_list = image.get("derivatives", "")
    if type(size_list) is list:
        size_type = image.get("largest_derivative", "")
        for size in size_list:
            if size.get("size", "") == size_type:
                height = size.get("height")
                width = size.get("width")
    return height, width


def _get_license_url(rights_info):
    elements = html.fromstring(rights_info.get("description", ""))
    cc_links = [
        elm[2]
        for elm in elements.iterlinks()
        if "https://creativecommons.org/" in elm[2]
    ]
    if len(cc_links) == 1:
        (license_url,) = cc_links
    else:
        license_url = None
    return license_url


def _get_metadata(data):
    metadata = {}
    metadata["accession_number"] = data.get("accession_number")
    metadata["date"] = data.get("object_date")
    metadata["description"] = data.get("description")
    metadata["medium"] = data.get("medium")
    metadata["credit_line"] = data.get("credit_line")
    metadata["classification"] = data.get("classification")
    return metadata


def _get_creators(data):
    artists_info = data.get("artists")
    if type(artists_info) == list:
        creators_list = (
            artists.get("name")
            for artists in artists_info
            if artists.get("rank") == 1
        )
        creator = next(creators_list, None)
    else:
        creator = None
    if creator is None:
        logger.warning("No creator found")
    return creator


def _get_images(image):
    image_url, thumbnail_url = None, None
    image_url = image.get("largest_derivative_url")
    if image_url:
        if "http" not in image_url:
            image_url = "https://" + image_url
        thumbnail_url = image.get("thumbnail_url", "")
        if "http" not in thumbnail_url and thumbnail_url:
            thumbnail_url = "https://" + thumbnail_url
    return image_url, thumbnail_url


if __name__ == "__main__":
    main()

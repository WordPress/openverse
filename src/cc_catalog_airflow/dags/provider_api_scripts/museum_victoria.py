"""
This script is still in testing phase
and is used to check for viable methods 
to crawl

"""
import logging
from urllib.parse import urlparse
from common.requester import DelayedRequester
from common.storage.image import ImageStore

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

LIMIT = 100
DELAY = 5.0
RETRIES = 3
PROVIDER = "museumvictoria"
ENDPOINT = "https://collections.museumsvictoria.com.au/api/search"
LANDING_PAGE = "https://collections.museumsvictoria.com.au/"

delay_request = DelayedRequester(delay=DELAY)
image_store = ImageStore(provider=PROVIDER)

HEADERS = {
    "Accept": "application/json"
}

DEFAULT_QUERY_PARAM = {
    "has_image": "yes",
    "perpage": LIMIT,
    "imagelicence": "cc+by",
    "page": 0
}

LICENSE_LIST = [
    "cc by-nc-nd",
    "cc by",
    "public domain",
    "cc by-nc",
    "cc by-nc-sa",
    "cc by-sa",
]

RECORDS_IDS = []

def main():
    for license_ in LICENSE_LIST:
        logger.info(f"querying for license {license_}")
        condition = True
        page = 0
        while condition:
            query_params = _get_query_params(
                license_type=license_,
                page=page
            )
            results = _get_batch_objects(
                params=query_params
            )
            print(results)
            if type(results) == list:
                if len(results) > 0:
                    image_count = _handle_batch_objects(results)
                    page += 1
                else:
                    condition = False
            else:
                condition = False
    image_count = image_store.commit()
    logger.info(f"Total images {image_count}")


def _get_query_params(
        query_params=DEFAULT_QUERY_PARAM,
        license_type=None,
        page=0
        ):
    query_params["imagelicence"] = license_type
    query_params["page"] = page
    return query_params


def _get_batch_objects(
        endpoint=ENDPOINT,
        params=None,
        headers=HEADERS,
        retries=RETRIES
    ):
    for retry in range(retries):
        response = delay_request.get(
            endpoint,
            params,
            headers=headers
        )
        print(response)
        try:
            response_json = response.json()
            if type(response_json) == list:
                data = response_json
                break
            else:
                data = None
        except Exception as e:
            data = None
    return data 


def _handle_batch_objects(
        objects,
        landing_page=LANDING_PAGE):
    image_count = 0
    for obj in objects:
        object_id = obj.get("id")
        if object_id in RECORDS_IDS:
            continue
        RECORDS_IDS.append(object_id)
        foreign_landing_url = landing_page + object_id
        media_data = obj.get("media")
        if media_data is None:
            continue
        image_data = _get_media_info(media_data)
        if len(image_data) == 0:
            continue
        for img in image_data:
            image_count = image_store.add_item(
                foreign_identifier=img.get("image_id"),
                foreign_landing_url=foreign_landing_url,
                image_url=img.get("image_url"),
                license_url=img.get("license_url")
            )
    return image_count


def _get_media_info(media_data):
    image_data = []
    for media in media_data:
        media_type = media.get("type")
        if media_type == "image":
            image_url, image_id = _get_image_url_id(
                media
            )
            license_url = _get_license_url(
                media
            )
            if (
                image_url is None or image_id is None or license_url is None
            ):
                continue
            image_data.append(
                {
                    "image_id": image_id,
                    "image_url": image_url,
                    "license_url": license_url
                }
            )
    return image_data


def _get_image_url_id(media):
    image_url, image_id = None, None
    if "large" in media.keys():
        image_url = media.get("large").get("uri")
        image_id = _get_image_id(image_url)
    elif "medium" in media.keys():
        image_url = media.get("medium").get("uri")
        image_id = _get_image_id(image_url)
    elif "small" in media.keys():
        image_url = media.get("small").get("uri")
        image_id = _get_image_id(image_url)
    return image_url, image_id


def _get_image_id(image_url):
    path = urlparse(image_url).path.split("/")[-1]
    image_id = path.split("-")[0]
    return image_id


def _get_license_url(media):
    license_url = None
    license_ = media.get("licence")
    if license_ is not None:
        uri = license_.get("uri")
        if "creativecommons" in uri:
            license_url = uri
    return license_url


if __name__ == "__main__":
    main()
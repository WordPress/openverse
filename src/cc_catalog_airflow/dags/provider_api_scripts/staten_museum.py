import logging
from common.requester import DelayedRequester
from common.storage.image import ImageStore

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

LIMIT = 2000
DELAY = 5
RETRIES = 3
PROVIDER = "statensmuseum"
ENDPOINT = "https://api.smk.dk/api/v1/art/search/"
LANDING_PAGE_BASE_URL = "https://open.smk.dk/en/artwork/image/"
IMAGE_SIZE = "max"
THUMBNAIL_SIZE = 400

delay_request = DelayedRequester(delay=DELAY)
image_store = ImageStore(provider=PROVIDER)

DEFAULT_QUERY_PARAM = {
    "keys": "*",
    "filter": "[has_image:true],[public_domain:true]",
    "offset": 0,
    "rows": LIMIT
}

HEADERS = {
     "Accept": "application/json"
}

def main():
    condition = True
    offset = 0
    while condition:
        query_params = _get_query_param(offset=offset)
        items = _get_batch_items(
            query_params=query_params
            )
        if len(items) == 0:
            image_count = _handle_items_data(
                items
            )
            offset += LIMIT
        else:
            condition = False
    image_count = image_store.commit()
    logger.info(f"total images collected {image_count}")


def _get_query_param(
        offset=0,
        default_query_param=DEFAULT_QUERY_PARAM
        ):
    query_params = default_query_param.copy()
    query_params.update(
        offset=offset
    )
    return query_params


def _get_batch_items(
        endpoint=ENDPOINT,
        query_params=None,
        headers=HEADERS,
        retries=RETRIES
        ):
    for retry in range(retries):
        response = delay_request.get(
            endpoint,
            query_params,
            headers=headers
        )
        try:
            response_json = response.json()
            if "items" in response_json.keys():
                items = response_json.get("items")
                break
            else:
                items = None
        except Exception as e:
            logger.error(f"errored due to {e}")
            items = None
    return items


def _handle_items_data(
        items,
        landing_page_base=LANDING_PAGE_BASE_URL,
        ):
    image_count = 0
    for item in items:
        image_iiif_id = item.get("image_iiif_id")
        if image_iiif_id is None:
            continue
        rights = item.get("rights")
        license_, version = _get_license_info(rights)
        if license_ is None and version is None:
            continue
        object_id = item.get("id")
        foreign_landing_url = landing_page_base + object_id
        image_url, thumbnail_url = _get_image_url(
            image_iiif_id
        )
        height = item.get("image_height")
        width = item.get("image_width")
        production = item.get("production")
        creator = _get_creator(production)
        titles = item.get("titles")
        title = _get_title(titles)
        image_count = image_store.add_item(
                foreign_identifier=image_iiif_id,
                foreign_landing_url=foreign_landing_url,
                image_url=image_url,
                height=height,
                width=width,
                license_=license_,
                license_version=version,
                thumbnail_url=thumbnail_url,
                creator=creator,
                title=title,
                meta_data=meta_data,
        )
    return image_count


def _get_image_url(
        image_iiif_id,
        image_size=IMAGE_SIZE,
        thumbnail_size=THUMBNAIL_SIZE
        ):
    image_url = image_iiif_id + f"/full/{image_size}/0/default.jpg"
    thumbnail_url = (
        image_iiif_id + f"/full/!{thumbnail_size},/0/default.jpg"
    )
    print(image_url)
    return image_url, thumbnail_url


def _get_license_info(rights):
    if "creativecommons" in rights:
        license_, version = "cc0", "1.0"
    else:
        license_, version = None, None
    return license_, version


def _get_creator(production):
    creator = None
    if type(production) == list:
        if type(production[0]) == dict:
            creator = production[0].get("creator")
    return creator


def _get_title(titles):
    title = None
    if type(titles) == list:
        if type(titles[0]) == dict:
            title = titles[0].get("title")
    return title


def _get_metadata(item):
    pass


if __name__ == "__main__":
    main()
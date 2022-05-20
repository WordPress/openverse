import logging

from common.licenses import get_license_info
from common.loader import provider_details as prov
from common.requester import DelayedRequester
from common.storage.image import ImageStore


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

LIMIT = 2000
DELAY = 5
RETRIES = 3
PROVIDER = prov.SMK_DEFAULT_PROVIDER
ENDPOINT = "https://api.smk.dk/api/v1/art/search/"
LANDING_PAGE_BASE_URL = "https://open.smk.dk/en/artwork/image/"
IMAGE_SIZE = 2048
THUMBNAIL_SIZE = 400

delay_request = DelayedRequester(delay=DELAY)
image_store = ImageStore(provider=PROVIDER)

DEFAULT_QUERY_PARAMS = {
    "keys": "*",
    "filters": "[has_image:true],[public_domain:true]",
    "offset": 0,
    "rows": LIMIT,
}

HEADERS = {"Accept": "application/json"}


def main():
    condition = True
    offset = 0
    while condition:
        query_params = _get_query_param(offset=offset)
        items = _get_batch_items(query_params=query_params)
        if type(items) == list:
            if len(items) > 0:
                _handle_items_data(items)
                offset += LIMIT
            else:
                condition = False
        else:
            condition = False
    image_count = image_store.commit()
    logger.info(f"total images collected {image_count}")


def _get_query_param(offset=0, default_query_param=None):
    if default_query_param is None:
        default_query_param = DEFAULT_QUERY_PARAMS
    query_params = default_query_param.copy()
    query_params.update(offset=offset)
    return query_params


def _get_batch_items(
    endpoint=ENDPOINT, query_params=None, headers=None, retries=RETRIES
):
    if headers is None:
        headers = HEADERS.copy()
    items = None
    for retry in range(retries):
        response = delay_request.get(endpoint, query_params, headers=headers)
        try:
            response_json = response.json()
            if "items" in response_json.keys():
                items = response_json.get("items")
                break
        except Exception as e:
            logger.error(f"errored due to {e}")
    return items


def _handle_items_data(
    items,
    landing_page_base=LANDING_PAGE_BASE_URL,
):
    image_count = 0
    for item in items:
        images = _get_images(item)
        if len(images) == 0:
            continue
        rights = item.get("rights")
        license_, version = _get_license_info(rights)
        if license_ is None and version is None:
            continue
        object_id = item.get("object_number")
        if object_id is None:
            continue
        foreign_landing_url = landing_page_base + object_id
        production = item.get("production")
        creator = _get_creator(production)
        titles = item.get("titles")
        title = _get_title(titles)
        meta_data = _get_metadata(item)
        for img in images:
            license_info = get_license_info(license_=license_, license_version=version)
            image_count = image_store.add_item(
                foreign_identifier=img.get("id"),
                foreign_landing_url=foreign_landing_url,
                image_url=img.get("image_url"),
                height=img.get("height"),
                width=img.get("width"),
                license_info=license_info,
                thumbnail_url=img.get("thumbnail"),
                creator=creator,
                title=title,
                meta_data=meta_data,
            )
    return image_count


def _get_images(item):
    images = []

    # Legacy images do not have an iiif_id; fall back to the ID from the
    # collection DB.
    iiif_id = item.get("image_iiif_id")
    id = iiif_id or item.get("id")

    if id is not None:
        if iiif_id is None:
            # Legacy images do not have IIIF links.
            image_url = item.get("image_native")
            thumbnail_url = item.get("image_thumbnail")
        else:
            image_url, thumbnail_url = _get_image_urls(iiif_id)

        height = item.get("image_height")
        width = item.get("image_width")

        images.append(
            {
                "id": id,
                "image_url": image_url,
                "thumbnail": thumbnail_url,
                "height": height,
                "width": width,
            }
        )

    alternative_images = item.get("alternative_images")
    if type(alternative_images) == list:
        for alt_img in alternative_images:
            if type(alt_img) == dict:
                iiif_id = alt_img.get("iiif_id")
                if iiif_id is None:
                    # The API for alternative images does not include the
                    # 'id', so we must skip if `iiif_id` is not present.
                    continue
                image_url, thumbnail_url = _get_image_urls(iiif_id)
                height = alt_img.get("height")
                width = alt_img.get("width")
                images.append(
                    {
                        "id": iiif_id,
                        "image_url": image_url,
                        "thumbnail": thumbnail_url,
                        "height": height,
                        "width": width,
                    }
                )
    return images


def _get_image_urls(
    image_iiif_id, image_size=IMAGE_SIZE, thumbnail_size=THUMBNAIL_SIZE
):
    # For high quality IIIF-enabled images, restrict the image size to prevent loading
    # very large files.
    image_url = image_iiif_id + f"/full/!{image_size},/0/default.jpg"
    thumbnail_url = image_iiif_id + f"/full/!{thumbnail_size},/0/default.jpg"

    return image_url, thumbnail_url


def _get_license_info(rights):
    license_, version = None, None
    if type(rights) == str:
        if "creativecommons" in rights:
            license_, version = "cc0", "1.0"

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
    meta_data = {}
    created_date = item.get("created")
    if created_date:
        meta_data["created_date"] = created_date
    collection = item.get("collection")
    if type(collection) == list:
        meta_data["collection"] = ",".join(collection)
    techniques = item.get("techniques")
    if type(techniques) == list:
        meta_data["techniques"] = ",".join(techniques)
    colors = item.get("colors")
    if type(colors) == list:
        meta_data["colors"] = ",".join(colors)
    return meta_data


if __name__ == "__main__":
    main()

"""
Content Provider:       WordPress Photo Directory

ETL Process:            Use the API to identify all openly licensed media.

Output:                 TSV file containing the media metadata.

Notes:                  https://wordpress.org/photos/wp-json/wp/v2
                        Provide photos, media, users and more related resources.
                        No rate limit specified.
"""
import logging
from pathlib import Path

import lxml.html as html
from common.licenses.licenses import get_license_info
from common.requester import DelayedRequester
from storage.image import ImageStore
from util.loader import provider_details as prov


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

LIMIT = 100  # number of items per page in API response
DELAY = 1  # in seconds
RETRIES = 3

HOST = "wordpress.org"
ENDPOINT = f"https://{HOST}/photos/wp-json/wp/v2"

PROVIDER = prov.WORDPRESS_DEFAULT_PROVIDER

DEFAULT_QUERY_PARAMS = {
    "format": "json",
    "page": 1,
    "per_page": LIMIT,
}

delayed_requester = DelayedRequester(DELAY)
image_store = ImageStore(provider=PROVIDER)

license_url = "https://creativecommons.org/publicdomain/zero/1.0/"
license_info = get_license_info(license_url=license_url)

IMAGE_RELATED_RESOURCES = {
    "users": {},  # authors
    "photo-categories": {},
    "photo-colors": {},
    "photo-orientations": {},
    "photo-tags": {},
}


def main():
    """
    This script pulls the data from the WordPress Photo Directory and writes it into a
    .TSV file to be eventually read into our DB.
    """

    logger.info("Begin: WordPress Photo Directory script")
    _prefetch_image_related_data()
    image_count = _get_images()
    image_store.commit()
    logger.info(f"Total images pulled: {image_count}")
    logger.info("Terminated!")


def _prefetch_image_related_data():
    for resource in IMAGE_RELATED_RESOURCES.keys():
        collection = _get_resources(resource)
        IMAGE_RELATED_RESOURCES[resource] = collection
    logger.info("Prefetch of image-related data completed.")


def _get_resources(resource_type):
    total_pages = page = 1
    endpoint = f"{ENDPOINT}/{resource_type}"
    collection = {}
    while total_pages >= page:
        query_params = _get_query_params(page=page)
        batch_data, total_pages = _get_item_page(endpoint, query_params=query_params)
        if isinstance(batch_data, list) and len(batch_data) > 0:
            collection_page = _process_resource_batch(resource_type, batch_data)
            collection = collection | collection_page
            page += 1
    return collection


def _process_resource_batch(resource_type, batch_data):
    collected_page = {}
    for item in batch_data:
        item_id, name, url = None, None, None
        try:
            item_id = item["id"]
            name = item["name"]
            if resource_type == "users":
                # 'url' is the website of the author and 'link' would be their wp.org
                # profile, so at least the last must always be present
                url = item["url"] or item["link"]
        except Exception as e:
            logger.error(f"Couldn't save resource({resource_type}) info due to {e}")
            continue
        if resource_type == "users":
            collected_page[item_id] = {"name": name, "url": url}
        else:
            collected_page[item_id] = name
    return collected_page


def _get_query_params(page=1, default_query_params=None):
    if default_query_params is None:
        default_query_params = DEFAULT_QUERY_PARAMS
    query_params = default_query_params.copy()
    query_params["page"] = page
    return query_params


def _get_item_page(endpoint, retries=RETRIES, query_params=None):
    response_json, total_pages = None, None
    if retries < 0:
        logger.error("No retries remaining. Returning Nonetypes.")
        return None, 0

    response = delayed_requester.get(endpoint, query_params, allow_redirects=False)

    if response is not None and response.status_code in [200, 301, 302]:
        try:
            response_json = response.json()
            total_pages = int(response.headers["X-WP-TotalPages"])
        except Exception as e:
            logger.warning(f"Response not captured due to {e}")
            response_json = None

    if response_json is None or total_pages is None:
        logger.warning(
            "Retrying:\n_get_item_page(\n"
            f"    {endpoint},\n"
            f"    {query_params},\n"
            f"    retries={retries - 1}"
            ")"
        )
        response_json, total_pages = _get_item_page(endpoint, retries - 1, query_params)
    return response_json, total_pages


def _get_images():
    item_count = 0
    total_pages = page = 1
    endpoint = f"{ENDPOINT}/photos"
    while total_pages >= page:
        query_params = _get_query_params(page=page)
        batch_data, total_pages = _get_item_page(endpoint, query_params=query_params)
        if isinstance(batch_data, list) and len(batch_data) > 0:
            item_count = _process_image_batch(batch_data)
            page += 1
    return item_count


def _process_image_batch(image_batch):
    for item in image_batch:
        item_meta_data = _extract_image_data(item)
        if item_meta_data is None:
            continue
        image_store.add_item(**item_meta_data)
    return image_store.total_items


def _get_image_details(media_data):
    try:
        url = media_data.get("_links").get("wp:featuredmedia")[0].get("href")
        response_json = _get_response_json(url, RETRIES, allow_redirects=False)
        return response_json
    except (KeyError, AttributeError):
        return None


def _get_response_json(endpoint, retries=0, query_params=None, **kwargs):
    """
    Function copied from common.requester.DelayedRequester class to allow responses
    with status code 301 or 302. It's expected it can be removed once the API is
    fully ready. This API currently returns a `302` with a JSON body.
    """
    response_json = None

    if retries < 0:
        logger.error("No retries remaining.  Failure.")
        raise Exception("Retries exceeded")

    response = delayed_requester.get(endpoint, params=query_params, **kwargs)
    if response is not None and response.status_code in [200, 301, 302]:
        try:
            response_json = response.json()
        except Exception as e:
            logger.warning(f"Could not get response_json.\n{e}")
            response_json = None

    if response_json is None or response_json.get("error") is not None:
        logger.warning(f"Bad response_json:  {response_json}")
        logger.warning(
            "Retrying:\n_get_response_json(\n"
            f"    {endpoint},\n"
            f"    {query_params},\n"
            f"    retries={retries - 1}"
            ")"
        )
        response_json = _get_response_json(
            endpoint, retries=retries - 1, query_params=query_params, **kwargs
        )

    return response_json


def _extract_image_data(media_data):
    """
    Extract data for individual item.
    """
    try:
        foreign_identifier = media_data["slug"]
        foreign_landing_url = media_data["link"]
    except (TypeError, KeyError, AttributeError):
        return None
    title = _get_title(media_data)
    image_details = _get_image_details(media_data)
    if image_details is None:
        return None
    image_url, height, width, filetype = _get_file_info(image_details)
    if image_url is None:
        return None
    thumbnail = _get_thumbnail_url(image_details)
    metadata = _get_metadata(media_data, image_details)
    creator, creator_url = _get_creator_data(media_data)
    tags = _get_related_data("tags", media_data)

    return {
        "title": title,
        "creator": creator,
        "creator_url": creator_url,
        "foreign_identifier": foreign_identifier,
        "foreign_landing_url": foreign_landing_url,
        "image_url": image_url,
        "height": height,
        "width": width,
        "thumbnail_url": thumbnail,
        "filetype": filetype,
        "license_info": license_info,
        "meta_data": metadata,
        "raw_tags": tags,
    }


def _get_file_info(image_details):
    file_details = (
        image_details.get("media_details", {}).get("sizes", {}).get("full", {})
    )
    image_url = file_details.get("source_url")
    height = file_details.get("height")
    width = file_details.get("width")
    filetype = None
    if filename := file_details.get("file"):
        filetype = Path(filename).suffix.replace(".", "")
    return image_url, height, width, filetype


def _get_thumbnail_url(image_details):
    return (
        image_details.get("media_details", {})
        .get("sizes", {})
        .get("thumbnail", {})
        .get("source_url")
    )


def _get_creator_data(image):
    creator, creator_url = None, None
    if author_id := image.get("author"):
        creator = IMAGE_RELATED_RESOURCES.get("users").get(author_id, {}).get("name")
        creator_url = IMAGE_RELATED_RESOURCES.get("users").get(author_id, {}).get("url")
    return creator, creator_url


def _get_title(image):
    if title := image.get("content", {}).get("rendered"):
        title = html.fromstring(title).text_content()
    return title


def _get_metadata(image, image_details):
    raw_metadata = image_details.get("media_details", {}).get("image_meta", {})
    metadata = {}
    extras = [
        "aperture",
        "camera",
        "created_timestamp",
        "focal_length",
        "iso",
        "shutter_speed",
    ]
    for key in extras:
        value = raw_metadata.get(key)
        if value not in [None, ""]:
            metadata[key] = value

    if published_date := image_details.get("date"):
        metadata["published_date"] = published_date

    # these fields require looking up additional queried data
    resource_extras = ["categories", "colors", "orientations"]
    for resource in resource_extras:
        metadata[resource] = sorted(_get_related_data(resource, image))
    return metadata


def _get_related_data(resource_type, image):
    resource_type = f"photo-{resource_type}"
    ids = image.get(resource_type)
    resource_names = set()
    resources_ids = IMAGE_RELATED_RESOURCES[resource_type].keys()
    for rid in ids:
        if rid in resources_ids:
            resource_names.add(IMAGE_RELATED_RESOURCES[resource_type][rid])
    return list(resource_names)


if __name__ == "__main__":
    main()

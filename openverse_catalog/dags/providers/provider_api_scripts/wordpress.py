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
from common.licenses import get_license_info
from common.loader import provider_details as prov
from common.requester import DelayedRequester
from common.storage.image import ImageStore


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
    "_embed": "true",
}

delayed_requester = DelayedRequester(DELAY)
image_store = ImageStore(provider=PROVIDER)

license_url = "https://creativecommons.org/publicdomain/zero/1.0/"
license_info = get_license_info(license_url=license_url)


def main():
    """
    This script pulls the data from the WordPress Photo Directory and writes it into a
    .TSV file to be eventually read into our DB.
    """

    logger.info("Begin: WordPress Photo Directory script")
    image_count = _get_images()
    image_store.commit()
    logger.info(f"Total images pulled: {image_count}")
    logger.info("Terminated!")


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
    foreign_identifier = media_data.get("slug")
    if foreign_identifier is None:
        return None
    foreign_landing_url = media_data.get("link")

    try:
        media_details = (
            media_data.get("_embedded", {})
            .get("wp:featuredmedia", {})[0]
            .get("media_details", {})
        )
    except (KeyError, IndexError):
        return None

    image_url, height, width, filetype, filesize = _get_file_info(media_details)
    if image_url is None:
        return None

    title = _get_title(media_data)
    author, author_url = _get_author_data(media_data)
    metadata, tags = _get_metadata(media_data, media_details)

    return {
        "title": title,
        "creator": author,
        "creator_url": author_url,
        "foreign_identifier": foreign_identifier,
        "foreign_landing_url": foreign_landing_url,
        "image_url": image_url,
        "height": height,
        "width": width,
        "filetype": filetype,
        "filesize": filesize,
        "license_info": license_info,
        "meta_data": metadata,
        "raw_tags": tags,
    }


def _get_file_info(media_details):
    preferred_sizes = ["2048x2048", "1536x1536", "medium_large", "large", "full"]
    for size in preferred_sizes:
        file_details = media_details.get("sizes", {}).get(size, {})
        image_url = file_details.get("source_url")
        if not image_url or image_url == "":
            continue

        height = file_details.get("height")
        width = file_details.get("width")
        filetype = None
        if filename := file_details.get("file"):
            filetype = Path(filename).suffix.replace(".", "")

        filesize = (
            media_details.get("filesize", 0)
            if size == "full"
            else file_details.get("filesize", 0)
        )
        if not filesize or int(filesize) == 0:
            filesize = _get_filesize(image_url)

        return image_url, height, width, filetype, filesize
    return None, None, None, None, None


def _get_filesize(image_url):
    resp = delayed_requester.get(image_url)
    if resp:
        filesize = int(resp.headers.get("Content-Length", 0))
        return filesize if filesize != 0 else None


def _get_author_data(image):
    try:
        raw_author = image.get("_embedded", {}).get("author", [])[0]
    except IndexError:
        return None, None
    author = raw_author.get("name")
    if author is None or author == "":
        author = raw_author.get("slug")
    author_url = raw_author.get("url")
    if author_url == "":
        author_url = raw_author.get("link")
    return author, author_url


def _get_title(image):
    if title := image.get("content", {}).get("rendered"):
        try:
            title = html.fromstring(title).text_content()
        except UnicodeDecodeError as e:
            logger.warning(f"Can't save the image's title ('{title}') due to {e}")
            return None
    return title


def _get_metadata(media_data, media_details):
    raw_metadata = media_details.get("image_meta", {})
    metadata, tags = {}, []
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

    raw_related_resources = media_data.get("_embedded", {}).get("wp:term", [])
    resource_mapping = {
        "photo_category": "categories",
        "photo_color": "colors",
        "photo_orientation": "orientation",
        "photo_tag": "tags",
    }
    for resource_arr in raw_related_resources:
        for resource in resource_arr:
            if (txy := resource.get("taxonomy")) in resource_mapping.keys():
                resource_key = resource_mapping[txy]
                resource_val = resource.get("name")
                if txy == "photo_tag":
                    tags.append(resource_val)
                elif txy == "photo_orientation":
                    metadata["orientation"] = resource_val
                else:
                    metadata.setdefault(resource_key, [])
                    metadata[resource_key].append(resource_val)
    return metadata, tags


if __name__ == "__main__":
    main()

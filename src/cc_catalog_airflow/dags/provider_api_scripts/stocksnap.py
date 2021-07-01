"""
Content Provider:       StockSnap

ETL Process:            Use the API to identify all CC-licensed images.

Output:                 TSV file containing the image, the respective
                        meta-data.

Notes:                  https://stocksnap.io/api/
                        No rate limit specified. No authentication required.
"""
import json
import logging
import lxml.html as html

from common import DelayedRequester, ImageStore
from common.licenses.licenses import get_license_info
from common.urls import rewrite_redirected_url
from util.loader import provider_details as prov


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

DELAY = 1  # in seconds
RETRIES = 3
HOST = 'stocksnap.io'
ENDPOINT = f'https://{HOST}/api/load-photos/date/desc'
CDN = "https://cdn.stocksnap.io/img-thumbs/960w"
PROVIDER = prov.STOCKSNAP_DEFAULT_PROVIDER
HEADERS = {
    "Accept": "application/json",
}
DEFAULT_QUERY_PARAMS = {}

delayed_requester = DelayedRequester(DELAY)
image_store = ImageStore(provider=PROVIDER)


saved_json_counter = {
    'full_response': 0,
    'empty_response': 0,
    'full_item': 0,
    'no_image_url': 0,
    'no_foreign_landing_url': 0,
    'no_license': 0,
}


def check_and_save_json_for_test(name, data):
    if saved_json_counter[name] == 0:
        with open(f"{name}.json", "w+", encoding="utf-8") as outf:
            json.dump(data, outf, indent=2)
        saved_json_counter[name] += 1


def main():
    """
    This script pulls the data for a given date from the Stocksnap,
    and writes it into a .TSV file to be eventually read
    into our DB.
    """

    logger.info("Begin: StockSnap script")
    image_count = _get_items()
    logger.info(f"Total images pulled: {image_count}")
    logger.info('Terminated!')


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
        if page_number > 1:
            should_continue = False
    return item_count


def _get_batch_json(
        endpoint=ENDPOINT,
        headers=None,
        retries=RETRIES,
        query_param=None
):
    if headers is None:
        headers = HEADERS.copy()
    response_json = delayed_requester.get_response_json(
        endpoint,
        retries,
        query_param,
        headers=headers
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
    return image_store.total_images


def _extract_item_data(media_data):
    """
    Extract data for individual image
    """

    foreign_identifier = media_data["img_id"]
    foreign_landing_url = f"https://{HOST}/photo/{foreign_identifier}"
    foreign_landing_url = rewrite_redirected_url(foreign_landing_url)
    if foreign_landing_url is None:
        print("Foreign landing url not resolved.")
        return None
    image_url, height, width = _get_image_info(media_data)
    if image_url is None:
        print("Found no image url.")
        return None
    item_license = _get_license()
    page = _get_landing_page(foreign_landing_url)
    title = _get_title(page)
    creator, creator_url = _get_creator_data(page)
    thumbnail = image_url
    metadata = _get_metadata(media_data)
    tags = _get_tags(media_data)
    return {
        'title': title,
        'creator': creator,
        'creator_url': creator_url,
        'foreign_identifier': foreign_identifier,
        'foreign_landing_url': foreign_landing_url,
        'image_url': image_url,
        'height': height,
        'width': width,
        'thumbnail_url': thumbnail,
        'license_': item_license.license,
        'license_version': item_license.version,
        'meta_data': metadata,
        'raw_tags': tags
    }


def _get_image_info(media_data):
    width = media_data.get('img_width')
    height = media_data.get('img_height')
    img_id = media_data.get('img_id')
    image_url = f"{CDN}/{img_id}.jpg"
    return image_url, width, height


def _get_landing_page(url):
    raw_page = delayed_requester.get(url)
    return html.document_fromstring(raw_page.text)


def _get_creator_data(page):
    page.find_class("author")
    author_elem = page.find_class("author")[0]
    creator = author_elem.text_content().strip()
    creator_url = None
    href = author_elem.attrib.get('href')
    if href is not None:
        creator_url = f"https://{HOST}{href}"
    return creator, creator_url


def _get_title(page):
    """
    Get the photo's title and transform it to title case, as shown on its page.
    So for example, for "owl bird Photo" it returns "Owl Bird Photo".
    """
    title_str = page.xpath("//h1/span")[0].text_content()
    return title_str.title()


def _get_metadata(item):
    """
    Metadata may include: description, date created and modified at source,
    categories, popularity statistics.
    """
    extras = ["downloads", "page_views", "favorites"]
    metadata = {}
    for key in extras:
        value = item.get(key)
        if value is not None:
            metadata[key] = value
    return metadata


def _get_tags(item):
    return item.get('tags')


def _get_license():
    """
    All images are licensed under CC0.
    """
    item_license_url = "https://creativecommons.org/publicdomain/zero/1.0/"
    return get_license_info(license_url=item_license_url)


if __name__ == '__main__':
    main()

# TODO: Lint your code with pycodestyle

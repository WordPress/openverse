"""
Content Provider:       StockSnap

ETL Process:            Use the API to identify all CC-licensed images.

Output:                 TSV file containing the image, the respective
                        meta-data.

Notes:                  https://stocksnap.io/api/
                        No rate limit specified.
"""
import json
import logging
from urllib.parse import urlparse

from common import DelayedRequester, ImageStore
from common.licenses.licenses import get_license_info
from util.loader import provider_details as prov

"""
This is template for an API script. Broadly, there are several steps:
1. Download batches of information for the query for openly-licensed media
2. For each item in batch, extract the necessary meta data.
3. Save the metadata using ImageStore.add_item or AudioStore.add_item methods

Try to write small functions that are easier to test. Don't forget to
write tests, too!

You can test your script during development by running it:
`python -m <your_script_name>.py`

To extract information from html, you can use lxml.html.
Recommended examples:
- For scripts requiring a start date: `wikimedia_commons.py`
- For scripts without a start date: `science_museum.py`.

ImageStore/AudioStore are the classes that clean the media metadata
and save it to the disk in form of a tsv file.
They will save the file to '/tmp' folder on your computer when you run
this script as is
"""

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
# No API key required.
# API_KEY = os.getenv("STOCKSNAP", "nokeyprovided")

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


def _get_query_param(
        page_number=0,
        default_query_param=None,
):
    if default_query_param is None:
        default_query_param = DEFAULT_QUERY_PARAMS
    query_param = default_query_param.copy()
    query_param["page"] = str(page_number)
    return query_param


def _get_items():
    item_count = 0
    page_number = 1
    should_continue = True
    while should_continue:
        # query_param = _get_query_param(page_number=page_number)
        page_endpoint = f"{ENDPOINT}/{page_number}"
        batch_data = _get_batch_json(endpoint=page_endpoint)
        if isinstance(batch_data, list) and len(batch_data) > 0:
            item_count = _process_item_batch(batch_data)
            page_number += 1
        else:
            should_continue = False
    return item_count


def _get_batch_json(
        endpoint=ENDPOINT,
        headers=None,
        retries=RETRIES,
        query_param=None
):
    if headers is None:
        headers = HEADERS
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
        if data:
            check_and_save_json_for_test('full_response', data)
        else:
            check_and_save_json_for_test('empty_response', data)
        return data


def _process_item_batch(items_batch):
    for item in items_batch:
        # For testing purposes, you would need to save json data for single
        # media objects. To make sure that you test edge cases,
        # we add the code that saves a json file per each condition:
        # full, and without one of the required properties.
        # TODO: save the resulting json files (if any) in the
        #  `provider_api_scripts/tests/resources/<provider_name>` folder
        # TODO: remove the code for saving json files from the final script

        item_meta_data = _extract_item_data(item)
        if item_meta_data is None:
            continue
        image_store.add_item(**item_meta_data)
    return image_store.total_images


def _extract_item_data(media_data):
    """
    Extract data for individual image

    Required properties:
    - foreign_landing_url
    - image_url / audio_url
    - item_license

    Optional properties:
    - foreign_identifier
    - title
    - creator
    - creator_url
    - thumbnail_url
    - metadata
    - tags
    - width
    - height
    """
    # TODO: remove the code for saving json files from the final script

    foreign_identifier = media_data["img_id"]
    foreign_landing_url = f"https://{HOST}/photo/{foreign_identifier}"
    image_url, height, width = _get_image_info(media_data)
    if image_url is None:
        print("Found no media url:")
        print(f"{json.dumps(media_data, indent=2)}")
        check_and_save_json_for_test('no_image_url', media_data)
        return None
    item_license = _get_license()
    if item_license is None:
        print("Found no item license:")
        print(f"{json.dumps(media_data, indent=2)}")
        check_and_save_json_for_test('no_license', media_data)
        return None
    title = _get_title(media_data)
    creator, creator_url = _get_creator_data(media_data)
    thumbnail = image_url
    metadata = _get_metadata(media_data)
    tags = _get_tags(media_data)
    check_and_save_json_for_test('full_item', media_data)

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


def _get_creator_data(item):
    # TODO: Add correct implementation of _get_creator_data
    # creator = item.get('creator_key').strip()
    # creator_url = _cleanse_url(
    #     item.get('creator_key', {}).get('url')
    # )
    # return creator, creator_url
    return None, None


def _get_title(item):
    # TODO: Add correct implementation of _get_title
    title = item.get('title')
    return title


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
    To parse the item license, use `get_license_info` function. It
    returns a namedtuple LicenseInfo(license_url, license, version)

    It requires either:
    1) a`license_url` (eg. `https://creativecommons.org/licenses/by/4.0/`)
    or
    2)`license_name` and `license_version`

    `license_name` can be one of the following:
    [ 'by', 'by-nc', 'by-nc-nd', 'by-nc-sa', 'by-nd', 'by-sa',
    'devnations', 'sampling', 'sampling+',
    'publicdomain', 'pdm', 'cc0' ]

    To view all possible licenses, look at licenses/constants.
    To validate that the license_name and license_version you get
    are correct, you can use `get_license_info_from_license_pair(
    license_name, license_version)`
    """
    item_license_url = "https://creativecommons.org/publicdomain/zero/1.0/"
    return get_license_info(license_url=item_license_url)


def _cleanse_url(url_string):
    """
    Check to make sure that a url is valid, and prepend a protocol if needed
    """

    parse_result = urlparse(url_string)

    if parse_result.netloc == HOST:
        parse_result = urlparse(url_string, scheme='https')
    elif not parse_result.scheme:
        parse_result = urlparse(url_string, scheme='http')

    if parse_result.netloc or parse_result.path:
        return parse_result.geturl()


if __name__ == '__main__':
    main()

# TODO: Remove unnecessary comments
# TODO: Lint your code with pycodestyle

"""
Content Provider:       Wikimedia Commons

ETL Process:            Use the API to identify all CC-licensed images.

Output:                 TSV file containing the image, the respective
                        meta-data.

Notes:                  https://commons.wikimedia.org/wiki/API:Main_page
                        No rate limit specified.
"""

import argparse
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import logging
import os
from urllib.parse import urlparse

import lxml.html as html

import common.requester as requester
import common.storage.image as image
from util.loader import provider_details as prov

logger = logging.getLogger(__name__)

LIMIT = 250
# The 10000 is a bit arbitrary, but needs to be larger than the mean
# number of uses per file (globally) in the response_json, or we will
# fail without a continuation token.  The largest example seen so far
# had a little over 1000 uses
MEAN_GLOBAL_USAGE_LIMIT = 10000
DELAY = 1
HOST = 'commons.wikimedia.org'
ENDPOINT = f'https://{HOST}/w/api.php'
PROVIDER = prov.WIKIMEDIA_DEFAULT_PROVIDER
CONTACT_EMAIL = os.getenv('WM_SCRIPT_CONTACT')
UA_STRING = (
    f'CC-Catalog/0.1 (https://creativecommons.org; {CONTACT_EMAIL})'
)
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': UA_STRING
}
DEFAULT_QUERY_PARAMS = {
    'action': 'query',
    'generator': 'allimages',
    'gaisort': 'timestamp',
    'gaidir': 'newer',
    'gailimit': LIMIT,
    'prop': 'imageinfo|globalusage',
    'iiprop': 'url|user|dimensions|extmetadata|mediatype',
    'gulimit': LIMIT,
    'gunamespace': 0,
    'format': 'json',
}
PAGES_PATH = ['query', 'pages']
IMAGE_MEDIATYPES = {'BITMAP'}

delayed_requester = requester.DelayedRequester(DELAY)
image_store = image.ImageStore(provider=PROVIDER)


def main(date):
    """
    This script pulls the data for a given date from the Wikimedia
    Commons API, and writes it into a .TSV file to be eventually read
    into our DB.

    Required Arguments:

    date:  Date String in the form YYYY-MM-DD.  This is the date for
           which running the script will pull data.
    """

    logger.info(f'Processing Wikimedia Commons API for date: {date}')

    continue_token = {}
    total_images = 0
    start_timestamp, end_timestamp = _derive_timestamp_pair(date)

    while True:
        image_batch, continue_token = _get_image_batch(
            start_timestamp,
            end_timestamp,
            continue_token=continue_token)
        logger.info(f'Continue Token: {continue_token}')
        image_pages = _get_image_pages(image_batch)
        if image_pages:
            _process_image_pages(image_pages)
            total_images = image_store.total_images
        logger.info(f'Total Images so far: {total_images}')
        if not continue_token:
            break

    image_store.commit()
    total_images = image_store.total_images
    logger.info(f'Total images: {total_images}')
    logger.info('Terminated!')


def _derive_timestamp_pair(date):
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    utc_date = date_obj.replace(tzinfo=timezone.utc)
    start_timestamp = str(int(utc_date.timestamp()))
    end_timestamp = str(int((utc_date + timedelta(days=1)).timestamp()))
    return start_timestamp, end_timestamp


def _get_image_batch(
        start_timestamp,
        end_timestamp,
        continue_token={},
        retries=5
):
    query_params = _build_query_params(
        start_timestamp,
        end_timestamp,
        continue_token=continue_token
    )
    image_batch = None
    for _ in range(MEAN_GLOBAL_USAGE_LIMIT):
        response_json = (
            delayed_requester.
            get_response_json(
                ENDPOINT,
                retries=retries,
                query_params=query_params,
                headers=DEFAULT_REQUEST_HEADERS,
                timeout=60
            )
        )

        if response_json is None:
            image_batch = None
            new_continue_token = None
            break
        else:
            new_continue_token = response_json.pop('continue', {})
            logger.debug(f'new_continue_token: {new_continue_token}')
            query_params.update(new_continue_token)
            image_batch = _merge_response_jsons(image_batch, response_json)

        if 'batchcomplete' in response_json:
            logger.debug('Found batchcomplete')
            break

    return image_batch, new_continue_token


def _get_image_pages(image_batch):
    image_pages = None

    if image_batch is not None:
        image_pages = image_batch.get('query', {}).get('pages')

    if image_pages is None:
        logger.warning(f'No pages in the image_batch: {image_batch}')
    else:
        logger.info(f'Got {len(image_pages)} pages')

    return image_pages


def _process_image_pages(image_pages):
    for i in image_pages.values():
        _process_image_data(i)


def _build_query_params(
        start_date,
        end_date,
        continue_token={},
        default_query_params=DEFAULT_QUERY_PARAMS,
):
    query_params = default_query_params.copy()
    query_params.update(
        gaistart=start_date,
        gaiend=end_date,
    )
    query_params.update(continue_token)
    return query_params


def _merge_response_jsons(left_json, right_json):
    # Note that we will keep the continue value from the right json in
    # the merged output!  This is because we assume the right json is
    # the later one in the sequence of responses.
    if left_json is None:
        return right_json

    left_pages = _get_image_pages(left_json)
    right_pages = _get_image_pages(right_json)

    if (
            left_pages is None
            or right_pages is None
            or left_pages.keys() != right_pages.keys()
    ):
        logger.warning('Cannot merge responses with different pages!')
        merged_json = None
    else:
        merged_json = deepcopy(left_json)
        merged_json.update(right_json)
        merged_pages = _get_image_pages(merged_json)
        merged_pages.update({
            k: _merge_image_pages(left_pages[k], right_pages[k])
            for k in left_pages
        })

    return merged_json


def _merge_image_pages(left_page, right_page):
    merged_page = deepcopy(left_page)
    merged_globalusage = (
        left_page['globalusage'] + right_page['globalusage']
    )
    merged_page.update(right_page)
    merged_page['globalusage'] = merged_globalusage

    return merged_page


def _process_image_data(image_data):
    foreign_id = image_data.get('pageid')
    logger.debug(f'Processing page ID: {foreign_id}')
    image_info = _get_image_info_dict(image_data)
    valid_mediatype = _check_mediatype(image_info)
    if not valid_mediatype:
        return

    image_url = image_info.get('url')
    creator, creator_url = _extract_creator_info(image_info)

    image_store.add_item(
        foreign_landing_url=image_info.get('descriptionshorturl'),
        image_url=image_url,
        license_url=_get_license_url(image_info),
        foreign_identifier=foreign_id,
        width=image_info.get('width'),
        height=image_info.get('height'),
        creator=creator,
        creator_url=creator_url,
        title=image_data.get('title'),
        meta_data=_create_meta_data_dict(image_data)
    )


def _get_image_info_dict(image_data):
    image_info_list = image_data.get('imageinfo')
    if image_info_list:
        image_info = image_info_list[0]
    else:
        image_info = {}
    return image_info


def _check_mediatype(image_info, image_mediatypes=IMAGE_MEDIATYPES):
    valid_mediatype = True
    image_mediatype = image_info.get('mediatype')
    if image_mediatype not in image_mediatypes:
        logger.debug(
            f'Incorrect mediatype: {image_mediatype} not in {image_mediatypes}'
        )
        valid_mediatype = False
    else:
        valid_mediatype = True
    return valid_mediatype


def _extract_date_info(image_info):
    date_originally_created = (
        image_info
        .get('extmetadata', {})
        .get('DateTimeOriginal', {})
        .get('value', '')
    )

    last_modified_at_source = (
        image_info
        .get('extmetadata', {})
        .get('DateTime', {})
        .get('value', '')
    )
    return (date_originally_created, last_modified_at_source)


def _extract_creator_info(image_info):
    artist_string = (
        image_info
        .get('extmetadata', {})
        .get('Artist', {})
        .get('value', '')
    )

    if not artist_string:
        return (None, None)

    artist_elem = html.fromstring(artist_string)
    # We take all text to replicate what is shown on Wikimedia Commons
    artist_text = ''.join(artist_elem.xpath('//text()')).strip()
    url_list = list(artist_elem.iterlinks())
    artist_url = _cleanse_url(url_list[0][2]) if url_list else None
    return (artist_text, artist_url)


def _extract_category_info(image_info):
    categories_string = (
        image_info
        .get('extmetadata', {})
        .get('Categories', {})
        .get('value', '')
    )

    categories_list = categories_string.split('|')
    return categories_list


def _get_license_url(image_info):
    return (
        image_info
        .get('extmetadata', {})
        .get('LicenseUrl', {})
        .get('value', '')
        .strip()
    )


def _create_meta_data_dict(image_data):
    meta_data = {}
    global_usage_length = len(image_data.get('globalusage', []))
    image_info = _get_image_info_dict(image_data)
    date_originally_created, last_modified_at_source = _extract_date_info(
        image_info)
    categories_list = _extract_category_info(image_info)
    description = (
        image_info
        .get('extmetadata', {})
        .get('ImageDescription', {})
        .get('value')
    )
    if description:
        description_text = ' '.join(
            html.fromstring(description).xpath('//text()')
        ).strip()
        meta_data['description'] = description_text
    meta_data['global_usage_count'] = global_usage_length
    meta_data['date_originally_created'] = date_originally_created
    meta_data['last_modified_at_source'] = last_modified_at_source
    meta_data['categories'] = categories_list
    return meta_data


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
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
        level=logging.INFO
    )
    parser = argparse.ArgumentParser(
        description='Wikimedia Commons API Job',
        add_help=True,
    )
    parser.add_argument(
        '--date',
        help='Identify images uploaded on a date (format: YYYY-MM-DD).')
    args = parser.parse_args()
    if args.date:
        date = args.date
    else:
        date_obj = datetime.now() - timedelta(days=2)
        date = datetime.strftime(date_obj, '%Y-%m-%d')

    main(date)

"""
Content Provider:       Wikimedia Commons

ETL Process:            Use the API to identify all CC-licensed images.

Output:                 TSV file containing the image, the respective
                        meta-data.

Notes:                  https://commons.wikimedia.org/wiki/API:Main_page
                        No rate limit specified.
"""

import argparse
from datetime import datetime, timedelta, timezone
import logging
import os
from urllib.parse import urlparse

import lxml.html as html

import common.requester as requester
import common.storage.image as image

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

LIMIT = 500
DELAY = 1
HOST = 'commons.wikimedia.org'
ENDPOINT = f'https://{HOST}/w/api.php'
PROVIDER = 'wikimedia'
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
    'prop': 'imageinfo',
    'iiprop': 'url|user|dimensions|extmetadata',
    'format': 'json',
}

delayed_requester = requester.DelayedRequester(DELAY)
image_store = image.ImageStore(provider=PROVIDER)


def main(date):
    logger.info(f'Processing Wikimedia Commons API for date: {date}')

    continue_token = {}
    total_images = 0
    start_ts, end_ts = _derive_timestamp_pair(date)

    while True:
        image_batch = _get_image_batch(
            start_ts,
            end_ts,
            continue_token=continue_token)
        image_pages, continue_token = _get_image_pages(image_batch)
        if image_pages:
            total_images = _process_image_pages(image_pages)
        logger.info(f'Total Images so far: {total_images}')
        if not continue_token:
            break

    total_images = image_store.commit()
    logger.info('Total images: {}'.format(total_images))
    logger.info('Terminated!')


def _derive_timestamp_pair(date):
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    utc_date = date_obj.replace(tzinfo=timezone.utc)
    start_ts = str(int(utc_date.timestamp()))
    end_ts = str(int((utc_date + timedelta(days=1)).timestamp()))
    return start_ts, end_ts


def _get_image_batch(start_ts, end_ts, continue_token, retries=5):
    query_params = _build_query_params(
        start_ts,
        end_ts,
        continue_token=continue_token,
    )
    image_batch = _get_response_json(query_params, retries=retries)
    return image_batch


def _get_image_pages(image_batch):
    image_pages = None
    continue_token = {}

    if image_batch is not None and image_batch.get('query'):
        continue_token = image_batch.get('continue', {})
        image_pages = image_batch['query'].get('pages')

        logger.info(f'Got {len(image_pages)} pages')
        logger.info(f'Continue Token: {continue_token}')

    if not continue_token:
        logger.debug(f'Final image_batch: {image_batch}')

    return image_pages, continue_token


def _process_image_pages(image_pages):
    for i in image_pages.values():
        total_images = _process_image_data(i)
    return total_images


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


def _get_response_json(
        query_params,
        endpoint=ENDPOINT,
        request_headers=DEFAULT_REQUEST_HEADERS,
        retries=0,
):
    response_json = None

    if retries < 0:
        logger.warning('No retries remaining.  Returning Nonetype.')
        return response_json

    response = delayed_requester.get(
        endpoint,
        params=query_params,
        headers=request_headers
    )
    if response is not None and response.status_code == 200:
        try:
            response_json = response.json()
        except Exception as e:
            logger.warning(f'Could not get response_json.\n{e}')
            response_json = None

    if (
            response_json is None
            or response_json.get('error') is not None
    ):
        logger.warning(f'Bad response_json:  {response_json}')
        logger.warning(
            'Retrying:\n_get_response_json(\n'
            f'    {endpoint},\n'
            f'    {query_params},\n'
            f'    {request_headers}'
            f'    retries={retries - 1}'
            ')'
        )
        response_json = _get_response_json(
            query_params,
            endpoint=endpoint,
            request_headers=request_headers,
            retries=retries - 1
        )

    return response_json


def _process_image_data(image_data):
    foreign_id = image_data.get('pageid')
    logger.debug('Processing page ID: {}'.format(foreign_id))
    image_info = _get_image_info_dict(image_data)
    image_url = image_info.get('url')
    creator, creator_url = _extract_creator_info(image_info)

    return image_store.add_item(
        foreign_landing_url=image_info.get('descriptionshorturl'),
        image_url=image_url,
        license_url=_get_license_url(image_info),
        foreign_identifier=foreign_id,
        width=image_info.get('width'),
        height=image_info.get('height'),
        creator=creator,
        creator_url=creator_url,
        title=image_data.get('title'),
        meta_data=_create_meta_data_dict(image_info)
    )


def _get_image_info_dict(image_data):
    image_info_list = image_data.get('imageinfo')
    if image_info_list:
        image_info = image_info_list[0]
    else:
        image_info = {}
    return image_info


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


def _get_license_url(image_info):
    return (
        image_info
        .get('extmetadata', {})
        .get('LicenseUrl', {})
        .get('value', '')
        .strip()
    )


def _create_meta_data_dict(image_info):
    meta_data = {}
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

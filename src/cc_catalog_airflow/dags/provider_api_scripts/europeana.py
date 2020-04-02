"""
Content Provider:       Europeana

ETL Process:            Use the API to identify all CC licensed images.

Output:                 TSV file containing the images and the
                        respective meta-data.

Notes:                  https://www.europeana.eu/api/v2/search.json
"""

import argparse
from datetime import datetime, timedelta, timezone
import logging
import os

from common.requester import DelayedRequester
from common.storage import image

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

DELAY = 1.0
RESOURCES_PER_REQUEST = '10'
PROVIDER = 'europeana'
API_KEY = os.getenv('EUROPEANA_API_KEY')
ENDPOINT = 'https://www.europeana.eu/api/v2/search.json?'
RESOURCE_TYPE = 'IMAGE'
# DATE_TYPES = ['created', 'update']

LICENSE_INFO = {
    '1': ('by-nc-sa', '2.0'),
    '2': ('by-nc', '2.0'),
    '3': ('by-nc-nd', '2.0'),
    '4': ('by', '2.0'),
    '5': ('by-sa', '2.0'),
    '6': ('by-nd', '2.0'),
    '9': ('cc0', '1.0'),
    '10': ('pdm', '1.0'),
    # '11': ('ooc-nc', '1.0'),
}

DEFAULT_QUERY_PARAMS = {
    'wskey': API_KEY,
    'query': '*',
    'profile': 'rich',
    'reusability': ['open', 'restricted'],
    'sort': ['europeana_id+desc', 'timestamp_created_epoch+desc'],
    'rows': RESOURCES_PER_REQUEST,
    'media': 'true',
    'start': 1,
    'qf': [f'TYPE:{RESOURCE_TYPE}', 'provider_aggregation_edm_isShownBy:*'],
}

delayed_requester = DelayedRequester(DELAY)
image_store = image.ImageStore(provider=PROVIDER)


def main(date):
    logger.info(f'Processing Europeana API for date: {date}')

    start_timestamp, end_timestamp = _derive_timestamp_pair(date)
    _get_pagewise(start_timestamp, end_timestamp)

    logger.info('Terminated!')


def _get_pagewise(start_timestamp, end_timestamp):
    cursor = '*'
    prev_cursor = ''
    total_number_of_images = 0
    images_retrieved = 0

    while cursor != prev_cursor:
        image_list, next_cursor, total_number_of_images = _get_image_list(
            start_timestamp,
            end_timestamp,
            cursor
        )

        if image_list is not None:
            images_retrieved += len(image_list)
            logger.info(
                f'Images retrieved: {images_retrieved} of {total_number_of_images}')
            prev_cursor = cursor
            cursor = next_cursor

        else:
            logger.warning('No image data!  Attempting to continue')


def _get_image_list(
        start_timestamp,
        end_timestamp,
        cursor,
        endpoint=ENDPOINT,
        max_tries=6  # one original try, plus 5 retries
):
    for try_number in range(max_tries):

        query_param_dict = _build_query_param_dict(
            start_timestamp,
            end_timestamp,
            cursor
        )

        response = delayed_requester.get(
            endpoint,
            params=query_param_dict,
        )

        logger.debug('response.status_code: {response.status_code}')
        response_json = _extract_response_json(response)
        image_list, next_cursor, total_number_of_images = _extract_image_list_from_json(
            response_json)

        if (image_list is not None) and (next_cursor is not None):
            break

    if try_number == max_tries - 1 and (
            (image_list is None) or (next_cursor is None)):
        logger.warning('No more tries remaining. Returning None types.')
        return None, None
    else:
        return image_list, next_cursor, total_number_of_images


def _extract_response_json(response):
    if response is not None and response.status_code == 200:
        try:
            response_json = response.json()
        except Exception as e:
            logger.warning(f'Could not get image_data json.\n{e}')
            response_json = None
    else:
        response_json = None

    return response_json


def _extract_image_list_from_json(response_json):
    if (
            response_json is None
            or response_json.get('success') != True
    ):
        image_list, next_cursor = None, None
    else:
        image_list = response_json.get('items')
        next_cursor = response_json.get('nextCursor')
        total_number_of_images = response_json.get('totalResults')

    return image_list, next_cursor, total_number_of_images


def _build_query_param_dict(
        start_timestamp,
        end_timestamp,
        cursor,
        api_key=API_KEY,
        default_query_param=DEFAULT_QUERY_PARAMS,
):
    query_param_dict = default_query_param.copy()
    query_param_dict.update(
        {
            'timestamp_created_epoch': f'{start_timestamp}TO{end_timestamp}',
            'cursor': cursor,
        }
    )

    return query_param_dict


def _derive_timestamp_pair(date):
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    utc_date = date_obj.replace(tzinfo=timezone.utc)
    start_timestamp = str(int(utc_date.timestamp()))
    end_timestamp = str(int((utc_date + timedelta(days=1)).timestamp()))
    return start_timestamp, end_timestamp


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Europeana API Job',
        add_help=True
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

"""
Content Provider:       Flickr

ETL Process:            Use the API to identify all CC licensed images.

Output:                 TSV file containing the images and the
                        respective meta-data.

Notes:                  https://www.flickr.com/help/terms/api
                        Rate limit: 3600 requests per hour.
"""

import argparse
import logging
import os
from datetime import datetime, timedelta, timezone

import lxml.html as html

from common.requester import DelayedRequester
from common.storage import image

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

DELAY = 1.0
LIMIT = 500
MAX_TAGS = 40
PROVIDER = 'flickr'
API_KEY = os.getenv('FLICKR_API_KEY')
ENDPOINT = 'https://api.flickr.com/services/rest/?method=flickr.photos.search'
DATE_TYPES = ['taken', 'upload']

LICENSE_INFO = {
    '1': ('by-nc-sa', '2.0'),
    '2': ('by-nc', '2.0'),
    '3': ('by-nc-nd', '2.0'),
    '4': ('by', '2.0'),
    '5': ('by-sa', '2.0'),
    '6': ('by-nd', '2.0'),
    '9': ('cc0', '1.0'),
    '10': ('pdm', '1.0'),
}

DEFAULT_QUERY_PARAMS = {
    'media': 'photos',
    'content_type': 1,
    'extras': (
        'description,license,date_upload,date_taken,owner_name,tags,o_dims,'
        'url_t,url_s,url_m,url_l,views'
    ),
    'format': 'json',
    'nojsoncallback': 1,
}

delayed_requester = DelayedRequester(DELAY)
image_store = image.ImageStore(provider=PROVIDER)


def main(date):
    logger.info(f'Processing Flickr API for date: {date}')

    start_timestamp, end_timestamp = _derive_timestamp_pair(date)

    for date_type in DATE_TYPES:
        logger.info(f'processing date type {date_type}')
        total_images = _process_date(start_timestamp, end_timestamp, date_type)

    total_images = image_store.commit()
    logger.info(f'Total images: {total_images}')
    logger.info('Terminated!')


def _derive_timestamp_pair(date):
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    utc_date = date_obj.replace(tzinfo=timezone.utc)
    start_timestamp = str(int(utc_date.timestamp()))
    end_timestamp = str(int((utc_date + timedelta(days=1)).timestamp()))
    return start_timestamp, end_timestamp


def _process_date(start_timestamp, end_timestamp, date_type):
    total_pages = 1
    page_number = 1
    total_images = 0

    while page_number <= total_pages:
        logger.info(f'Processing page: {page_number} of {total_pages}')

        image_list, new_total_pages = _get_image_list(
            start_timestamp,
            end_timestamp,
            date_type,
            page_number
        )

        if image_list is not None:
            total_images = _process_image_list(image_list)
            logger.info(f'Total Images so far: {total_images}')
        else:
            logger.warning('No image data!  Attempting to continue')

        if new_total_pages is not None and total_pages <= new_total_pages:
            total_pages = new_total_pages

        page_number += 1

    logger.info(f'Total pages processed: {page_number}')

    return total_images


def _get_image_list(
        start_timestamp,
        end_timestamp,
        date_type,
        page_number,
        endpoint=ENDPOINT,
        retries=5
):
    query_param_dict = _build_query_param_dict(
        start_timestamp,
        end_timestamp,
        page_number,
        date_type,
    )

    if retries < 0:
        logger.warning('No retries remaining.  Returning Nonetypes.')
        return None, None
    else:
        response = delayed_requester.get(
            endpoint,
            params=query_param_dict,
        )

    logger.debug('response.status_code: {response.status_code}')

    if response is not None and response.status_code == 200:
        try:
            response_json = response.json()
        except Exception as e:
            logger.warning(f'Could not get image_data json.\n{e}')
            response_json = None
    else:
        response_json = None

    image_list, total_pages = _extract_image_list_from_json(response_json)

    if image_list is None or total_pages is None:
        image_list, total_pages = _get_image_list(
            start_timestamp,
            end_timestamp,
            date_type,
            page_number,
            retries=retries - 1
        )

    return image_list, total_pages


def _build_query_param_dict(
        start_timestamp,
        end_timestamp,
        cur_page,
        date_type,
        api_key=API_KEY,
        license_info=LICENSE_INFO,
        limit=LIMIT,
        default_query_param=DEFAULT_QUERY_PARAMS,
):
    query_param_dict = default_query_param.copy()
    query_param_dict.update(
        {
            f'min_{date_type}_date': start_timestamp,
            f'max_{date_type}_date': end_timestamp,
            'page': cur_page,
            'api_key': api_key,
            'license': ','.join(license_info.keys()),
            'per_page': limit,
        }
    )

    return query_param_dict


def _extract_image_list_from_json(response_json):
    if (
            response_json is None
            or response_json.get('stat') != 'ok'
    ):
        image_data = None
    else:
        image_data = response_json.get('photos')

    if image_data is not None:
        image_list = image_data.get('photo')
        total_pages = image_data.get('pages')
    else:
        image_list, total_pages = None, None

    return image_list, total_pages


def _process_image_list(image_list):
    for image_data in image_list:
        total_images = _process_image_data(image_data)

    return total_images


def _process_image_data(image_data):
    logger.debug(f'Processing image data: {image_data}')
    image_url, height, width = _get_image_url(image_data)
    license_, license_version = _get_license(image_data.get('license'))

    if 'owner' in image_data:
        creator_url = (
            f'https://www.flickr.com/photos/{image_data["owner"].strip()}'
        )
    else:
        creator_url = None

    if creator_url is None:
        logger.warning('No creator_url constructed!')

    foreign_id = image_data.get('id')
    if foreign_id is None:
        logger.warning('No foreign_id in image_data!')

    if foreign_id and creator_url:
        foreign_landing_url = '{}/{}'.format(creator_url, foreign_id)
    else:
        foreign_landing_url = None

    logger.debug(f'foreign_landing_url: {foreign_landing_url}')

    return image_store.add_item(
        foreign_landing_url=foreign_landing_url,
        image_url=image_url,
        thumbnail_url=image_data.get('url_s'),
        license_=license_,
        license_version=license_version,
        foreign_identifier=foreign_id,
        width=width,
        height=height,
        creator=image_data.get('ownername'),
        creator_url=creator_url,
        title=image_data.get('title'),
        meta_data=_create_meta_data_dict(image_data),
        raw_tags=_create_tags_list(image_data),
    )


def _get_image_url(image_data):
    # prefer large, then medium, then small images
    for size in ['l', 'm', 's']:
        url_key = 'url_{}'.format(size)
        height_key = 'height_{}'.format(size)
        width_key = 'width_{}'.format(size)
        if url_key in image_data:
            return (
                image_data.get(url_key),
                image_data.get(height_key),
                image_data.get(width_key)
            )

    logger.warning('Image not detected!')
    return None, None, None


# TODO write tests for this
def _get_license(license_id, license_info=LICENSE_INFO):
    license_id = str(license_id)

    if license_id not in license_info:
        logger.warning('Unknown license ID!')

    license_, license_version = license_info.get(license_id, (None, None))

    return license_, license_version


def _create_meta_data_dict(image_data):
    meta_data = {
        'pub_date': image_data.get('dateupload'),
        'date_taken': image_data.get('datetaken'),
        'views': image_data.get('views'),
    }
    description = image_data.get('description', {}) .get('_content')
    logger.debug(f'description: {description}')
    if description.strip():
        try:
            description_text = ' '.join(
                html.fromstring(description).xpath('//text()')
            ).strip()[:2000]  # We don't want arbitrarily long descriptions.
            meta_data['description'] = description_text
        except Exception as e:
            logger.warning(f'Could not parse description {description}!\n{e}')

    return {k: v for k, v in meta_data.items() if v is not None}


def _create_tags_list(image_data, max_tags=MAX_TAGS):
    raw_tags = None
    raw_tag_string = image_data.get('tags', '').strip()
    if raw_tag_string:
        raw_tags = list(set(raw_tag_string.split()))[:max_tags]

    return raw_tags


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Flickr API Job',
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

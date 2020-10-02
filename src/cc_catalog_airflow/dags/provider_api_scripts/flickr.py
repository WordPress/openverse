"""
Content Provider:       Flickr

ETL Process:            Use the API to identify all CC licensed images.

Output:                 TSV file containing the images and the
                        respective meta-data.

Notes:                  https://www.flickr.com/help/terms/api
                        Rate limit: 3600 requests per hour.
"""

import argparse
from datetime import datetime, timedelta, timezone
import logging
import os

import lxml.html as html

from common.requester import DelayedRequester
from common.storage import image
from util.loader import provider_details as prov

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

DELAY = 1.0
LIMIT = 500
MAX_TAG_STRING_LENGTH = 2000
MAX_DESCRIPTION_LENGTH = 2000
PROVIDER = prov.FLICKR_DEFAULT_PROVIDER
API_KEY = os.getenv('FLICKR_API_KEY')
ENDPOINT = 'https://api.flickr.com/services/rest/'
PHOTO_URL_BASE = prov.FLICKR_PHOTO_URL_BASE
DATE_TYPE = 'upload'
# DAY_DIVISION is an integer that gives how many equal portions we should
# divide a 24-hour period into for requesting photo data.  For example,
# DAY_DIVISION = 24 would mean dividing the day into hours, and requesting the
# photo data for each hour of the day separately.  This is necessary because
# if we request too much at once, the API will return fallacious results.
DAY_DIVISION = 48  # divide into half hour increments
# SUB_PROVIDERS is a collection of providers within Flickr which are
# valuable to a broad audience
SUB_PROVIDERS = prov.FLICKR_SUB_PROVIDERS

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
    'method': 'flickr.photos.search',
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

    timestamp_pairs = _derive_timestamp_pair_list(date)
    date_type = DATE_TYPE

    for start_timestamp, end_timestamp in timestamp_pairs:
        total_images = _process_interval(
            start_timestamp,
            end_timestamp,
            date_type
        )

    total_images = image_store.commit()
    logger.info(f'Total images: {total_images}')
    logger.info('Terminated!')


def _derive_timestamp_pair_list(date, day_division=DAY_DIVISION):
    day_seconds = 86400
    default_day_division = 48
    portion = int(day_seconds / day_division)
    # We double check the day can be evenly divided by the requested division
    try:
        assert portion == day_seconds / day_division
    except AssertionError:
        logger.warning(
            f'day_division {day_division} does not divide the day evenly!  '
            f'Using the default of {default_day_division}'
        )
        day_division = default_day_division
        portion = int(day_seconds / day_division)

    utc_date = datetime.strptime(date, '%Y-%m-%d').replace(tzinfo=timezone.utc)

    def _ts_string(d):
        return str(int(d.timestamp()))

    pair_list = [
        (
            _ts_string(utc_date + timedelta(seconds=i * portion)),
            _ts_string(utc_date + timedelta(seconds=(i+1) * portion))
        )
        for i in range(day_division)
    ]
    return pair_list


def _process_interval(start_timestamp, end_timestamp, date_type):
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
        max_tries=6  # one original try, plus 5 retries
):
    for try_number in range(max_tries):
        query_param_dict = _build_query_param_dict(
            start_timestamp,
            end_timestamp,
            page_number,
            date_type,
        )
        response = delayed_requester.get(
            endpoint,
            params=query_param_dict,
        )

        logger.debug('response.status_code: {response.status_code}')
        response_json = _extract_response_json(response)
        image_list, total_pages = _extract_image_list_from_json(response_json)

        if (image_list is not None) and (total_pages is not None):
            break

    if try_number == max_tries - 1 and (
            (image_list is None) or (total_pages is None)):
        logger.warning('No more tries remaining. Returning Nonetypes.')
        return None, None
    else:
        return image_list, total_pages


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
            response_json is None or response_json.get('stat') != 'ok'
    ):
        image_page = None
    else:
        image_page = response_json.get('photos')

    if image_page is not None:
        image_list = image_page.get('photo')
        total_pages = image_page.get('pages')
    else:
        image_list, total_pages = None, None

    return image_list, total_pages


def _process_image_list(image_list):
    total_images = 0
    for image_data in image_list:
        total_images = _process_image_data(image_data)

    return total_images


def _process_image_data(image_data, sub_providers=SUB_PROVIDERS,
                        provider=PROVIDER):
    logger.debug(f'Processing image data: {image_data}')
    image_url, height, width = _get_image_url(image_data)
    license_, license_version = _get_license(image_data.get('license'))
    creator_url = _build_creator_url(image_data)
    foreign_id = image_data.get('id')
    if foreign_id is None:
        logger.warning('No foreign_id in image_data!')
    foreign_landing_url = _build_foreign_landing_url(creator_url, foreign_id)

    owner = image_data.get('owner').strip()
    source = next((s for s in sub_providers if owner in sub_providers[s]),
                  provider)

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
        source=source
    )


def _build_creator_url(image_data, photo_url_base=PHOTO_URL_BASE):
    owner = image_data.get('owner')
    if owner is not None:
        creator_url = _url_join(photo_url_base, owner.strip())
        logger.debug(f'creator_url: {creator_url}')
    else:
        logger.warning('No creator_url constructed!')
        creator_url = None

    return creator_url


def _build_foreign_landing_url(creator_url, foreign_id):
    if creator_url and foreign_id:
        foreign_landing_url = _url_join(creator_url, foreign_id)
        logger.debug(f'foreign_landing_url: {foreign_landing_url}')
    else:
        logger.warning('No foreign_landing_url constructed!')
        foreign_landing_url = None

    return foreign_landing_url


def _url_join(*args):
    return '/'.join(
        [s.strip('/') for s in args]
    )


def _get_image_url(image_data):
    # prefer large, then medium, then small images
    for size in ['l', 'm', 's']:
        url_key = f'url_{size}'
        height_key = f'height_{size}'
        width_key = f'width_{size}'
        if url_key in image_data:
            return (
                image_data.get(url_key),
                image_data.get(height_key),
                image_data.get(width_key)
            )

    logger.warning('Image not detected!')
    return None, None, None


def _get_license(license_id, license_info=LICENSE_INFO):
    license_id = str(license_id)

    if license_id not in license_info:
        logger.warning('Unknown license ID!')

    license_, license_version = license_info.get(license_id, (None, None))

    return license_, license_version


def _create_meta_data_dict(
        image_data,
        max_description_length=MAX_DESCRIPTION_LENGTH
):
    meta_data = {
        'pub_date': image_data.get('dateupload'),
        'date_taken': image_data.get('datetaken'),
        'views': image_data.get('views'),
    }
    description = image_data.get('description', {}) .get('_content', '')
    logger.debug(f'description: {description}')
    if description.strip():
        try:
            description_text = ' '.join(
                html.fromstring(description).xpath('//text()')
            ).strip()[:max_description_length]
            meta_data['description'] = description_text
        except Exception as e:
            logger.warning(f'Could not parse description {description}!\n{e}')

    return {k: v for k, v in meta_data.items() if v is not None}


def _create_tags_list(
        image_data,
        max_tag_string_length=MAX_TAG_STRING_LENGTH
):
    raw_tags = None
    # We limit the input tag string length, not the number of tags,
    # since tags could otherwise be arbitrarily long, resulting in
    # arbitrarily large data in the DB.
    raw_tag_string = image_data.get('tags', '').strip()[:max_tag_string_length]
    if raw_tag_string:
        # We sort for further consistency between runs, saving on
        # inserts into the DB later.
        raw_tags = sorted(list(set(raw_tag_string.split())))

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

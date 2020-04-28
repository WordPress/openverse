"""
Content Provider:  Smithsonian

ETL Process:       Use the API to identify all CC licensed images.

Output:            TSV file containing the images and the respective
                   meta-data.

Notes:             None
"""
import logging
import os

from common.storage import image
from common import requester

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

API_KEY = os.getenv('DATA_GOV_API_KEY')
DELAY = 5.0
LIMIT = 200  # number of rows to pull at once
ENDPOINT = 'https://api.si.edu/openaccess/api/v1.0/search'
PROVIDER = 'smithsonian'
ZERO_URL = 'https://creativecommons.org/publicdomain/zero/1.0/'
DEFAULT_PARAMS = {
    'api_key': API_KEY,
    'rows': LIMIT
}

image_store = image.ImageStore(provider=PROVIDER)
delayed_requester = requester.DelayedRequester(delay=DELAY)


def main():
    _process_unit_code('ACM')
    total_images = image_store.commit()
    logger.info(f'Total images:  {total_images}')


def _process_unit_code(unit_code, endpoint=ENDPOINT, limit=LIMIT):
    logger.info(f'Processing unit code:  {unit_code}')
    row_offset = 0
    total_rows = 1
    while row_offset < total_rows:
        query_params = _build_query_params(unit_code, row_offset)
        response_json = delayed_requester.get_response_json(
            endpoint,
            retries=3,
            query_params=query_params
        )
        logger.info(f'response:  {response_json.keys()}')
        _process_response_json(response_json)
        total_rows = response_json.get('response', {}).get('rowCount', 0)
        row_offset += limit


def _build_query_params(unit_code, row_offset, default_params=DEFAULT_PARAMS):
    query_params = default_params.copy()
    query_string = f'unit_code:{unit_code} AND online_media_type:Images'
    query_params.update(q=query_string, start=row_offset)
    return query_params


def _process_response_json(response_json):
    logger.info('processing response')
    rows = response_json.get('response', {}).get('rows', [])
    for row in rows:
        image_list = (
            row
            .get('content', {})
            .get('descriptiveNonRepeating', {})
            .get('online_media', {})
            .get('media')
        )
        if image_list is not None:
            title = row.get('title')
            foreign_landing_url = row.get('content', {}).get('descriptiveNonRepeating', {}).get('guid')
            _process_image_list(title, foreign_landing_url, image_list)


def _process_image_list(title, foreign_landing_url, image_list, license_url=ZERO_URL):
    for image_data in image_list:
        if (
                image_data.get('type') == 'Images'
                and image_data.get('usage', {}).get('access') == 'CC0'
        ):
            image_store.add_item(
                foreign_landing_url=foreign_landing_url,
                image_url=image_data.get('content'),
                thumbnail_url=image_data.get('thumbnail'),
                license_url=license_url,
                foreign_identifier=image_data.get('idsId'),
                title=title,
            )


if __name__ == '__main__':
    main()

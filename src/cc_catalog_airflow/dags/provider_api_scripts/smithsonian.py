"""
Content Provider:  Smithsonian

ETL Process:       Use the API to identify all CC licensed images.

Output:            TSV file containing the images and the respective
                   meta-data.

Notes:             None
"""
import logging
import os
import sys

from common.storage import image
from common import requester

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

API_KEY = os.getenv('DATA_GOV_API_KEY')
DELAY = 5.0
LIMIT = 1000  # number of rows to pull at once
API_ROOT = 'https://api.si.edu/openaccess/api/v1.0/'
SEARCH_ENDPOINT = API_ROOT + 'search'
UNIT_CODE_ENDPOINT = API_ROOT + 'terms/unit_code'
PROVIDER = 'smithsonian'
ZERO_URL = 'https://creativecommons.org/publicdomain/zero/1.0/'
DEFAULT_PARAMS = {
    'api_key': API_KEY,
    'rows': LIMIT
}

image_store = image.ImageStore(provider=PROVIDER)
delayed_requester = requester.DelayedRequester(delay=DELAY)


def main():
    unit_codes = _get_unit_code_list()
    print(unit_codes)
    for unit_code in unit_codes:
        _process_unit_code(unit_code)
    total_images = image_store.commit()
    logger.info(f'Total images:  {total_images}')


def _get_unit_code_list(endpoint=UNIT_CODE_ENDPOINT, params=DEFAULT_PARAMS):
    response_json = delayed_requester.get_response_json(
        endpoint,
        retries=3,
        query_params=params
    )
    unit_codes = response_json.get('response', {}).get('terms', [])
    logger.info(f'Found {len(unit_codes)} unit codes')
    if len(unit_codes) == 0:
        logger.error('Could not get unit code list!  Aborting...')
        sys.exit(1)
    return unit_codes


def _process_unit_code(unit_code, endpoint=SEARCH_ENDPOINT, limit=LIMIT):
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
        content = row.get('content', {})
        descriptive_non_repeating = content.get('descriptiveNonRepeating', {})
        indexed_structured = content.get('indexedStructured', {})
        freetext = content.get('freetext')

        title = row.get('title')
        landing_url = _get_foreign_landing_url(descriptive_non_repeating)
        creator = _get_creator(indexed_structured, freetext)
        meta_data = _extract_meta_data(descriptive_non_repeating, freetext)
        tags = _extract_tags(indexed_structured)

        image_list = (
            descriptive_non_repeating
            .get('online_media', {})
            .get('media')
        )
        if image_list is not None:
            _process_image_list(
                image_list,
                landing_url,
                title,
                creator,
                meta_data,
                tags
            )


def _get_foreign_landing_url(dnr_dict):
    foreign_landing_url = dnr_dict.get('record_link')
    if foreign_landing_url is None:
        foreign_landing_url = dnr_dict.get('guid')

    return foreign_landing_url


def _get_creator(indexed_structured, freetext):
    creator_list = indexed_structured.get('name')
    if not creator_list:
        creator_list = freetext.get('name', [])
    creator = ' '.join(
        [
            item if type(item) == str else item.get('content', '')
            for item in creator_list
        ]
    )

    return creator


def _extract_meta_data(descriptive_non_repeating, freetext):
    description = ''
    label_texts = ''
    notes = freetext.get('notes', [])

    for note in notes:
        if note.get('label') == 'Description':
            description += ' ' + note.get('content', '')
        elif note.get('label') == 'Label Text':
            label_texts += ' ' + note.get('content', '')

    meta_data = {
        'unit_code': descriptive_non_repeating.get('unit_code'),
        'data_source': descriptive_non_repeating.get('data_source')
    }
    if description:
        meta_data.update(description=description)
    if label_texts:
        meta_data.update(label_texts=label_texts)

    return meta_data


def _extract_tags(indexed_structured):
    tags = (
        indexed_structured.get('date', [])
        + indexed_structured.get('object_type', [])
        + indexed_structured.get('topic', [])
        + indexed_structured.get('place', [])
    )
    return tags if tags else None


def _process_image_list(
        image_list,
        foreign_landing_url,
        title,
        creator,
        meta_data,
        tags,
        license_url=ZERO_URL
):
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
                creator=None,
                meta_data=meta_data,
                raw_tags=tags
            )


if __name__ == '__main__':
    main()

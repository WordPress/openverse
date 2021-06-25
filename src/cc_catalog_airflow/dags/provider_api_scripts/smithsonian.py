"""
Content Provider:  Smithsonian

ETL Process:       Use the API to identify all CC licensed images.

Output:            TSV file containing the images and the respective
                   meta-data.

Notes:             None
"""
from datetime import datetime
import json
import logging
import os

from common import DelayedRequester, ImageStore
from util.loader import provider_details as prov

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)

API_KEY = os.getenv('DATA_GOV_API_KEY')
DELAY = 5.0
HASH_PREFIX_LENGTH = 2
LIMIT = 1000  # number of rows to pull at once
API_ROOT = 'https://api.si.edu/openaccess/api/v1.0/'
SEARCH_ENDPOINT = API_ROOT + 'search'
UNITS_ENDPOINT = API_ROOT + 'terms/unit_code'
PROVIDER = prov.SMITHSONIAN_DEFAULT_PROVIDER
# SUB_PROVIDERS is a collection of all providers within smithsonian
SUB_PROVIDERS = prov.SMITHSONIAN_SUB_PROVIDERS
ZERO_URL = 'https://creativecommons.org/publicdomain/zero/1.0/'
DEFAULT_PARAMS = {
    'api_key': API_KEY,
    'rows': LIMIT
}
RETRIES = 3
# CREATOR_TYPES should have lower-case strings as keys, and integers as values.
# The integers given the preference order of the different creator types, with
# lower being more preferred. No preference is implied between two creator
# types with the same integer value.
CREATOR_TYPES = {
    'artist': 0,
    'artist/maker': 0,
    'attributed to': 0,
    'author': 0,
    'created_by': 0,
    'creator': 0,
    'created by': 0,
    'model maker': 0,
    'modeler': 0,
    'photographer': 0,
    'photograph by': 0,
    'written by': 0,

    'architect': 1,
    'designer': 1,
    'designed by': 1,
    'illustrator': 1,
    'illustrated by': 1,
    'cartoonist': 1,
    'weaver': 1,
    'composer': 1,
    'composed by': 1,
    'embroiderer': 1,
    'landscape architect': 1,
    'calligrapher': 1,
    'sculptor': 1,
    'jeweler': 1,
    'potter': 1,
    'ceramist': 1,

    'compiled by': 2,
    'engraver': 2,
    'etcher': 2,
    'maker': 2,
    'silversmith': 2,
    'producer': 2,
    'produced by': 2,
    'metal worker': 2,
    'carver': 2,
    'cartographer': 2,

    'print maker': 3,
    'painter': 3,
    'after': 3,
    'inventor': 3,
    'lithographer': 3,
    'attribution': 3,
    'former attribution': 3,

    'manufactured by': 4,
    'manufacturer': 4,
    'published by': 4,
    'publisher': 4,
    'editor': 4,

    'patentee': 5,

    'collector': 6
}

DESCRIPTION_TYPES = {'description', 'summary', 'caption', 'notes',
                     'description (brief)', 'description (spanish)',
                     'description (brief spanish)', 'gallery label',
                     'exhibition label', 'luce center label',
                     'publication label', 'new acquisition label'}
TAG_TYPES = ('date', 'object_type', 'topic', 'place')

image_store = ImageStore(provider=PROVIDER)
delayed_requester = DelayedRequester(delay=DELAY)


def main():
    """
    This script loops through all hash prefixes of a specified length,
    gathering metadata for each prefix in turn. A 'hash prefix' is
    defined as a search query that finds all objects whose hash ID
    starts with some string of hexits of a specified length (e.g.,
    '0a2*' is a hash prefix of length 3).
    """
    for hash_prefix in _get_hash_prefixes(HASH_PREFIX_LENGTH):
        total_rows = _process_hash_prefix(hash_prefix)
        logger.info(f'Total rows for {hash_prefix}:  {total_rows}')
    total_images = image_store.commit()
    logger.info(f'Total images:  {total_images}')


def gather_samples(
        units_endpoint=UNITS_ENDPOINT,
        default_query_params=None,
        target_dir='/tmp'
):
    """
    Gather random samples of the rows from each 'unit' at the SI.

    These units are treated separately since they have somewhat
    different data formats.

    This function is for gathering test data only, and is untested.
    """
    if default_query_params is None:
        default_query_params = DEFAULT_PARAMS
    query_params = default_query_params.copy()
    now_str = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')
    sample_dir = os.path.join(target_dir, f'si_samples_{now_str}')
    logger.info(f'Creating sample_dir {sample_dir}')
    os.mkdir(sample_dir)
    unit_code_json = delayed_requester.get_response_json(
        units_endpoint,
        query_params=query_params
    )
    unit_code_list = unit_code_json.get('response', {}).get('terms', [])
    logger.info(f'found unit codes: {unit_code_list}')
    for unit in unit_code_list:
        _gather_unit_sample(unit, sample_dir)


def _gather_unit_sample(
        unit,
        sample_dir,
        retries=RETRIES,
        endpoint=SEARCH_ENDPOINT
):
    """
    This function is for gathering test data only, and is untested.
    """
    logger.info(f'gathering sample for unit {unit}')
    for hash_prefix in [None, 'a', 'aa', 'aaa', 'aaaa', 'aaaaa']:
        query_params = _build_query_params(
            0,
            hash_prefix=hash_prefix,
            unit_code=unit
        )
        response_json = delayed_requester.get_response_json(
            endpoint,
            retries=retries,
            query_params=query_params
        )
        if response_json is None:
            logger.warning(f'response_json is NoneType for {unit}')
            break
        elif response_json['response']['rowCount'] == 0:
            logger.info(
                f'No rows found for unit_code {unit} with hash {hash_prefix}'
            )
            break
        elif response_json['response']['rowCount'] > 10000:
            logger.info(
                f'Too many rows:  {response_json["response"]["rowCount"]}'
            )
        else:
            total_rows = response_json['response']['rowCount']
            saved_rows = min(total_rows, 1000)
            logger.info(f'Saving {saved_rows} of {total_rows} rows')
            with open(os.path.join(sample_dir, f'{unit}.json'), 'w') as f:
                f.write(json.dumps(response_json, indent=2))
            break


def _get_hash_prefixes(prefix_length):
    max_prefix = 'f' * prefix_length
    format_string = f'0{prefix_length}x'
    for h in range(int(max_prefix, 16) + 1):
        yield format(h, format_string)


def _process_hash_prefix(
        hash_prefix,
        endpoint=SEARCH_ENDPOINT,
        limit=LIMIT,
        retries=RETRIES
):
    logger.info(f'Processing hash_prefix:  {hash_prefix}')
    total_images = 0
    row_offset = 0
    total_rows = 1
    while row_offset < total_rows:
        logger.debug(f'Row offset:  {row_offset}')
        query_params = _build_query_params(row_offset, hash_prefix=hash_prefix)
        response_json = delayed_requester.get_response_json(
            endpoint,
            retries=retries,
            query_params=query_params
        )
        if response_json is None:
            logger.warning('response_json is None!  Continuing...')
        else:
            new_total = _process_response_json(response_json)
            total_images = new_total if new_total is not None else total_images
            logger.info(f'Total images so far:  {total_images}')
            total_rows = response_json.get('response', {}).get('rowCount', 0)
        row_offset += limit
    return total_rows


def _build_query_params(
        row_offset,
        hash_prefix=None,
        default_params=None,
        unit_code=None
):
    if default_params is None:
        default_params = DEFAULT_PARAMS
    query_params = default_params.copy()
    query_string = 'online_media_type:Images AND media_usage:CC0'
    if hash_prefix is not None:
        query_string += f' AND hash:{hash_prefix}*'
    if unit_code is not None:
        query_string += f' AND unit_code:{unit_code}'
    query_params.update(q=query_string, start=row_offset)
    return query_params


def _process_response_json(response_json):
    logger.debug('processing response')
    total_images = None
    rows = _get_row_list(response_json)
    for row in rows:
        image_list = _get_image_list(row)
        if image_list:
            meta_data = _extract_meta_data(row)
            source = _extract_source(meta_data)
            total_images = _process_image_list(
                image_list,
                _get_foreign_landing_url(row),
                _get_title(row),
                _get_creator(row),
                meta_data,
                _extract_tags(row),
                source
            )
    return total_images


def _get_row_list(response_json):
    return _check_type(response_json.get('response', {}).get('rows'), list)


def _get_image_list(row):
    dnr_dict = _get_descriptive_non_repeating_dict(row)
    online_media = _check_type(dnr_dict.get('online_media'), dict)
    return _check_type(online_media.get('media'), list)


def _get_foreign_landing_url(row):
    logger.debug('Getting foreign_landing_url from row')
    dnr_dict = _get_descriptive_non_repeating_dict(row)
    foreign_landing_url = dnr_dict.get('record_link')
    if foreign_landing_url is None:
        foreign_landing_url = dnr_dict.get('guid')

    return foreign_landing_url


def _get_title(row):
    return row.get('title')


def _get_creator(row, creator_types=None):
    if creator_types is None:
        creator_types = CREATOR_TYPES.copy()
    freetext = _get_freetext_dict(row)
    indexed_structured = _get_indexed_structured_dict(row)
    ordered_freetext_creator_objects = sorted(
        [
            i for i in _check_type(freetext.get('name'), list)
            if type(i) == dict
            and (_check_type(i.get('label'), str).lower() in creator_types)
            and (_check_type(i.get('content'), str))
            and ('unknown' not in i.get('content').lower())
        ],
        key=lambda x: creator_types[x['label'].lower()]
    )

    indexed_structured_creator_generator = (
        i['content'] for i in _check_type(indexed_structured.get('name'), list)
        if type(i) == dict
        and (_check_type(i.get('type'), str).lower() == 'personal_main')
        and (_check_type(i.get('content'), str))
    )

    if ordered_freetext_creator_objects:
        first_creator_object = ordered_freetext_creator_objects[0]
        top_priority = creator_types[first_creator_object['label'].lower()]

        creators_list = [c['content'] for c in ordered_freetext_creator_objects
                         if top_priority == creator_types[c['label'].lower()]]

        creator = '; '.join(creators_list[:-1]) + ' and ' + creators_list[-1] \
            if len(creators_list) > 1 else creators_list[0]

    else:
        creator = None

    if creator is None:
        logger.debug(f'No creator found in freetext:  {freetext}')
        creator = next(indexed_structured_creator_generator, None)
    if creator is None:
        logger.debug(
            f'No creator found in indexed_structured:  {indexed_structured}'
        )
    return creator


def _extract_meta_data(row, description_types=None):
    if description_types is None:
        description_types = DESCRIPTION_TYPES.copy()
    freetext = _get_freetext_dict(row)
    descriptive_non_repeating = _get_descriptive_non_repeating_dict(row)
    description = ''
    label_texts = ''
    notes = _check_type(freetext.get('notes'), list)

    for note in notes:
        label = _check_type(note.get('label', ''), str)
        if label.lower().strip() in description_types:
            description += ' ' + _check_type(note.get('content', ''), str)
        elif label.lower().strip() == 'label text':
            label_texts += ' ' + _check_type(note.get('content', ''), str)

    meta_data = {
        'unit_code': descriptive_non_repeating.get('unit_code'),
        'data_source': descriptive_non_repeating.get('data_source')
    }

    if description:
        meta_data.update(description=description.strip())
    if label_texts:
        meta_data.update(label_text=label_texts.strip())

    return {k: v for (k, v) in meta_data.items() if v is not None}


def _extract_source(meta_data, sub_providers=SUB_PROVIDERS):
    unit_code = meta_data.get('unit_code').strip()
    source = next((s for s in sub_providers if unit_code in
                   sub_providers[s]), None)
    if source is None:
        raise Exception(
            f"An unknown unit code value {unit_code} encountered ")
    return source


def _extract_tags(row, tag_types=None):
    if tag_types is None:
        tag_types = TAG_TYPES
    indexed_structured = _get_indexed_structured_dict(row)
    tag_lists_generator = (
        _check_type(indexed_structured.get(key), list) for key in tag_types
    )
    return [tag for tag_list in tag_lists_generator for tag in tag_list if tag]


def _get_descriptive_non_repeating_dict(row):
    logger.debug('Getting descriptive_non_repeating_dict from row')
    return _check_type(
        _get_content_dict(row).get('descriptiveNonRepeating'),
        dict
    )


def _get_indexed_structured_dict(row):
    logger.debug('Getting indexed_structured_dict from row')
    return _check_type(_get_content_dict(row).get('indexedStructured'), dict)


def _get_freetext_dict(row):
    logger.debug('Getting freetext_dict from row')
    return _check_type(_get_content_dict(row).get('freetext'), dict)


def _get_content_dict(row):
    return _check_type(row.get('content'), dict)


def _check_type(unknown_input, required_type):
    """
    This function ensures that the input is of the required type.

    Required Arguments:

    unknown_input:  This can be anything
    required_type:  built-in type name/constructor

    This function will check whether the unknown_input is of type
    required_type. If it is, it returns the unknown_input value
    unchanged. If not, will return the DEFAULT VALUE FOR THE TYPE
    required_type. So, if unknown_input is a float 3.0 and the
    required_type is int, this function will return 0.

    This function will work for required_type in:
    str, int, float, complex, list, tuple, dict, set, bool, and bytes.

    This function will create a relatively high-level log message
    whenever it has to initialize a default value for type
    required_type.
    """
    logger.debug(f"Ensuring {unknown_input} is of type {required_type}")
    if unknown_input is None:
        logger.debug(f"{unknown_input} is of type {type(unknown_input)}.")
        typed_input = required_type()
    elif type(unknown_input) != required_type:
        logger.info(
            f"{unknown_input} is of type {type(unknown_input)}"
            f" rather than {required_type}."
        )
        typed_input = required_type()
    else:
        typed_input = unknown_input
    return typed_input


def _process_image_list(
        image_list,
        foreign_landing_url,
        title,
        creator,
        meta_data,
        tags,
        source,
        license_url=ZERO_URL
):
    total_images = None
    for image_data in image_list:
        if (
                image_data.get('type') == 'Images'
                and image_data.get('usage', {}).get('access') == 'CC0'
        ):
            total_images = image_store.add_item(
                foreign_landing_url=foreign_landing_url,
                image_url=image_data.get('content'),
                thumbnail_url=image_data.get('thumbnail'),
                license_url=license_url,
                foreign_identifier=image_data.get('idsId'),
                title=title,
                creator=creator,
                meta_data=meta_data,
                raw_tags=tags,
                source=source
            )
    return total_images


if __name__ == '__main__':
    main()

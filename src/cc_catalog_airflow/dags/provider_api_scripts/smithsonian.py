"""
Content Provider:  Smithsonian

ETL Process:       Use the API to identify all CC licensed images.

Output:            TSV file containing the images and the respective
                   meta-data.

Notes:             None
"""
import json
import logging
import os

from common.storage import image

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)
DIRECTORY = os.getenv('SI_EXAMPLE_DIRECTORY')
PROVIDER = 'smithsonian'
ZERO_URL = 'https://creativecommons.org/publicdomain/zero/1.0/'

image_store = image.ImageStore(provider=PROVIDER)


def main():
    file_list = _get_file_list()
    logger.info(f'Processing files:\n{file_list}')
    for file_path in file_list:
        with open(file_path) as f:
            response_json = json.loads(f.read())
        search_term = file_path.split('/')[-1].split('.')[0]
        _process_response_json(search_term, response_json)
    total_images = image_store.commit()
    logger.info(f'Total images:  {total_images}')


def _get_file_list(directory=DIRECTORY):
    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f[-5:] == '.json'
    ]


def _process_response_json(search_term, response_json):
    logger.info(f'processing response for {search_term}')
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
            _process_image_list(title, image_list, search_term)


def _process_image_list(title, image_list, search_term, license_url=ZERO_URL):
    for image_data in image_list:
        if image_data.get('type') == 'Images' and image_data.get('usage', {}).get('access') == 'CC0':
            image_store.add_item(
                foreign_landing_url=image_data.get('guid'),
                image_url=image_data.get('content'),
                thumbnail_url=image_data.get('thumbnail'),
                license_url=license_url,
                foreign_identifier=image_data.get('idsId'),
                title=title,
                meta_data=None,
                raw_tags=[search_term],
            )




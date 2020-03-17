import logging
from common.requester import DelayedRequester
from common.storage.image import ImageStore

LIMIT = 1000
DELAY = 5.0
RETRIES = 3
PROVIDER = 'clevelandmuseum'
ENDPOINT = 'http://openaccess-api.clevelandart.org/api/artworks/'

delay_request = DelayedRequester(delay=DELAY)
image_store = ImageStore(provider=PROVIDER)

DEFAULT_QUERY_PARAM = {
    'cc': '1',
    'has_image': '1',
    'limit': LIMIT,
    'skip': 0
}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    logger.info('Begin: Cleveland Museum API requests')
    condition = True
    offset = 0

    while condition:
        query_param = _build_query_param(offset)
        response_json, total_images = _get_response(query_param)
        if response_json is not None and total_images != 0:
            logger.info('Successful response')
            batch = response_json['data']
            image_count = _handle_response(batch)
            logger.info(f'Total images till now {image_count}')
            offset += LIMIT
        else:
            logger.error('No more images to process')
            logger.info('Exiting')
            condition = False
    image_count = image_store.commit()
    logger.info(f'Total number of images received {image_count}')


def _build_query_param(offset):
    query_param = DEFAULT_QUERY_PARAM.copy()
    query_param.update(
        skip=offset
    )
    return query_param


def _get_response(
                query_param,
                endpoint=ENDPOINT,
                retires=RETRIES
                ):
    if retires < 0:
        total_images = 0
        logger.error('Max retries exceeded. Failure')
        raise Exception('retries exceeded')
        return None, total_images

    response = delay_request.get(
                endpoint,
                query_param
                )

    if response.status_code == 200 and response is not None:
        logger.info('Response status 200')
        try:
            response_json = response.json()
            total_images = len(response_json['data'])
            return response_json, total_images
        except Exception as e:
            logger.warning(f'response not captured due to {e}')
            response_json = None

    if response_json is None or response_json.get('error') is not None:
        logger.warning('Bad response_json')
        logger.info('Retrying \n'
                    f'endpoint -- {ENDPOINT} \t'
                    f' with parameters -- {query_param} ')

        _get_response(
            query_param,
            endpoint,
            retries=retries - 1
            )


def _handle_response(
                    batch
                    ):
    for data in batch:
        license_ = data.get('share_license_status', '').lower()
        if license_ != 'cc0':
            logger.error('Wrong license image')
            continue
        license_version = '1.0'

        foreign_id = data.get('id')
        foreign_landing_url = data.get('url', None)
        image_data = data.get('images', None)
        if image_data is not None:
            image_url, key = _get_image_type(image_data)
        else:
            image_url, key = None, None

        if image_url is not None:
            width = image_data[key]['width']
            height = image_data[key]['height']
        else:
            width, height = None, None

        title = data.get('title', None)
        metadata = _get_metadata(data)
        if data.get('creators'):
            creator_name = data.get('creators')[0].get('description', '')
        else:
            creator_name = ''

        total_images = image_store.add_item(
                        foreign_landing_url=foreign_landing_url,
                        image_url=image_url,
                        license_=license_,
                        license_version=license_version,
                        foreign_identifier=foreign_id,
                        width=width,
                        height=height,
                        title=title,
                        creator=creator_name,
                        meta_data=metadata,
                        source=PROVIDER
                        )
    return total_images


def _get_image_type(
                    image_data
                    ):
    if image_data.get('web'):
        key = 'web'
        image_url = image_data.get('web').get('url', None)
    elif image_data.get('print'):
        key = 'print'
        image_url = image_data.get('print').get('url', None)

    elif image_data.get('full'):
        key = 'full'
        image_url = image_data.get('full').get('url', None)
    else:
        image_url = None

    if image_url is None:
        key = None
    return image_url, key


def _get_metadata(data):
    metadata = {}

    metadata['accession_number'] = data.get('accession_number', '')
    metadata['technique'] = data.get('technique', '')
    metadata['date'] = data.get('creation_date', '')
    metadata['credit_line'] = data.get('creditline', '')
    metadata['classification'] = data.get('type', '')
    metadata['tombstone'] = data.get('tombstone', '')
    metadata['culture'] = ','.join(
        [i for i in data.get('culture', []) if i is not None]
    )
    return metadata


if __name__ == '__main__':
    main()

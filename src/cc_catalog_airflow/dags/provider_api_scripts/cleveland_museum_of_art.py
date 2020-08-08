import logging
from common.requester import DelayedRequester
from common.storage.image import ImageStore
from util.loader import provider_details as prov

LIMIT = 1000
DELAY = 5.0
RETRIES = 3
PROVIDER = prov.CLEVELAND_DEFAULT_PROVIDER
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


def _build_query_param(offset=0,
                       default_query_param=DEFAULT_QUERY_PARAM
                       ):
    query_param = default_query_param.copy()
    query_param.update(
        skip=offset
    )
    return query_param


def _get_response(
                query_param,
                endpoint=ENDPOINT,
                retries=RETRIES
                ):
    response_json, total_images = None, 0
    for tries in range(retries):
        response = delay_request.get(
                    endpoint,
                    query_param
                    )
        if response.status_code == 200 and response is not None:
            try:
                response_json = response.json()
                total_images = len(response_json['data'])
            except Exception as e:
                logger.warning(f'response not captured due to {e}')
                response_json = None
            if response_json is not None and total_images is not None:
                break

        logger.info('Retrying \n'
                    f'endpoint -- {endpoint} \t'
                    f' with parameters -- {query_param} ')
    if tries == retries-1 and ((response_json is None) or
                               (total_images is None)):
        logger.warning('No more tries remaining. Returning Nonetypes.')
        return None, 0
    else:
        return response_json, total_images


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

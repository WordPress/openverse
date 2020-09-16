"""
Content Provider:       PhyloPic

ETL Process:            Use the API to identify all CC licensed images.

Output:                 TSV file containing the image,
                        their respective meta-data.

Notes:                  http://phylopic.org/api/
                        No rate limit specified.
"""

import argparse
import logging

import common.requester as requester
import common.storage.image as image

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

DELAY = 5.0
HOST = 'phylopic.org'
ENDPOINT = f'http://{HOST}/api/a'
PROVIDER = 'phylopic'
LIMIT = 5

delayed_requester = requester.DelayedRequester(DELAY)
image_store = image.ImageStore(provider=PROVIDER)


def main(date='all'):
    """
    This script pulls the data for a given date from the PhyloPic
    API, and writes it into a .TSV file to be eventually read
    into our DB.

    Required Arguments:

    date:  Date String in the form YYYY-MM-DD.  This is the date for
           which running the script will pull data.
    """

    param = None
    offset = 0

    logger.info('Begin: PhyloPic API requests')

    if date == 'all':
        logger.info('Processing all images')
        param = {'offset': offset}

        image_count = _get_total_images()
        logger.info(f'Total images: {image_count}')

        while offset <= image_count:
            _add_data_to_buffer(**param)
            offset += LIMIT
            param = {'offset': offset}

    else:
        param = {'date': date}
        logger.info(f'Processing date: {date}')
        _add_data_to_buffer(**param)

    image_store.commit()

    logger.info('Terminated!')


def _add_data_to_buffer(**args):
    endpoint = _create_endpoint_for_IDs(**args)
    IDs = _get_image_IDs(endpoint)

    for id_ in IDs:
        if id_ is not None:
            details = _get_meta_data(id_)
            if details is not None:
                args = _create_args(details, id_)
                image_store.add_item(**args)


def _create_args(details, id_):
    args = {'foreign_landing_url': details[1],
            'image_url': details[2],
            'thumbnail_url': details[3],
            'license_url': details[6],
            'width': details[4],
            'height': details[5],
            'creator': details[7],
            'title': details[8],
            'meta_data': details[9],
            'foreign_identifier': id_
            }
    return args


def _get_total_images():
    # Get the total number of PhyloPic images
    total = 0
    endpoint = 'http://phylopic.org/api/a/image/count'
    result = delayed_requester.get_response_json(
        endpoint,
        retries=2
    )

    if result and result.get('success') is True:
        total = result.get('result', 0)

    return total


def _create_endpoint_for_IDs(**args):
    limit = LIMIT
    offset = 0
    endpoint = ''

    if args.get('date'):
        # Get a list of objects uploaded/updated on a given date.
        date = args['date']
        endpoint = f'http://phylopic.org/api/a/image/list/modified/{date}'

    else:
        # Get all images and limit the results for each request.
        offset = args['offset']
        endpoint = f'http://phylopic.org/api/a/image/list/{offset}/{limit}'
    return endpoint


def _get_image_IDs(_endpoint):
    result = delayed_requester.get_response_json(
        _endpoint,
        retries=2
    )
    image_IDs = []

    if result and result.get('success') is True:
        data = list(result.get('result'))

        if len(data) > 0:
            for i in range(len(data)):
                image_IDs.append(data[i].get('uid'))

    if not image_IDs:
        logger.warning('No content available!')
        return [None]

    return image_IDs


def _get_meta_data(_uuid):
    logger.info(f'Processing UUID: {_uuid}')

    base_url = 'http://phylopic.org'
    img_url = ''
    thumbnail = ''
    width = ''
    height = ''
    foreign_id = ''
    foreign_url = ''
    meta_data = {}
    endpoint = f"http://phylopic.org/api/a/image/{_uuid}?options=credit+" \
        "licenseURL+pngFiles+submitted+submitter+taxa+canonicalName" \
        "+string+firstName+lastName"
    request = delayed_requester.get_response_json(
        endpoint,
        retries=2
    )
    if request and request.get('success') is True:
        result = request['result']
    else:
        return None

    license_url = result.get('licenseURL')

    meta_data['taxa'], title = _get_taxa_details(result)

    foreign_url = f'{base_url}/image/{_uuid}'

    (creator, meta_data['credit_line'],
     meta_data['pub_date']) = _get_creator_details(result)

    img_url, width, height, thumbnail = _get_image_info(result, _uuid)
    foreign_id = img_url
    if img_url is None:
        return None

    return [
            foreign_id, foreign_url, img_url, thumbnail, str(width),
            str(height), license_url, creator, title, meta_data
        ]


def _get_creator_details(result):
    credit_line = None
    pub_date = None
    creator = ''

    first_name = result.get('submitter', {}).get('firstName')
    last_name = result.get('submitter', {}).get('lastName')
    creator = f'{first_name} {last_name}'.strip()

    if result.get('credit'):
        credit_line = result.get('credit').strip()
        pub_date = result.get('submitted').strip()

    return (creator, credit_line, pub_date)


def _get_taxa_details(result):
    taxa = result.get('taxa', [])
    # [0].get('canonicalName', {}).get('string')
    taxa_list = None
    title = ''
    if taxa:
        taxa = list(filter(
            lambda x: x.get('canonicalName') is not None, taxa))
        taxa_list = list(
            map(lambda x: x.get('canonicalName', {}).get('string', ''), taxa))

    if taxa_list:
        title = taxa_list[0]

    return (taxa_list, title)


def _get_image_info(result, _uuid):
    base_url = 'http://phylopic.org'
    img_url = ''
    thumbnail = ''
    width = ''
    height = ''

    image_info = result.get('pngFiles')
    if image_info:
        img = list(filter(lambda x: (
            int(str(x.get('width', '0'))) >= 257), image_info))
        img = sorted(img, key=lambda x: x['width'], reverse=True)
        thb = list(filter(lambda x: str(
            x.get('width', '')) == '256', image_info))

    if len(img) > 0:
        img_url = img[0].get('url')
        img_url = f'{base_url}{img_url}'
        width = img[0].get('width')
        height = img[0].get('height')

    if len(thb) > 0:
        thumbnail_info = thb[0].get('url')
        if thumbnail_info is not None:
            thumbnail = f'{base_url}{thumbnail_info}'

    if img_url == '':
        logging.warning(
            f'Image not detected in url: {base_url}/image/{_uuid}')
        return None, None, None, None
    else:
        return (img_url, width, height, thumbnail)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PhyloPic API Job',
                                     add_help=True)
    parser.add_argument('--date', default='all', help='Identify all images'
                        ' from a particular date (YYYY-MM-DD).')

    date = parser.parse_args().date

    main(date)

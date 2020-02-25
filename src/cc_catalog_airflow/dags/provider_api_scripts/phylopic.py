"""
Content Provider:       PhyloPic

ETL Process:            Use the API to identify all CC licensed images.

Output:                 TSV file containing the image,
                        their respective meta-data.

Notes:                  http://phylopic.org/api/
                        No rate limit specified.
"""


import argparse
from datetime import datetime, timedelta
import logging

import common.requester as requester
import common.storage.image as image


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


DELAY = 1
HOST = 'phylopic.org'
ENDPOINT = f'http://{HOST}/api/a'
PROVIDER = 'phylopic'
LIMIT = 100


delayed_requester = requester.DelayedRequester(DELAY)
image_store = image.ImageStore(provider=PROVIDER)


def main(date):
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
        logger.info('Total images: {}'.format(image_count))

        while offset <= image_count:
            _add_data_to_buffer(**param)
            offset += LIMIT
            param = {'offset': offset}

    else:
        param = {'date': date}
        logger.info('Processing date: {}'.format(date))
        _add_data_to_buffer(**param)

    image_store.commit()

    logger.info('Terminated!')


def _add_data_to_buffer(**args):
    IDs = _get_image_IDs(**args)

    for id in IDs:
        if id is not None:
            details = _get_meta_data(id)

            if details is not None:
                image_store.add_item(foreign_landing_url=details[1],
                                     image_url=details[2],
                                     thumbnail_url=details[3],
                                     license_url=details[6],
                                     width=details[4],
                                     height=details[5],
                                     creator=details[7],
                                     title=details[8],
                                     meta_data=details[9],
                                     )


def _get_total_images():
    # Get the total number of PhyloPic images
    total = 0
    endpoint = 'http://phylopic.org/api/a/image/count'
    result = _get_response_json(endpoint=endpoint, retries=2)

    if result and result.get('success') is True:
        total = result.get('result')

        return total if (total is not None) else 0


def _get_image_IDs(**args):
    limit = LIMIT
    offset = 0
    endpoint = ''

    if args.get('date'):
        # Get a list of recently updated/uploaded objects.
        date = args['date']
        endpoint = 'http://phylopic.org/api/a/image/list/modified/{}'.format(
                  date)

    else:
        # Get all images and limit the results for each request.
        offset = args['offset']
        endpoint = 'http://phylopic.org/api/a/image/list/{}/{}'.format(
                  offset, limit)

    if endpoint == '':
        return [None]

    result = _get_response_json(endpoint=endpoint, retries=2)
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
    logger.info('Processing UUID: {}'.format(_uuid))

    base_url = 'http://phylopic.org'
    img_url = ''
    thumbnail = ''
    width = ''
    height = ''
    foreign_id = ''
    foreign_url = ''
    meta_data = {}
    creator = ''
    title = ''
    endpoint = "http://phylopic.org/api/a/image/{}?options=credit+" \
               "licenseURL+pngFiles+submitted+submitter+taxa+canonicalName" \
               "+string+firstName+lastName".format(_uuid)
    request = _get_response_json(endpoint=endpoint, retries=2)
    if request and request.get('success') is True:
        result = request['result']

    license_url = result.get('licenseURL')

    meta_data['taxa'] = _get_taxa_details(result)

    foreign_id = img_url
    foreign_url = '{}/image/{}'.format(base_url, _uuid)

    (creator, meta_data['credit_line'],
     meta_data['pub_date']) = _get_creator_details(result)

    img_url, width, height, thumbnail = _get_image_info(result, _uuid)
    if img_url is None:
        return None

    return [
            foreign_id, foreign_url, img_url, thumbnail, str(width),
            str(height), license_url, creator, title, meta_data
        ]


def _get_creator_details(result):
    credit_line = None
    pub_date = None

    first_name = result.get('submitter', {}).get('firstName')
    last_name = result.get('submitter', {}).get('lastName')
    creator = '{} {}'.format(first_name, last_name).strip()

    if result.get('credit'):
        credit_line = result.get('credit').strip()
        pub_date = result.get('submitted').strip()

    return (creator, credit_line, pub_date)


def _get_taxa_details(result):
    taxa = result.get('taxa', [])
    # [0].get('canonicalName', {}).get('string')
    taxa_list = None
    if taxa:
        taxa = list(filter(
            lambda x: x.get('canonicalName') is not None, taxa))
        taxa_list = list(
            map(lambda x: x.get('canonicalName', {}).get('string', ''), taxa))

    if taxa_list:
        title = taxa_list[0]

        if len(taxa_list) > 1:
            return taxa_list


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
        img_url = '{}{}'.format(base_url, img_url)
        width = img[0].get('width')
        height = img[0].get('height')

    if len(thb) > 0:
        thumbnail_info = thb[0].get('url')
        if thumbnail_info is not None:
            thumbnail = '{}{}'.format(base_url, thumbnail_info)

    if not img_url:
        logging.warning(
            'Image not detected in url: {}/image/{}'.format(base_url, _uuid))
        return None, None, None, None
    else:
        return (img_url, width, height, thumbnail)


def _get_response_json(
        endpoint=ENDPOINT,
        retries=0,
):
    response_json = None

    if retries < 0:
        logger.error('No retries remaining.  Failure.')
        raise Exception('Retries exceeded')

    response = delayed_requester.get(
        endpoint,
        timeout=60
    )
    if response is not None and response.status_code == 200:
        try:
            response_json = response.json()
        except Exception as e:
            logger.warning(f'Could not get response_json.\n{e}')
            response_json = None

    if response_json is None:
        logger.warning(f'Bad response_json:  {response_json}')
        logger.warning(
            'Retrying:\n_get_response_json(\n'
            f'    {endpoint},\n'
            f'    retries={retries - 1}'
            ')'
        )
        response_json = _get_response_json(
            endpoint=endpoint,
            retries=retries - 1
        )

    return response_json


if __name__ == '__main__':
    date = ''

    parser = argparse.ArgumentParser(description='PhyloPic API Job',
                                     add_help=True)
    parser.add_argument('--mode', choices=['default', 'all'],
                        help='Identify all images from the previous day'
                             ' [default]'
                             ' or process the entire collection [all].')
    parser.add_argument('--date', default=False, help='Identify all images'
                        ' from a particular date (YYYY-MM-DD).')
    args = parser.parse_args()

    if str(args.mode) == 'all':
        date = 'all'

    elif args.date is not False:
        date = str(args.date)

    else:
        date = str(
            datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d'))

    main(date)

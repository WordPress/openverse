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
import json
import time

import common.requester as requester
import common.storage.image as image


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


DELAY = 5
HOST = 'phylopic.org'
ENDPOINT = f'http://{HOST}/api/a'
PROVIDER = 'phylopic'
FILE = 'phylopic_{}.tsv'.format(int(time.time()))
LIMIT = 5


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
            _commit_to_file_all(**param)
            offset += LIMIT
            param = {'offset': offset}

    else:
        param = {'date': date}
        logger.info('Processing date: {}'.format(date))
        _commit_to_file_date(**param)

    logger.info('Terminated!')


def _commit_to_file_all(**args):
    start_time = time.time()
    IDs = _get_image_IDs(**args)

    if IDs:
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
        image_store.commit()
        logger.info('Flushed current buffer to file.')


def _commit_to_file_date(**args):
    start_time = time.time()
    IDs = _get_image_IDs(**args)

    ctr = 1
    while ctr <= len(IDs):
        if IDs[ctr - 1] is not None:
            details = _get_meta_data(IDs[ctr - 1])

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

        if ctr % LIMIT == 0:
            # Add 5 images at a time to file
            image_store.commit()
            logger.info('Flushed current buffer to file.')
        ctr += 1

    image_store.commit()


def _get_total_images():
    # Get the total number of PhyloPic images
    total = 0
    endpoint = 'http://phylopic.org/api/a/image/count'
    request = delayed_requester.get(endpoint, timeout=60)
    result = request.json()

    if result and result.get('success') is True:
        total = result.get('result')

    return total


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
        logger.warning('Unable to parse endpoint: {}, args: {}'.format(
                       endpoint, args))
        return [None]

    response = delayed_requester.get(endpoint, timeout=60)
    result = response.json()
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

    start_time = time.time()
    base_URL = 'http://phylopic.org'
    img_URL = ''
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
    get_request = delayed_requester.get(endpoint, timeout=60)
    request = get_request.json()

    if request and request.get('success') is True:
        result = request['result']

    license_url = result.get('licenseURL')
    img_info = _get_image_info(result)

    if img_info is not None:
        img_URL = img_info[0]
        width = img_info[1]
        height = img_info[2]
        thumbnail = img_info[3]

    else:
        logger.warning('Image not detected in url: {}/image/{}'.format(
                       base_URL, _uuid))
        return None

    foreign_id = img_URL
    foreign_url = '{}/image/{}'.format(base_URL, _uuid)

    first_name = result.get('submitter', {}).get('firstName')
    last_name = result.get('submitter', {}).get('lastName')
    creator = '{} {}'.format(first_name, last_name).strip()

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
            meta_data['taxa'] = taxa_list

    if result.get('credit'):
        meta_data['credit_line'] = result.get('credit').strip()
        meta_data['pub_date'] = result.get('submitted').strip()

    return [
            foreign_id, foreign_url, img_URL,
            thumbnail if thumbnail else '\\N',
            str(width) if width else '\\N',
            str(height) if height else '\\N',
            license_url,
            creator if creator else '\\N',
            title if title else '\\N',
            json.dumps(
                meta_data, ensure_ascii=False) if bool(meta_data) else '\\N',
            '\\N', 'f', 'phylopic', 'phylopic'
        ]


def _get_image_info(result):
    base_URL = 'http://phylopic.org'
    img_URL = ''
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

        if img:
            img_URL = img[0].get('url')
            img_URL = '{}{}'.format(base_URL, img_URL)
            width = img[0].get('width')
            height = img[0].get('height')

            if thb:
                thumbnail_info = thb[0].get('url')
                if thumbnail_info:
                    thumbnail = '{}{}'.format(base_URL, thumbnail_info)

    if not img_URL:
        return None
    else:
        return [img_URL, width, height, thumbnail]


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

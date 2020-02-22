"""
Content Provider:       PhyloPic

ETL Process:            Use the API to identify all CC licensed images.

Output:                 TSV file containing the image, their respective meta-data.

Notes:                  http://phylopic.org/api/
                        No rate limit specified.
"""


import argparse
from datetime import datetime, timedelta
import logging
import json
import time
import lxml.html as html

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
FILE    = 'phylopic_{}.tsv'.format(int(time.time()))
LIMIT   = 5


delayed_requester = requester.DelayedRequester(DELAY)
image_store = image.ImageStore(provider=PROVIDER)


logger = logging.getLogger(__name__)


def getTotalImages():
    #Get the total number of PhyloPic images
    total = 0
    endpoint = 'http://phylopic.org/api/a/image/count'
    request = delayed_requester.get(endpoint)
    result = request.json()
    #result = json.loads(result_json)

    if result and result.get('success') == True:
        total = result.get('result')

    return total


def getImageIDs(**args):
    limit       = LIMIT
    offset      = 0
    endpoint    = ''

    if args.get('date'):
        # Get a list of recently updated/uploaded objects.
        date     = args['date']
        endpoint = 'http://phylopic.org/api/a/image/list/modified/{}'.format(date)

    else:
        # Get all images and limit the results for each request.
        offset   = args['offset']
        endpoint = 'http://phylopic.org/api/a/image/list/{}/{}'.format(offset, limit)

    if endpoint == '':
        logger.warning('Unable to parse endpoint: {}, args: {}'.format(endpoint, args))
        return [None]

    response = delayed_requester.get(endpoint)
    result = response.json()
    imageIDs = []

    if result and result.get('success') == True:
        data = list(result.get('result'))

        if len(data) > 0:
            for i in range(len(data)):
                imageIDs.append(data[i].get('uid'))

    if not imageIDs:
        logger.warning('Content not available!')
        return [None]

    return imageIDs


def getMetaData(_uuid):
    logger.info('Processing UUID: {}'.format(_uuid))

    startTime   = time.time()
    baseURL     = 'http://phylopic.org'
    license     = ''
    version     = ''
    imgURL      = ''
    thumbnail   = ''
    width       = ''
    height      = ''
    foreignID   = ''
    foreignURL  = ''
    metaData    = {}
    creator     = ''
    title       = ''

    endpoint    = 'http://phylopic.org/api/a/image/{}?options=credit+licenseURL+pngFiles+submitted+submitter+taxa+canonicalName+string+firstName+lastName'.format(_uuid)
    get_request = delayed_requester.get(endpoint)
    request     = get_request.json()

    if request and request.get('success') == True:
        result  = request['result']

    license_url = result.get('licenseURL')

    imgInfo = result.get('pngFiles')
    if imgInfo:
        img = list(filter(lambda x: (int(str(x.get('width', '0'))) >= 257), imgInfo))
        img = sorted(img, key = lambda x: x['width'],reverse=True)
        thb = list(filter(lambda x: str(x.get('width', '')) == '256', imgInfo))


        if img:
            imgURL  = img[0].get('url')
            imgURL  = '{}{}'.format(baseURL, imgURL)
            width   = img[0].get('width')
            height  = img[0].get('height')

            if thb:
                thumbInfo = thb[0].get('url')
                if thumbInfo:
                    thumbnail = '{}{}'.format(baseURL, thumbInfo)

    if not imgURL:
        logger.warning('Image not detected in url: {}/image/{}'.format(baseURL, _uuid))
        return None

    foreignID   = imgURL
    foreignURL  = '{}/image/{}'.format(baseURL, _uuid)

    firstName   = result.get('submitter', {}).get('firstName')
    lastName    = result.get('submitter', {}).get('lastName')
    creator     = '{} {}'.format(firstName, lastName).strip()

    taxa        = result.get('taxa', [])#[0].get('canonicalName', {}).get('string')
    taxaList    = None
    if taxa:
        taxa     = list(filter(lambda x: x.get('canonicalName') is not None, taxa))
        taxaList = list(map(lambda x: x.get('canonicalName', {}).get('string', ''), taxa))


    if taxaList:
        title = taxaList[0]

        if len(taxaList) > 1:
            metaData['taxa'] = taxaList


    if result.get('credit'):
        metaData['credit_line'] = result.get('credit').strip()
        metaData['pub_date']    = result.get('submitted').strip()


    return [
            foreignID, foreignURL, imgURL,
            thumbnail if thumbnail else '\\N',
            str(width) if width else '\\N',
            str(height) if height else '\\N',
            license_url,
            creator if creator else '\\N',
            title if title else '\\N',
            json.dumps(metaData, ensure_ascii=False) if bool(metaData) else '\\N',
            '\\N', 'f', 'phylopic', 'phylopic'
        ]


def commit_to_file_all(**args):
    startTime = time.time()
    IDs       = getImageIDs(**args)

    if IDs:
        for id in IDs:
            if id is not None:
                details = getMetaData(id)

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

def commit_to_file_date(**args):
    startTime = time.time()
    IDs       = getImageIDs(**args)
    rounds    = len(IDs)//5 if len(IDs)%5 == 0 else len(IDs)//5 + 1

    ctr = 1
    while ctr <= len(IDs):
        if IDs[ctr-1] is not None:
            details = getMetaData(IDs[ctr-1])

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


def main():
    logger.info('Begin: PhyloPic API requests')
    param   = None
    offset  = 0


    parser  = argparse.ArgumentParser(description='PhyloPic API Job', add_help=True)
    parser.add_argument('--mode', choices=['default', 'all'],
            help='Identify all images from the previous day [default]'
                 ' or process the entire collection [all].')
    parser.add_argument('--date', default=False, help='Identify all images from'
        ' a particular date (YYYY-MM-DD).')
    args = parser.parse_args()

    if str(args.mode) == 'all':
        logger.info('Processing all images')
        param = {'offset': offset}

        imgCtr  = getTotalImages()
        logger.info('Total images: {}'.format(imgCtr))

        while offset <= imgCtr:
            commit_to_file_all(**param)
            offset += LIMIT
            param   = {'offset': offset}

    elif args.date is not False:
        param = {'date': args.date}
        logger.info('Processing date: {}'.format(param['date']))
        commit_to_file_date(**param)

    else:
        param = {'date': datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')}
        logger.info('Processing date: {}'.format(param['date']))
        commit_to_file_date(**param)


    logger.info('Terminated!')


if __name__ == '__main__':
    main()

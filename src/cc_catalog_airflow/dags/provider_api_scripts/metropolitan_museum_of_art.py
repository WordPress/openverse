"""
Content Provider:       Metropolitan Museum of Art

ETL Process:            Use the API to identify all CC0 artworks.

Output:                 TSV file containing the image, their respective meta-data.

Notes:                  https://metmuseum.github.io/
                        No rate limit specified.
"""

from modules.etlMods import *
import argparse
import os
import ImageStore from common.storage.image
import DelayedRequester from common.requester
import logging
from datetime import datetime, timedelta, timezone


DELAY   = 1.0 #time delay (in seconds)
FILE    = 'metmuseum_{}.tsv'.format(int(time.time()))

logging.basicConfig(format='%(asctime)s: [%(levelname)s - Met Museum API] =======> %(message)s', level=logging.INFO)


def getObjectIDs(_date=None):
    #Get a list of recently updated/uploaded objects. if no date is specified return all objects.

    objectDate = ''

    if _date:
        objectDate = '?metadataDate={}'.format(_date)

    endpoint = 'https://collectionapi.metmuseum.org/public/collection/v1/objects{}'.format(objectDate)
    result   = requestContent(endpoint)

    if result:
        totalObjects = result['total']
        objectIDs    = result['objectIDs']

    else:
        logging.warning('Content not available!')

        return None

    return [totalObjects, objectIDs]


def getMetaData(_objectID):
    logging.info('Processing object: {}'.format(_objectID))

    license     = 'CC0'
    version     = '1.0'
    imgInfo     = ''
    imgURL      = ''
    width       = ''
    height      = ''
    foreignID   = ''
    foreignURL  = ''
    title       = ''
    creator     = ''
    metaData    = {}
    extracted   = []
    startTime   = time.time()
    idx         = 0

    endpoint    = 'https://collectionapi.metmuseum.org/public/collection/v1/objects/{}'.format(_objectID)
    objectData  = requestContent(endpoint)

    if objectData is None:
        logging.error('Unable to process object ID: {}'.format(_objectID))
        return None

    message  = objectData.get('message')
    if message:
        logging.warning('{}: {}'.format(message, _objectID))
        return None


    #validate CC0 license
    isCC0 = objectData.get('isPublicDomain')
    if (isCC0 is None) or (isCC0 == False):
        logging.warning('CC0 license not detected!')
        return None

    #get the landing page
    foreignURL  = objectData.get('objectURL', None)
    if foreignURL is None:
        logging.warning('Landing page not detected!')
        return None


    #get the title
    title   = objectData.get('title', '')
    title   = sanitizeString(title)

    #get creator info
    creator = objectData.get('artistDisplayName', '')
    creator = sanitizeString(creator)

    #get the foreign identifier
    foreignID = _objectID

    #accessionNumber
    metaData['accession_number'] = sanitizeString(objectData.get('accessionNumber', ''))
    metaData['classification']   = sanitizeString(objectData.get('classification', ''))
    metaData['culture']          = sanitizeString(objectData.get('culture', ''))
    metaData['date']             = sanitizeString(objectData.get('objectDate', ''))
    metaData['medium']           = sanitizeString(objectData.get('medium', ''))
    metaData['credit_line']      = sanitizeString(objectData.get('creditLine', ''))
    #metaData['geography']        = objectData.get('geographyType', '')


    #get the image url and thumbnail
    imgInfo     = objectData.get('primaryImage')
    if imgInfo is None:
        logging.warning('Image not detected in url {}'.format(foreignURL))
        return None

    imgURL = imgInfo

    thumbnail = ''
    if '/original/' in imgURL:
        thumbnail = imgURL.replace('/original/', '/web-large/')


    otherImages = objectData.get('additionalImages')
    if len(otherImages) > 0:
        idx = 1
        metaData['set'] = foreignURL


    extracted.append([
            str(foreignID), foreignURL, imgURL, thumbnail,
            '\\N', '\\N', '\\N', license, str(version), creator, '\\N',
            title, json.dumps(metaData, ensure_ascii=False), '\\N', 'f', 'met', 'met'
        ])


    #extract the additional images
    for img in otherImages:
        foreignID   = '{}-{}'.format(_objectID, idx)
        imgURL      = img
        thumbnail   = ''

        if imgURL:
            if '/original/' in imgURL:
                thumbnail = imgURL.replace('/original/', '/web-large/')

            extracted.append([
                str(foreignID), foreignURL, imgURL, thumbnail,
                '\\N', '\\N', '\\N', license, str(version), creator, '\\N',
                title, json.dumps(metaData, ensure_ascii=False), '\\N', 'f', 'met', 'met'
            ])

        idx += 1


    writeToFile(extracted, FILE)
    delayProcessing(startTime, DELAY)

    return len(extracted)


def execJob(_param=None):

    result = getObjectIDs(_param)
    if result:
        logging.info('Total objects found: {}'.format(result[0]))

        extracted = map(lambda obj: getMetaData(obj), result[1])
        logging.info('Total CC0 images: {}'.format(sum(filter(None, extracted))))


def main():
    logging.info('Begin: Met Museum API requests')
    param   = None
    mode    = 'date: '

    parser  = argparse.ArgumentParser(description='Met Museum API Job', add_help=True)
    parser.add_argument('--mode', choices=['default', 'all'],
            help='Identify all artworks from the previous day [default] or process the entire collection [all].')
    parser.add_argument('--date', type=lambda dt: datetime.strptime(dt, '%Y-%m-%d'),
            help='Identify artworks published on a given date (format: YYYY-MM-DD).')

    args = parser.parse_args()
    if args.date:
        param = (args.date.strftime('%Y-%m-%d'))

    elif args.mode:

        if str(args.mode) == 'default':
            param = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
        else:
            mode  = 'all CC0 artworks'
            param = None

    mode += param if param is not None else ''
    logging.info('Processing {}'.format(mode))

    execJob(param)

    logging.info('Terminated!')


if __name__ == '__main__':
    main()

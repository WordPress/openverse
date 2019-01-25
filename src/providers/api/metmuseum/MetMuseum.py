"""
Content Provider:       Metropolitan Museum of Art

ETL Process:            Use the API to identify all CC0 artworks.

Output:                 TSV file containing the image, their respective meta-data.

Notes:                  https://metmuseum.github.io/
                        No rate limit specified.
"""

import logging
import json
import requests
import time
import sys
import os
import random
reload(sys)
sys.setdefaultencoding('utf8')

DELAY       = 3.0 #seconds
FILE        = 'metmuseum_{}.tsv'.format(int(time.time()))

logging.basicConfig(format='%(asctime)s: [%(levelname)s - Met Museum API] =======> %(message)s', level=logging.INFO)


def delayProcessing(_startTime):
    global DELAY

    waitTime = min(DELAY, abs(DELAY - (float(time.time()) - float(_startTime)))) #time delay between requests.
    waitTime = round(waitTime, 3)

    logging.info('Time delay: {} seconds'.format(waitTime))
    time.sleep(waitTime)


def requestContent(_url):
    logging.info('Processing request: {}'.format(_url))

    try:
        response = requests.get(_url)

        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            logging.warning('Unable to request URL: {}. Status code: {}'.format(url, response.status_code))
            return None

    except Exception as e:
        logging.error('There was an error with the request.')
        logging.info('{}: {}'.format(type(e).__name__, e))
        return None


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


def writeToFile(_data):
    global FILE

    if len(_data) < 1:
        return None

    logging.info('Writing to file')

    with open(FILE, 'a') as fh:
        for line in _data:
            if line:
                fh.write('\t'.join(line) + '\n')


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
    title   = objectData.get('title', '').strip().encode('unicode-escape')

    #get creator info
    creator = objectData.get('artistDisplayName', '').strip().encode('unicode-escape')


    #get the foreign identifier
    foreignID = _objectID

    #accessionNumber
    metaData['accession_number'] = objectData.get('accessionNumber', '')
    metaData['classification']   = objectData.get('classification', '')
    metaData['culture']          = objectData.get('culture', '')
    metaData['date']             = objectData.get('objectDate', '')
    metaData['medium']           = objectData.get('medium', '')
    metaData['credit_line']      = objectData.get('creditLine', '')
    #metaData['geography']        = objectData.get('geographyType', '')


    #get the image url and thumbnail
    imgInfo     = objectData.get('primaryImage')
    if imgInfo is None:
        logging.warning('Image not detected in url {}'.format(foreignURL))
        return None

    imgURL = imgInfo

    thumbnail = ''
    if '/original/' in imgURL:
        thumbnail = imgURL.replace('/original/', '/web-additional/')


    otherImages = objectData.get('additionalImages')
    if len(otherImages) > 0:
        idx = 1
        metaData['set'] = foreignURL


    extracted.append([
            str(foreignID), foreignURL, imgURL, thumbnail,
            '', '', '', license, str(version), creator, '',
            title, json.dumps(metaData), '', 'f', 'met', 'met'
        ])


    #extract the additional images
    for img in otherImages:
        foreignID   = '{}-{}'.format(_objectID, idx)
        imgURL      = img
        thumbnail   = ''

        if imgURL:
            if '/original/' in imgURL:
                thumbnail = imgURL.replace('/original/', '/web-additional/')

            extracted.append([
                str(foreignID), foreignURL, imgURL, thumbnail,
                '', '', '', license, str(version), creator, '',
                title, json.dumps(metaData), '', 'f', 'met', 'met'
            ])

        idx += 1

    delayProcessing(startTime)
    writeToFile(extracted)

    return len(extracted)


def main():
    logging.info('Begin: Met API requests')

    result = getObjectIDs()
    if result:
        logging.info('Total objects found: {}'.format(result[0]))

        extracted = map(lambda obj: getMetaData(obj), result[1])
        logging.info('Total images: {}'.format(sum(filter(None, extracted))))


    logging.info('Terminated!')


if __name__ == '__main__':
    main()

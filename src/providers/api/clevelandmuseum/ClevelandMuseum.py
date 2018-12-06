"""
Content Provider:       Cleveland Museum

ETL Process:            Use the API to identify all CC0 artworks.

Output:                 TSV file containing the image, their respective meta-data.

Notes:                  http://openaccess-api.clevelandart.org/
                        No limit specified.
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

LIMIT       = 1000
LICENSE     = 'cc0'
DELAY       = 5.0 #seconds
FILE        = 'cc0.tsv'

logging.basicConfig(format='%(asctime)s: [%(levelname)s - Cleveland Museum API] =======> %(message)s', level=logging.INFO)

def delayProcessing(_startTime):
    global DELAY

    waitTime = max(1.0, DELAY - (float(time.time()) - float(_startTime))) #delay between requests.
    waitTime = round(waitTime, 3)

    logging.info('Time delay: {} seconds'.format(waitTime))
    time.sleep(waitTime)


def writeToFile(_data):
    global FILE

    if len(_data) < 1:
        return None

    logging.info('Writing to file')

    with open(FILE, 'a') as fh:
        for line in _data:
            if line:
                fh.write('\t'.join(line) + '\n')


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


def getMetaData(_data):
    license     = 'cc0'
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

    #verify the license
    if not ('share_license_status' in _data) and (_data['share_license_status'] == 'CC0'):
        logging.warning('CC0 license not detected!')
        return None

    #get the landing page
    foreignURL  = _data.get('url', None)

    #get the image url and dimension
    imgInfo     = _data.get('images')
    if imgInfo and imgInfo.get('web'):

        imgURL  = imgInfo.get('web', {}).get('url', None)

        if imgURL:
            width   = imgInfo['web']['width']
            height  = imgInfo['web']['height']

    if (not imgInfo) or (not imgURL):
        logging.warning('Image not detected in url {}'.format(foreignURL))
        return None

    #provider identifier for the artwork
    foreignID   = _data.get('id', imgURL)

    #title
    title       = _data.get('title', '').strip().encode('unicode-escape')

    if not foreignURL:
        logging.warning('Landing page not detected')
        return None

    #get creator info
    creatorInfo = _data.get('creators', {})
    creatorName = None

    if creatorInfo:
        creatorName = creatorInfo[0].get('description', '')

    if creatorName:
        creator = creatorName.strip().encode('unicode-escape')


    #get additional meta data
    metaData['accession_number'] = _data.get('accession_number', '')
    metaData['technique']        = _data.get('technique', '')
    metaData['date']             = _data.get('creation_date', '')
    metaData['credit_line']      = _data.get('creditline', '')
    metaData['medium']           = _data.get('technique', '')
    metaData['classification']   = _data.get('type', '')
    metaData['culture']          = _data.get('culture', '')
    metaData['tombstone']        = _data.get('tombstone', '')

    #No description of artwork. The digital_description and wall_description are null.

    return [
            str(foreignID),
            foreignURL,
            imgURL,
            '',
            str(int(float(width))) if width else '',
            str(int(float(height))) if height else '',
            '',
            license,
            str(version),
            creator,
            '',
            title,
            json.dumps(metaData),
            '',
            'f',
            'clevelandmuseum',
            'clevelandmuseum'
        ]



def main():
    global LIMIT

    offset  = 0
    isValid = True

    while isValid:
        startTime   = time.time()
        url         = 'http://openaccess-api.clevelandart.org/api/artworks/?cc0=1&limit={0}&skip={1}'.format(LIMIT, offset)
        batch       = requestContent(url)

        if batch and ('data' in batch):
            extracted = batch['data']

            if extracted:
                result = map(lambda data: getMetaData(data), extracted)
                writeToFile(result)
                offset += LIMIT

                delayProcessing(startTime)

            else:
                isValid = False
                break


    logging.info('Terminated!')


if __name__ == '__main__':
    main()

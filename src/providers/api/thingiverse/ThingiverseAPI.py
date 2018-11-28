"""
Content Provider:       Thingiverse

ETL Process:            Use the API to identify all CC0 3D Models.

Output:                 TSV file containing the 3D models, their respective images and meta-data.

Notes:                  https://www.thingiverse.com/developers/getting-started
                        All API requests require authentication.
                        Rate limiting is 300 per 5 minute window.
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

MAX_THINGS  = 100
LICENSE     = 'pd0'
TOKEN       = os.environ['THINGIVERSE_TOKEN']
DELAY       = 10.0 #seconds
FILE        = 'pd0.tsv'


logging.basicConfig(format='%(asctime)s: [%(levelname)s - Thingiverse API] =======> %(message)s', level=logging.INFO)

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
        if _data:
            fh.write('\t'.join(_data) + '\n')


def requestContent(_url):

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


def requestBatchThings(_page):
    global TOKEN, MAX_THINGS, LICENSE

    url = 'https://api.thingiverse.com/search/{3}?access_token={1}&per_page={2}&page={0}'.format(_page, TOKEN, MAX_THINGS, LICENSE)
    logging.info('Processing URL: {}'.format(url))

    result = requestContent(url)
    if result:
        return map(lambda x: x['id'], result)

    return None


def getMetaData(_thing):
    global TOKEN

    url         = 'https://api.thingiverse.com/things/{0}?access_token={1}'.format(_thing, TOKEN)
    licenseText = 'Creative Commons - Public Domain Dedication'
    license     = None
    version     = None
    creator     = None
    creatorURL  = None
    title       = None
    foreignURL  = None

    logging.info('Processing thing: {}'.format(_thing))

    result = requestContent(url)
    if result:
        startTime = time.time()

        #validate CC0 license
        if not (('license' in result) and (licenseText.lower() in result['license'].lower())):
            logging.warning('License not detected => https://www.thingiverse.com/thing:{}'.format(_thing))
            return None
        else:
            license = 'cc0'
            version = '1.0'


        #get meta data

        #description of the work
        if 'description' in result:
            description = result['description'].strip()

        #title for the 3D model
        if 'name' in result:
            title = result['name'].strip().encode('unicode-escape')


        #the landing page
        if 'public_url' in result:
            foreignURL = result['public_url'].strip()
        else:
            foreignURL = 'https://www.thingiverse.com/thing:{}'.format(_thing)


        #creator of the 3D model
        if 'creator' in result:
            if ('first_name' in result['creator']) and ('last_name' in result['creator']):
                creator = '{} {}'.format(result['creator']['first_name'].strip(), result['creator']['last_name'].strip())

            if (creator.strip() == '') and ('name' in result['creator']):
                creator = result['creator']['name'].strip()

            if creator:
                creator = creator.encode('unicode-escape')

            if 'public_url' in result['creator']:
                creatorURL = result['creator']['public_url'].strip()


        #get the tags
        delayProcessing(startTime)
        logging.info('Requesting tags for thing: {}'.format(_thing))
        startTime = time.time()
        tags      = requestContent(url.replace(_thing, '{0}/tags'.format(_thing)))
        tagsList  = None

        if tags:
            tagsList = map(lambda tag: {'name': str(tag['name'].strip()), 'provider': 'thingiverse'} , tags)


        #get 3D models and their respective images
        delayProcessing(startTime)
        logging.info('Requesting images for thing: {}'.format(_thing))

        imageList = requestContent(url.replace(_thing, '{}/files'.format(_thing)))
        for img in imageList:
            metaData    = {}
            thumbnail   = None
            imageURL    = None
            foreignID   = None

            metaData['description'] = description

            if ('default_image' in img) and img['default_image']:
                if 'url' not in img['default_image']:
                    logging.warning('3D Model Not Detected!')
                    continue

                metaData['3d_model'] = img['default_image']['url']
                foreignID            = str(img['default_image']['id'])
                images               = img['default_image']['sizes']

                for imgSize in images:

                    if str(imgSize['type']).strip().lower() == 'display':

                        if str(imgSize['size']).lower() == 'medium':
                            thumbnail = imgSize['url'].strip()

                        if str(imgSize['size']).lower() == 'large':
                            imageURL  = imgSize['url'].strip()


                        elif imageURL is None:
                            imageURL  = thumbnail

                    else:
                        continue

                if imageURL is None:
                    logging.warning('Image Not Detected!')
                    continue

                writeToFile([
                    imageURL if not foreignID else foreignID,
                    foreignURL,
                    imageURL,
                    thumbnail,
                    '',
                    '',
                    '',
                    license,
                    str(version),
                    creator,
                    creatorURL,
                    title,
                    json.dumps(metaData),
                    json.dumps(tagsList),
                    'f',
                    'thingiverse',
                    'thingiverse'])


def main():
    page        = 1
    totalPages  = 100

    for i in range(totalPages): #temporary control flow

        batch = requestBatchThings(page)

        if batch:
            map(lambda thing: getMetaData(str(thing)), batch)

        page += 1

    logging.info('Terminated!')


if __name__ == '__main__':
    main()

"""
Content Provider:       New York Public Library

ETL Process:            Use the API to identify all CC0 images.

Output:                 TSV file containing the images and the respective meta-data.

Notes:                  http://api.repo.nypl.org/
                        Rate limit: 10,000 requests per day.
"""

from modules.etlMods import *

logging.basicConfig(format='%(asctime)s: [%(levelname)s - NYPL API] =======> %(message)s', level=logging.INFO)


DELAY           = 3.0 #time delay (in seconds)
FILE            = 'nypl_{}.tsv'.format(int(time.time()))
SIZE            = 500
TOKEN           = os.environ['NYPL_TOKEN']
HEADER          = {'Authorization': 'Token token={}'.format(TOKEN)}
TOT_REQ         = 0
INIT_TIME       = time.time() #start time
BASE_ENDPOINT   = 'http://api.repo.nypl.org/api/v1/'


def getRootIDs():
    #NYPL API - Method 9: Return Top-Level UUIDS.
    #Methods returns uuids for top-level collection records and item records without parents
    logging.info('Requesting top-level UUIDs (collections and items)')

    uuidList, total, pages = getUUIDs('items/roots')
    logging.info('No. top-level UUIDS: {}'.format(total))

    delayProcessing(time.time(), DELAY) #throttle requests

    return uuidList



def getUUIDs(_method, _type=None, _limit=None, _offset=None):
    endpoint    = '{}{}'.format(BASE_ENDPOINT, _method)
    request     = requestContent(endpoint, HEADER)


    if not request:
        return None

    nypl        = request.get('nyplAPI')
    reqParams   = nypl.get('request')

    logging.info('API Request details: {}'.format(reqParams))

    response    = nypl.get('response')
    headers     = response.get('headers')
    if headers.get('code', '') == '200':
        if _type:
            data    = response.get(_type)
        else:
            uuids   = response.get('uuids', {})
            data    = uuids.get('uuid')

        total   = response.get('numResults')
        pages   = reqParams.get('totalPages')

        return [data, total, pages]


    return None


def getCaptures(_uuid):
    #NYPL API - Method 4: Return Captures for a UUID
    #Input - a UUID for an item, a container, or a collection
    #Method returns uuid (capture), imageID, itemLink, title, etc
    page        = 1
    limit       = 500
    method      = 'items/{}?page={}&per_page={}'.format(_uuid, page, limit)

    logging.info('Requesting captures for UUID: {}'.format(_uuid))

    #loop and increment the page numpers
    captures, total, pages = getUUIDs(method, 'capture')
    delayProcessing(time.time(), DELAY) #throttle requests

    if pages is None:
        logging.warning('Captures not found!')
        return None

    logging.info('Total Captures {}'.format(total))

    while page <= int(pages):
        logging.info('Processing page {} of {}'.format(page, pages))

        #filter captures without images
        imgDetails  = list(filter(lambda item: (item.get('imageLinks') is not None), captures))

        #filter captures without creativecommons.org in the rights statement and get the UUID
        ccContent   = list(map(lambda itemID: itemID.get('uuid'), filter(lambda item: ('creativecommons.org' in item.get('rightsStatementURI')), imgDetails)))

        #get the capture details
        if ccContent:
            extracted = list(map(lambda uuid: getMetaData(uuid), ccContent)) #('510d47df-e519-a3d9-e040-e00a18064a99')

            #write to file
            if extracted:
                writeToFile(extracted, FILE)


        page += 1
        delayProcessing(time.time(), DELAY) #throttle requests

        #get next batch of captures
        method      = 'items/{}?page={}&per_page={}'.format(_uuid, page, limit)

        logging.info('Requesting captures for UUID: {}'.format(_uuid))

        #loop and increment the page numpers
        captures, total, pages = getUUIDs(method, 'capture')


def getMetaData(_uuid):
    #NYPL API - Method 6: Return Capture Details
    #Input: capture ID
    #Method returns uuid, imageLinks, typeOfResource, imageID, etc

    delayProcessing(time.time(), DELAY) #throttle requests


    endpoint = '{}items/item_details/{}'.format(BASE_ENDPOINT, _uuid)

    logging.info('Requesting capture details for UUID: {}'.format(_uuid))

    request     = requestContent(endpoint, HEADER)
    nyplData    = request.get('nyplAPI')

    response    = nyplData.get('response')
    headers     = response.get('headers')

    if headers.get('code', {}).get('$') == '200':
        mods = response.get('mods')
        license = ''
        version = ''
        title   = ''
        creator = ''


        title = mods.get('titleInfo', {}).get('title', {}).get('$')
        title = sanitizeString(title)

        creator = mods.get('name', {}).get('namePart', {}).get('$')
        creator = sanitizeString(creator)

        #originInfo = mods.get('originInfo', {}).get('dateIssued', {}).get('$')

        captureInfo = response.get('sibling_captures', {}).get('capture', [])
        if type(captureInfo) is not list:
            captureInfo = [captureInfo]

        #get all images (and alternative images)
        #exclude images that do not match the title (this is not mandatory but it is an extra validation step)
        captureInfo = list(filter(lambda item: (sanitizeString(item.get('title', {}).get('$')) == title), captureInfo))

        for item in captureInfo:
            foreignID   = ''
            foreignURL  = ''
            imgURL      = ''
            width       = ''
            height      = ''
            thumbnail   = ''

            #rightsStatementURI - get only CC0 images
            rightsInfo = item.get('rightsStatementURI', {}).get('$')
            if rightsInfo.endswith('creativecommons.org/publicdomain/zero/1.0/'):
                license = 'cc0'
                version = 1.0
            else:
                logging.warning('CC0 license not detected in UUID: {}!'.format(_uuid))
                continue


            #get image information
            imageLinks = item.get('imageLinks', {}).get('imageLink')
            if imageLinks:
                imgInfo     = list(map(lambda imgInfo: imgInfo.get('$'), filter(lambda img: ('"full-size"' in img.get('description', {})), imageLinks)))
                imgURL      = imgInfo[0].replace('&download=1', '')

                thmbInfo    = list(map(lambda imgInfo: imgInfo.get('$'), filter(lambda img: ('300 pixels' in img.get('description', {})), imageLinks)))
                thumbnail   = thmbInfo[0].replace('&download=1', '')

            if imgURL == '':
                logging.warning('Image not detected in UUID: {}!'.format(_uuid))
                continue


            #print(item.get('typeOfResource'))

            foreignURL = item.get('itemLink', {}).get('$')
            foreignID  = item.get('imageID', {}).get('$')


            yield [
                str(foreignID), foreignURL, imgURL, thumbnail,
                '\\N', '\\N', '\\N', license, str(version), creator, '\\N',
                title, '\\N', '\\N', 'f', 'nypl', 'nypl'
            ]



def getRecent():

    pass




rootID = getRootIDs()

#sample = rootID[0:10]
#print('Sample UUIDs: {}'.format(sample))
list(map(lambda uuid: getCaptures(uuid), rootID))


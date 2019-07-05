"""
Content Provider:       RawPixel

ETL Process:            Use the API to identify all CC0 images.

Output:                 TSV file containing the image, their respective meta-data.

Notes:                  https://api.rawpixel.com/api/v1/search?freecc0=1&html=0
                        No rate limit specified.
"""

from modules.etlMods import *
from urllib.parse import parse_qs


DELAY   = 1.0 #time delay (in seconds)
FILE    = 'rawpixel_{}.tsv'.format(int(time.time()))

logging.basicConfig(format='%(asctime)s: [%(levelname)s - RawPixel API] =======> %(message)s', level=logging.INFO)


def getImageList(_page=1):
    endpoint    = 'https://api.rawpixel.com/api/v1/search?freecc0=1&html=0&page={}'.format(_page)
    request     = requestContent(endpoint)

    if request.get('results'):
        return [request.get('total'), request.get('results')]

    else:
        return [None, None]



def getMetaData(_image):
    startTime   = time.time()

    #verify the license and extract the metadata
    foreignID   = ''
    foreignURL  = ''
    imgURL      = ''
    width       = ''
    height      = ''
    thumbnail   = ''
    tags        = ''
    title       = ''
    owner       = ''
    license     = 'cc0'
    version     = '1.0'
    tags        = {}

    if _image.get('freecc0'):
        #get the image identifier
        foreignID = _image.get('id', '')

        #get the landing page
        foreignURL = _image.get('url')

        if not foreignURL:
            logging.warning('Landing page not detected for image ID: {}'.format(foreignID))
            return None

        imgURL = _image.get('image_opengraph')
        if imgURL:
            #extract the dimensions from the query params because the dimensions in the metadata are at times inconsistent with the rescaled images
            queryParams = urlparse(imgURL)
            width       = parse_qs(queryParams.query).get('w', [])[0] #width
            height      = parse_qs(queryParams.query).get('h', [])[0] #height

            thumbnail   = _image.get('image_400', '')
        else:
            logging.warning('Image not detected in URL: {}'.format(foreignURL))
            return None

        title = sanitizeString(_image.get('image_title', ''))

        owner = sanitizeString(_image.get('artists', ''))
        owner = owner.replace('(Source)', '').strip()

        keywords        = _image.get('keywords_raw')
        if keywords:
            keywordList = keywords.split(',')
            keywordList = list(filter(lambda word: word.strip() not in ['cc0', 'creative commons', 'creative commons 0'], keywordList))

            tags        = [{'name': sanitizeString(tag), 'provider': 'rawpixel'} for tag in keywordList]

    delayProcessing(startTime, DELAY)
    return [
            str(foreignID), foreignURL, imgURL,
            thumbnail if thumbnail else '\\N',
            str(width) if width else '\\N',
            str(height) if height else '\\N', '\\N',
            license, str(version),
            owner if owner else '\\N', '\\N',
            title if title else '\\N',
            '\\N',
            json.dumps(tags, ensure_ascii=False) if bool(tags) else '\\N',
            'f', 'rawpixel', 'rawpixel'
        ]


def main():
    page    = 1
    imgCtr  = 0
    isValid = True

    logging.info('Begin: RawPixel API requests')


    total, result = getImageList(page)

    while (imgCtr < total) and isValid:
        logging.info('Processing page: {}'.format(page))

        startTime = time.time()
        extracted = list(map(lambda img: getMetaData(img), result))
        extracted = list(filter(None, extracted))

        imgCtr   += len(extracted)

        #write to file
        if extracted:
            writeToFile(extracted, FILE)

        page += 1
        delayProcessing(startTime, DELAY) #throttle requests
        total, result = getImageList(page)

        if not result:
            isValid = False

        if not total:
            total = 0
            isValid = False

    logging.info('Total images: {}'.format(imgCtr))
    logging.info('Terminated!')


if __name__ == '__main__':
    main()

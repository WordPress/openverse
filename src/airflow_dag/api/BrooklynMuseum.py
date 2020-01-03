"""
Content Provider:       Brooklyn Museum

ETL Process:            Use the API to identify all CC licensed artworks.

Output:                 TSV file containing the images and respective meta-data.

Notes:                  https://www.brooklynmuseum.org/opencollection/api
                        3000 calls per day (per API Key)
"""

from modules.etlMods import *


DELAY       = 3.0 #time delay (in seconds)
FILE        = 'brooklynmuseum_{}.tsv'.format(int(time.time()))
API_KEY     = os.environ['BROOKLYN_MUSEUM_API_KEY']
LIMIT       = 10
ENDPOINT    = 'https://www.brooklynmuseum.org/api/v2/'


logging.basicConfig(format='%(asctime)s: [%(levelname)s - Brooklyn Museum API] =======> %(message)s', level=logging.INFO)

def getObjects(_offset=0, _date=None):
    #Get a list of recently updated/uploaded objects. if no date is specified return all objects.
    startTime = time.time()

    endpoint = '{0}object?has_images=1&rights_type_permissive=1&limit={1}&offset={2}'.format(ENDPOINT, LIMIT, _offset)
    #if _date:
        #endpoint += '&date_added={}'.format(_date)  #or use load_date

    headers  = {'api_key': API_KEY}
    result   = requestContent(endpoint, headers)
    delayProcessing(startTime, DELAY)

    if result and result.get('message', '').lower() == 'success.':

        objData = result.get('data')
        return list(obj['id'] for obj in objData)

    else:
        logging.warning('Content not available!')

        return None


def getMetaData(_objectID):
    logging.info('Processing object: {}'.format(_objectID))
    startTime   = time.time()
    metaData    = {}
    objectData  = {}
    extracted   = []
    imgURL      = ''
    width       = ''
    height      = ''
    foreignID   = ''
    foreignURL  = ''
    title       = ''
    creator     = ''
    license     = ''
    version     = ''

    endpoint    = '{0}object/{1}'.format(ENDPOINT, _objectID)
    headers     = {'api_key': API_KEY}
    result      = requestContent(endpoint, headers)
    delayProcessing(startTime, DELAY)

    if result and result.get('data') is not None:
        objectData = result.get('data')

        #verify the license
        rightsInfo = objectData.get('rights_type')

        if 'creative commons' not in rightsInfo.get('name').lower():
            logging.warning('License not detected!')
            return None

        licenseInfo = re.search('https://creativecommons.org/licenses/[^\s]+', rightsInfo.get('description'))
        licenseURL  = licenseInfo.group(0).strip()
        if licenseURL:
            ccURL               = urlparse(licenseURL)
            license, version    = getLicense(ccURL.netloc, ccURL.path, licenseURL)
        else:
            logging.warning('License not detected!')
            return None

        title       = sanitizeString(objectData.get('title', ''))

        #the API doesnt provide a direct link to the landing page. Exception provided below
        foreignURL  = 'https://www.brooklynmuseum.org/opencollection/objects/{}'.format(_objectID)

        artists     = objectData.get('artists')
        artistInfo  = [{'name': sanitizeString(artist['name']), 'nationality': sanitizeString(artist['nationality'])} for artist in artists]
        if artistInfo:
            creator                 = artistInfo[0].get('name')
            metaData['artist_info'] = artistInfo

        metaData['credit_line']         = sanitizeString(objectData.get('credit_line'))
        metaData['medium']              = sanitizeString(objectData.get('medium'))
        metaData['description']         = sanitizeString(objectData.get('description'))
        metaData['date']                = sanitizeString(objectData.get('object_date'))
        metaData['credit_line']         = sanitizeString(objectData.get('period'))
        metaData['classification']      = sanitizeString(objectData.get('classification'))
        metaData['accession_number']    = sanitizeString(objectData.get('accession_number'))

        #extract the image(s)
        imageInfo = objectData.get('images')
        if not imageInfo:
            logging.warning('Image not detected for object {}'.format(_objectID))
            return None

        if len(imageInfo) > 1:
            metaData['set'] = foreignURL

        for img in imageInfo:
            foreignID   = img.get('id', '')
            imgURL      = img.get('largest_derivative_url', '')

            if not imgURL:
                logging.warning('Image not detected for object {}'.format(_objectID))
                continue

            thumbnail   = img.get('standard_size_url', '')
            lgDeriv     = img.get('largest_derivative')
            if lgDeriv:
                #get the image dimensions
                derivatives = img.get('derivatives')
                if type(derivatives) is list:
                    dimensions  = [(dim.get('width'), dim.get('height')) for dim in derivatives if str(dim.get('size')) == str(lgDeriv)]
                    width = dimensions[0][0]
                    height = dimensions[0][1]

            metaData['caption']     = sanitizeString(img.get('caption'))
            metaData['credit']      = sanitizeString(img.get('credit'))

            extracted.append([
                str(foreignID),
                foreignURL,
                imgURL,
                thumbnail if thumbnail else '\\N',
                str(int(float(width))) if width else '\\N',
                str(int(float(height))) if height else '\\N',
                '\\N',
                license,
                str(version),
                creator if creator else '\\N',
                '\\N',
                title if title else '\\N',
                '\\N' if not metaData else json.dumps(metaData, ensure_ascii=False),
                '\\N',
                'f',
                'brooklynmuseum',
                'brooklynmuseum'
            ])

    else:
        logging.warning('Content not available!')
        return None


    writeToFile(extracted, FILE)
    delayProcessing(startTime, DELAY)


def main():
    offset      = 0
    isValid     = True

    while isValid:
        objIDs      = getObjects(offset)

        if objIDs:
            list(map(lambda obj: getMetaData(obj), objIDs))

            offset += LIMIT
        else:
            isValid = False
            break

    logging.info('Terminated!')

if __name__ == '__main__':
    main()


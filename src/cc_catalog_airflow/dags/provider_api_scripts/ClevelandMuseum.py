"""
Content Provider:       Cleveland Museum

ETL Process:            Use the API to identify all CC0 artworks.

Output:                 TSV file containing the image, their respective meta-data.

Notes:                  http://openaccess-api.clevelandart.org/
                        No rate limit specified.
"""

from modules.etlMods import *

LIMIT       = 1000
DELAY       = 5.0 #time delay (in seconds)
FILE        = 'clevelandmuseum_{}.tsv'.format(int(time.time()))

logging.basicConfig(format='%(asctime)s: [%(levelname)s - Cleveland Museum API] =======> %(message)s', level=logging.INFO)


def getMetaData(_data):
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
    key         = None

    #verify the license
    if (not ('share_license_status' in _data)) or (str(_data['share_license_status']).upper() != 'CC0'):
        logging.warning('CC0 license not detected!')
        return None

    #get the landing page
    foreignURL  = _data.get('url', None)

    #get the image url and dimension
    imgInfo     = _data.get('images')

    if imgInfo.get('web'):
        imgURL  = imgInfo.get('web', {}).get('url', None)
        key     = 'web'

    elif imgInfo.get('print'):
        imgURL  = imgInfo.get('print', {}).get('url', None)
        key     = 'print'

    elif imgInfo.get('full'):
        imgURL  = imgInfo.get('full', {}).get('url', None)
        key     = 'full'

    if imgURL and key:
        width   = imgInfo[key]['width']
        height  = imgInfo[key]['height']


    #provider identifier for the artwork
    foreignID   = _data.get('id', imgURL)

    #title
    title       = sanitizeString(_data.get('title', ''))

    if not foreignURL:
        logging.warning('Landing page not detected')
        return None

    #get creator info
    creatorInfo = _data.get('creators', {})
    creatorName = None

    if creatorInfo:
        creatorName = creatorInfo[0].get('description', '')

    if creatorName:
        creator = sanitizeString(creatorName)


    #get additional meta data
    metaData['accession_number'] = sanitizeString(_data.get('accession_number', ''))
    metaData['technique']        = sanitizeString(_data.get('technique', ''))
    metaData['date']             = sanitizeString(_data.get('creation_date', ''))
    metaData['credit_line']      = sanitizeString(_data.get('creditline', ''))
    metaData['medium']           = sanitizeString(_data.get('technique', ''))
    metaData['classification']   = sanitizeString(_data.get('type', ''))
    metaData['culture']          = sanitizeString(','.join(list(filter(None, _data.get('culture', '')))))
    metaData['tombstone']        = sanitizeString(_data.get('tombstone', ''))

    #No description of artwork. The digital_description and wall_description are null.

    return [
            str(foreignID),
            foreignURL,
            imgURL,
            '\\N',
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
            'clevelandmuseum',
            'clevelandmuseum'
        ]



def main():
    logging.info('Begin: Cleveland Museum API requests')

    offset  = 0
    isValid = True

    while isValid:
        startTime   = time.time()
        endpoint    = 'http://openaccess-api.clevelandart.org/api/artworks/?cc0=1&has_image=1&limit={0}&skip={1}'.format(LIMIT, offset)
        batch       = requestContent(endpoint)

        if batch and ('data' in batch):
            extracted = batch['data']

            if extracted:
                result = map(lambda data: getMetaData(data), extracted)
                writeToFile(list(result), FILE)
                offset += LIMIT

                delayProcessing(startTime, DELAY)

            else:
                isValid = False
                break


    logging.info('Terminated!')


if __name__ == '__main__':
    main()

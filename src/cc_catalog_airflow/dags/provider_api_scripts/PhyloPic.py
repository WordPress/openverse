"""
Content Provider:       PhyloPic

ETL Process:            Use the API to identify all CC licensed images.

Output:                 TSV file containing the image, their respective meta-data.

Notes:                  http://phylopic.org/api/
                        No rate limit specified.
"""

from modules.etlMods import *


DELAY   = 5.0 #time delay (in seconds)
FILE    = 'phylopic_{}.tsv'.format(int(time.time()))
LIMIT   = 5

logging.basicConfig(format='%(asctime)s: [%(levelname)s - PhyloPic API] =======> %(message)s', level=logging.INFO)


def getTotalImages():
    #Get the total number of PhyloPic images
    ctr      = 0
    endpoint = 'http://phylopic.org/api/a/image/count'
    result   = requestContent(endpoint)

    if result and result.get('success') == True:
        ctr = result.get('result')

    return ctr



def getImageIDs(**args):
    limit       = LIMIT
    offset      = 0
    endpoint    = ''

    if args.get('date'):
        #Get a list of recently updated/uploaded objects.
        date     = args['date']
        endpoint = 'http://phylopic.org/api/a/image/list/modified/{}'.format(date)

    else:
        #get all images and limit the results for each request.
        offset   = args['offset']
        endpoint = 'http://phylopic.org/api/a/image/list/{}/{}'.format(offset, limit)

    if endpoint == '':
        logging.warning('Unable to parse endpoint: {}, args: {}'.format(endpoint, args))
        return [None]

    result   = requestContent(endpoint)
    imageIDs = None

    if result and result.get('success') == True:
        data = list(result.get('result'))

        if len(data) > 0:
            imageIDs = list(map(lambda res: res.get('uid'), data))

    if not imageIDs:
        logging.warning('Content not available!')
        return [None]

    return imageIDs


def getMetaData(_uuid):
    logging.info('Processing UUID: {}'.format(_uuid))

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
    request     = requestContent(endpoint)

    if request and request.get('success') == True:
        result  = request['result']

    licenseInfo = result.get('licenseURL')
    if licenseInfo:
        ccURL               = urlparse(licenseInfo.strip())
        license, version    = getLicense(ccURL.netloc, ccURL.path, _uuid)

    if not license:
        logging.warning('License not detected in url: {}/image/{}'.format(baseURL, _uuid))
        return None


    imgInfo = result.get('pngFiles')
    if imgInfo:
        img = list(filter(lambda x: (int(str(x.get('width', '0'))) >= 500), imgInfo))
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
        logging.warning('Image not detected in url: {}/image/{}'.format(baseURL, _uuid))
        return None

    foreignID   = imgURL
    foreignURL  = '{}/image/{}'.format(baseURL, _uuid)

    firstName   = sanitizeString(result.get('submitter', {}).get('firstName'))
    lastName    = sanitizeString(result.get('submitter', {}).get('lastName'))
    creator     = '{} {}'.format(firstName, lastName).strip()

    taxa        = result.get('taxa', [])#[0].get('canonicalName', {}).get('string')
    taxaList    = None
    if taxa:
        taxa     = list(filter(lambda x: x.get('canonicalName') is not None, taxa))
        taxaList = list(map(lambda x: sanitizeString(x.get('canonicalName', {}).get('string', '')), taxa))


    if taxaList:
        title = taxaList[0]

        if len(taxaList) > 1:
            metaData['taxa'] = taxaList


    if result.get('credit'):
        metaData['credit_line'] = sanitizeString(result.get('credit'))
        metaData['pub_date']    = sanitizeString(result.get('submitted'))



    delayProcessing(startTime, DELAY)
    return [
            foreignID, foreignURL, imgURL,
            thumbnail if thumbnail else '\\N',
            str(width) if width else '\\N',
            str(height) if height else '\\N', '\\N',
            license, str(version),
            creator if creator else '\\N', '\\N',
            title if title else '\\N',
            json.dumps(metaData, ensure_ascii=False) if bool(metaData) else '\\N',
            '\\N', 'f', 'phylopic', 'phylopic'
        ]


def execJob(**args):
    startTime   = time.time()
    result      = getImageIDs(**args)
    result      = list(filter(None, list(result)))
    delayProcessing(startTime, DELAY)

    if result:
        #get image details
        extracted = list(map(lambda uuid: getMetaData(uuid), result))

        #write batch to file
        writeToFile(extracted, FILE)
        delayProcessing(startTime, DELAY)


def main():
    logging.info('Begin: PhyloPic API requests')
    param   = None
    offset  = 0


    parser  = argparse.ArgumentParser(description='PhyloPic API Job', add_help=True)
    parser.add_argument('--mode', choices=['default', 'all'],
            help='Identify all images from the previous day [default] or process the entire collection [all].')


    args = parser.parse_args()
    if str(args.mode) == 'all':
        logging.info('Processing all images')
        param = {'offset': offset}

        imgCtr  = getTotalImages()
        logging.info('Total images: {}'.format(imgCtr))

        while offset <= imgCtr:
            execJob(**param)
            offset += LIMIT
            param   = {'offset': offset}

    else:
        param = {'date': datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')}
        logging.info('Processing date: {}'.format(param['date']))
        execJob(**param)


    logging.info('Terminated!')


if __name__ == '__main__':
    main()

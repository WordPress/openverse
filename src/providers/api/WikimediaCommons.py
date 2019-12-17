"""
Content Provider:       Wikimedia Commons

ETL Process:            Use the API to identify all CC-licensed images.

Output:                 TSV file containing the image, the respective meta-data.

Notes:                  https://www.mediawiki.org/wiki/API:Main_page
                        No rate limit specified.
"""

from modules.etlMods import *
import calendar
import lxml.html as html
from urllib.parse import urlparse

logging.basicConfig(format='%(asctime)s: [%(levelname)s - MediaWiki API] =======> %(message)s', level=logging.INFO)

LIMIT   = 40
DELAY   = 5.0 #time delay (in seconds)
FILE    = 'wmc_{}.tsv'.format(int(time.time()))
WM_HOST = 'commons.wikimedia.org'
SOURCE  = 'wikimedia'


def getImageBatch(_startDate, _endDate, _continue=None):
    logging.info('Processing image batch, continue token: {}'.format(_continue))

    endpoint = 'https://www.mediawiki.org/w/api.php?action=query&generator=allimages&prop=imageinfo&gailimit={0}&gaisort=timestamp&gaistart={1}T00:00:00Z&gaiend={2}T00:00:00Z&iiprop=url|user|dimensions|extmetadata&iiurlwidth=300&format=json'.format(LIMIT, _startDate, _endDate)

    if _continue:
        endpoint = '{}&gaicontinue={}'.format(endpoint, _continue)

    request      = requestContent(endpoint)
    if request.get('query'):
        cntToken = request.get('continue', {}).get('gaicontinue')
        result   = request.get('query', {}).get('pages')

        return [cntToken, result]

    return [None, None]


def cleanse_url(url_string):
    """
    Check to make sure that a url is valid, and prepend a protocol if needed
    """

    parse_result = urlparse(url_string)

    if parse_result.netloc == WM_HOST:
        parse_result = urlparse(url_string, scheme='https')
    elif not parse_result.scheme:
        parse_result = urlparse(url_string, scheme='http')

    if parse_result.netloc or parse_result.path:
        return parse_result.geturl()


def extract_creator_info(artist_string):
    if not artist_string:
        return (None, None)
    artist_elem = html.fromstring(artist_string)
    # We take all text to replicate what is shown on Wikimedia Commons
    artist_text = ''.join(artist_elem.xpath('//text()')).strip()
    url_list = list(artist_elem.iterlinks())
    artist_url = cleanse_url(url_list[0][2]) if url_list else None
    return (artist_text, artist_url)

def getMetaData(_imgData):
    foreignID   = ''
    foreignURL  = ''
    imgURL      = ''
    thumbnail   = ''
    width       = ''
    height      = ''
    metaData    = {}
    license     = ''
    version     = ''
    owner       = ''
    ownerURL    = ''
    title       = ''

    foreignID = _imgData.get('pageid')
    logging.info('Processing page ID: {}'.format(foreignID))

    imageInfo = _imgData.get('imageinfo', {})
    if type(imageInfo) is list:
        imageInfo = imageInfo[0]

    if imageInfo:
        licenseInfo = imageInfo.get('extmetadata', {}).get('LicenseUrl', {}).get('value')

        if licenseInfo:
            ccURL               = urlparse(licenseInfo.strip())
            license, version    = getLicense(ccURL.netloc, ccURL.path, foreignID)

        if not license:
            logging.warning('License not detected in page ID: {}'.format(foreignID))
            return None

    imgURL = imageInfo.get('url', '')
    if imgURL:
        width       = sanitizeString(str(imageInfo.get('width', '')))
        height      = sanitizeString(str(imageInfo.get('height', '')))
        thumbnail   = imageInfo.get('thumburl', '')
    else:
        logging.warning('Image not detected in page ID: {}'.format(foreignID))
        return None

    artist_string = imageInfo\
        .get('extmetadata', {})\
        .get('Artist', {})\
        .get('value', '')
    owner, ownerURL = extract_creator_info(artist_string)
    if owner:
        ownerURL = 'https://commons.wikimedia.org/wiki/User:{}'.format(owner)

    descr = imageInfo.get('extmetadata', {}).get('ImageDescription', {}).get('value')
    if descr:
        metaData['description'] = sanitizeString(descr)

    foreignURL = imageInfo.get('descriptionshorturl', '')
    if foreignURL == '':
        return None

    title = sanitizeString(_imgData.get('title', ''))

    return create_tsv_list_row(
        foreign_identifier=foreignID,
        foreign_landing_url=foreignURL,
        image_url=imgURL,
        thumbnail=thumbnail,
        width=width,
        height=height,
        license_=license,
        license_version=version,
        creator=owner,
        creator_url=ownerURL,
        title=title,
        meta_data=metaData,
        provider=SOURCE,
        source=SOURCE
    )


def execJob(_param):
    totalImages = 0
    isValid     = True
    cntToken    = None

    logging.info('Processing date: {} to {}'.format(_param.get('start'), _param.get('end')))

    cntToken, imgBatch  = getImageBatch(_param.get('start'), _param.get('end'))

    while isValid and imgBatch:
        startTime   = time.time()
        extracted   = list(map(lambda img: getMetaData(img[1]), imgBatch.items()))
        extracted   = list(filter(None, extracted))
        totalImages += len(extracted)

        logging.info('Extracted {} CC licensed images. Total images: {}'.format(len(extracted), totalImages))


        writeToFile(extracted, FILE)
        delayProcessing(startTime, DELAY)


        if not cntToken:
            isValid = False
            break


        cntToken, imgBatch  = getImageBatch(_param.get('start'), _param.get('end'), cntToken)


    logging.info('Total images: {}'.format(totalImages))


def main():
    logging.info('Begin: MediaWiki API requests')

    param   = None

    parser  = argparse.ArgumentParser(description='MediaWiki API Job', add_help=True)
    parser.add_argument('--mode', choices=['default'],
            help='Identify all images that were uploaded the previous day [default]')
    parser.add_argument('--date', type=lambda dt: datetime.strptime(dt, '%Y-%m-%d'),
            help='Identify images uploaded on a user-defined date (format: YYYY-MM-DD).')
    parser.add_argument('--month', type=lambda dt: datetime.strptime(dt, '%Y-%m'),
            help='Identify images uploaded during a user-defined month (format: YYYY-MM).')


    args = parser.parse_args()
    if args.date:
        param           = {}
        param['start']  = args.date.strftime('%Y-%m-%d')
        param['end']    = datetime.strftime(datetime.strptime(param['start'], '%Y-%m-%d') + timedelta(days=1), '%Y-%m-%d')

    elif args.month:
        param           = {}
        param['start']  = args.month.strftime('%Y-%m-01')
        days            = calendar.monthrange(args.month.year, args.month.month)[1]
        param['end']    = datetime.strftime(datetime.strptime(param['start'], '%Y-%m-%d') + timedelta(days=days), '%Y-%m-%d')

    elif args.mode:

        if str(args.mode) == 'default': #the previous day
            param           = {}
            param['start']  = datetime.strftime(datetime.now() - timedelta(days=1), '%Y-%m-%d')
            param['end']    = datetime.strftime(datetime.strptime(param['start'], '%Y-%m-%d') + timedelta(days=1), '%Y-%m-%d')
        else:
            logging.warning('Invalid option')
            logging.info('Terminating!')

    #run the job and identify all CC licensed images
    if param:
        execJob(param)


    logging.info('Terminated!')



if __name__ == '__main__':
    main()

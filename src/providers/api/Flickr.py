"""
Content Provider:       Flickr

ETL Process:            Use the API to identify all CC licensed images.

Output:                 TSV file containing the images and the respective meta-data.

Notes:                  https://www.flickr.com/help/terms/api
                        Rate limit: 3600 queries per hour.
"""

from modules.etlMods import *
import calendar
from dateutil import rrule

logging.getLogger(__name__)
Ts_RANGE    = int(5) #process job using 5 minute intervals
DELAY       = 1.0 #time delay (in seconds)
FILE        = 'flickr_{}.tsv'.format(int(time.time()))
SIZE        = 500
API_KEY     = os.environ['FLICKR_API_KEY']
FLICKR      = 'flickr'


URL      = None
#QUERY    = 'https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key={0}&min_upload_date={1}&max_upload_date={2}&license=1&media=photos&content_type=1&extras=description,license,date_upload,date_taken,owner_name,tags,o_dims,url_t,url_s,url_m,url_l&per_page={3}&format=json&nojsoncallback=1'.format(API, MIN_DATE, MAX_DATE, SIZE)

logging.basicConfig(format='%(asctime)s: [%(levelname)s - Flickr API] =======> %(message)s', level=logging.INFO)
#logging.info('processing date range: {} - {}'.format(MIN_DATE, MAX_DATE))

def getLicense(_index):
    version     = 2.0
    ccLicense   = {
        1:  'by-nc-sa',
        2:  'by-nc',
        3:  'by-nc-nd',
        4:  'by',
        5:  'by-sa',
        6:  'by-nd',
        9:  'CC0',
        10: 'PDM'
    }

    if _index == 'all':
        return ccLicense.keys()
    else:
        _index  = int(_index)


    if (_index <= 0) or (_index in [7, 8]) or (_index > 10):
        logging.warning('License not detected!')
        return None, None


    license = ccLicense[_index]

    if _index in [9, 10]:
        version = 1.0

    return license, version


def get_image_url(_data):
    for size in ['l', 'm', 's']: # prefer large, then medium, then small images
        url_key = 'url_{}'.format(size)
        height_key = 'height_{}'.format(size)
        width_key = 'width_{}'.format(size)
        if url_key in _data:
            return (
                _data.get(url_key), _data.get(height_key), _data.get(width_key))

    logging.warning('Image not detected!')
    return (None, None, None)


def create_meta_data_dict(_data):
    meta_data = {}
    if 'dateupload' in _data:
        meta_data['pub_date'] = sanitizeString(_data.get('dateupload'))

    if 'datetaken' in _data:
        meta_data['date_taken'] = sanitizeString(_data.get('datetaken'))

    description = sanitizeString(_data.get('description', {}).get('_content'))
    if description:
        meta_data['description'] = description

    return meta_data


def create_tags_list(_data):
    max_tags = 20
    raw_tag_string = _data.get('tags', '').strip()
    if raw_tag_string:
        raw_tag_list = list(set(raw_tag_string.split()))[:max_tags]
        return [{'name': tag.strip(), 'provider': FLICKR} for tag in raw_tag_list]
    else:
        return None


def extractData(_data):
    title = _data.get('title')
    creator = _data.get('ownername')
    imageURL, height, width = get_image_url(_data)
    thumbnail = _data.get('url_s')
    license, version = getLicense(_data.get('license', -1))
    metaData = create_meta_data_dict(_data)
    tagData = create_tags_list(_data)

    if 'owner' in _data:
        creatorURL = 'www.flickr.com/photos/{}'.format(_data['owner']).strip()
    else:
        creatorURL = None

    foreignID = _data.get('id')

    if foreignID and creatorURL:
        foreignURL = '{}/{}'.format(creatorURL, foreignID)
    else:
        foreignURL = None


    return create_tsv_list_row(
        foreign_identifier=imageURL if not foreignID else foreignID,
        foreign_landing_url=foreignURL,
        image_url=imageURL,
        thumbnail=thumbnail,
        width=width,
        height=height,
        license=license,
        license_version=version,
        creator=creator,
        creator_url=creatorURL,
        title=title,
        meta_data=metaData,
        tags=tagData,
        watermarked='f',
        provider=FLICKR,
        source=FLICKR
    )


def getMetaData(_startTs, _endTs, _license, _switchDate=False):
    procTime    = time.time()
    pages       = 1
    curPage     = 1
    numImages   = 0
    endpoint    = 'https://api.flickr.com/services/rest/?method=flickr.photos.search'


    while curPage <= pages:
        #loop through each page of data
        logging.info('Processing page: {}'.format(curPage))

        queryStr    = '{0}&api_key={1}&min_upload_date={2}&max_upload_date={3}&license={5}&media=photos&content_type=1&extras=description,license,date_upload,date_taken,owner_name,tags,o_dims,url_t,url_s,url_m,url_l&per_page={4}&format=json&nojsoncallback=1&page={6}'.format(endpoint, API_KEY, _startTs, _endTs, SIZE, _license, curPage)

        if _switchDate:
            queryStr = queryStr.replace('upload_date', 'taken_date')

        imgData     = requestContent(queryStr)
        if imgData:
            status = imgData['stat']
            if status == 'ok':
                result  = imgData['photos']
                total   = result['total']   #total results
                pages   = result['pages']   #number of pages
                curPage = result['page']    #current page
                photos  = result['photo']   #image meta data for the current page

                if photos:
                    extracted = list(map(lambda photo: extractData(photo), photos))
                    extracted = list(filter(None, extracted))
                    numImages += len(extracted)
                    writeToFile(extracted, FILE)

        curPage += 1
        delayProcessing(procTime, DELAY) #throttle requests
        procTime = time.time()

    logging.info('Total pages processed: {}'.format(pages))

    return numImages


def execJob(_license, _startDate, _duration=1, _mode=None):
    totalImages = 0
    srtTime     = datetime.strptime(_startDate, '%Y-%m-%d %H:%M')
    endTime     = datetime.strptime(_startDate, '%Y-%m-%d %H:%M') + timedelta(hours=_duration)

    for dt in rrule.rrule(rrule.MINUTELY, dtstart=srtTime, until=endTime):
        elapsed = int((dt - srtTime).seconds/60)

        if elapsed % Ts_RANGE == 0:
            curTime = dt
            nxtTime = curTime + timedelta(minutes=Ts_RANGE)
            logging.info('Processing dates: {} to {}, license: {}'.format(curTime, nxtTime, getLicense(_license)[0]))

            #get the meta data within the time interval
            totalImages += getMetaData(curTime, nxtTime, _license) #check upload_date
            totalImages += getMetaData(curTime, nxtTime, _license, True) #check taken_date

    logging.info('Total {} images: {}'.format(getLicense(_license)[0], totalImages))


def main():
    logging.info('Begin: Flickr API requests')
    param       = None
    duration    = 1 #in hours

    parser  = argparse.ArgumentParser(description='Flickr API Job', add_help=True)
    parser.add_argument('--mode', choices=['default'],
            help='Identify all images that were uploaded in the previous hour [default] \nIdentify all images that were uploaded on a given date [date] or month [month].')
    parser.add_argument('--date', type=lambda dt: datetime.strptime(dt, '%Y-%m-%d'),
            help='Identify images uploaded on a given date (format: YYYY-MM-DD).')
    parser.add_argument('--month', type=lambda dt: datetime.strptime(dt, '%Y-%m'),
            help='Identify images uploaded in a given year and month (format: YYYY-MM).')


    args = parser.parse_args()
    if args.date:
        param    = args.date.strftime('%Y-%m-%d %H:%M')
        duration = 24

    elif args.month:
        param    = args.month.strftime('%Y-%m-01 %H:%M')
        days     = calendar.monthrange(args.month.year, args.month.month)[1]
        duration = 24 * int(days)

    elif args.mode:

        if str(args.mode) == 'default': #the start of the previous hour
            param = datetime.strftime(datetime.now() - timedelta(hours=1), '%Y-%m-%d %H:00')
        else:
            logging.warning('Invalid option')
            logging.info('Terminating!')

    #run the job and identify images for each CC license
    if param:
        list(map(lambda license: execJob(license, param, duration), list(getLicense('all'))))

    logging.info('Terminated!')


if __name__ == '__main__':
    main()

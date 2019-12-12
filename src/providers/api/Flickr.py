"""
Content Provider:       Flickr

ETL Process:            Use the API to identify all CC licensed images.

Output:                 TSV file containing the images and the respective meta-data.

Notes:                  https://www.flickr.com/help/terms/api
                        Rate limit: 3600 queries per hour.
"""

import argparse
import calendar
import logging
import os
import time
from datetime import datetime, timedelta
from dateutil import rrule

import modules.etlMods as em

logging.getLogger(__name__)
Ts_RANGE    = int(5) #process job using 5 minute intervals
DELAY       = 1.0 #time delay (in seconds)
FILE        = 'flickr_{}.tsv'.format(int(time.time()))
SIZE        = 500
API_KEY     = os.environ['FLICKR_API_KEY']
FLICKR      = 'flickr'
ENDPOINT    = 'https://api.flickr.com/services/rest/?method=flickr.photos.search'

logging.basicConfig(
    format='%(asctime)s: [%(levelname)s - Flickr API] =======> %(message)s',
    level=logging.INFO)

def get_license(_index):
    version = 2.0
    cc_license = {
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
        return cc_license.keys()
    else:
        _index  = int(_index)


    if (_index <= 0) or (_index in [7, 8]) or (_index > 10):
        logging.warning('License not detected!')
        return None, None


    license_ = cc_license[_index]

    if _index in [9, 10]:
        version = 1.0

    return license_, version


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
        meta_data['pub_date'] = em.sanitizeString(_data.get('dateupload'))

    if 'datetaken' in _data:
        meta_data['date_taken'] = em.sanitizeString(_data.get('datetaken'))

    description = em.sanitizeString(_data.get('description', {}).get('_content'))
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


def extract_data(_data):
    title = _data.get('title')
    creator = _data.get('ownername')
    image_url, height, width = get_image_url(_data)
    thumbnail = _data.get('url_s')
    license_, version = get_license(_data.get('license', -1))
    meta_data = create_meta_data_dict(_data)
    tags = create_tags_list(_data)

    if 'owner' in _data:
        creator_url = 'www.flickr.com/photos/{}'.format(_data['owner']).strip()
    else:
        creator_url = None

    foreign_id = _data.get('id')

    if foreign_id and creator_url:
        foreign_url = '{}/{}'.format(creator_url, foreign_id)
    else:
        foreign_url = None


    return em.create_tsv_list_row(
        foreign_identifier=image_url if not foreign_id else foreign_id,
        foreign_landing_url=foreign_url,
        image_url=image_url,
        thumbnail=thumbnail,
        width=width,
        height=height,
        license_=license_,
        license_version=version,
        creator=creator,
        creator_url=creator_url,
        title=title,
        meta_data=meta_data,
        tags=tags,
        watermarked='f',
        provider=FLICKR,
        source=FLICKR
    )


def construct_api_query_string(
        start_ts,
        end_ts,
        license_,
        cur_page,
        switch_date=False):
    date_type = 'taken' if switch_date else 'upload'
    api_query_string = (
        '{0}&api_key={1}&min_{7}_date={2}&max_{7}_date={3}&license={5}'
        '&media=photos&content_type=1&extras=description,license,date_upload,'
        'date_taken,owner_name,tags,o_dims,url_t,url_s,url_m,url_l'
        '&per_page={4}&format=json&nojsoncallback=1&page={6}'
    ).format(
        ENDPOINT, API_KEY, start_ts, end_ts, SIZE, license_, cur_page, date_type)

    return api_query_string


def process_images(start_ts, end_ts, license_, switch_date=False):
    proc_time    = time.time()
    pages       = 1
    cur_page     = 1
    num_images   = 0


    while cur_page <= pages:
        #loop through each page of data
        logging.info('Processing page: {}'.format(cur_page))

        api_query_string = construct_api_query_string(
            start_ts,
            end_ts,
            license_,
            cur_page,
            switch_date
        )

        img_data = em.requestContent(api_query_string)
        if img_data and img_data.get('stat') == 'ok':
            result  = img_data.get('photos', {})
            pages   = result.get('pages')   #number of pages
            cur_page = result.get('page')    #current page
            photos  = result.get('photo')   #image meta data for the current page

            if photos:
                # TODO update to >= python3.8, use walrus assignment
                extracted = [r for r in (extract_data(p) for p in photos) if r]
                num_images += len(extracted)
                em.writeToFile(extracted, FILE)

        cur_page += 1
        em.delayProcessing(proc_time, DELAY) #throttle requests
        proc_time = time.time()

    logging.info('Total pages processed: {}'.format(pages))

    return num_images


def exec_job(license_, start_date, _duration=1, _mode=None):
    total_images = 0
    start_time = datetime.strptime(start_date, '%Y-%m-%d %H:%M')
    end_time = datetime.strptime(start_date, '%Y-%m-%d %H:%M') + timedelta(hours=_duration)

    for dt in rrule.rrule(rrule.MINUTELY, dtstart=start_time, until=end_time):
        elapsed = int((dt - start_time).seconds/60)

        if elapsed % Ts_RANGE == 0:
            curTime = dt
            nxtTime = curTime + timedelta(minutes=Ts_RANGE)
            logging.info('Processing dates: {} to {}, license: {}'.format(curTime, nxtTime, get_license(license_)[0]))

            #get the meta data within the time interval
            total_images += process_images(curTime, nxtTime, license_) #check upload_date
            total_images += process_images(curTime, nxtTime, license_, True) #check taken_date

    logging.info('Total {} images: {}'.format(get_license(license_)[0], total_images))


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
        for license_ in get_license('all'):
            exec_job(license_, param, duration)

    logging.info('Terminated!')


if __name__ == '__main__':
    main()

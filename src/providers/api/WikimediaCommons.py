"""
Content Provider:       Wikimedia Commons

ETL Process:            Use the API to identify all CC-licensed images.

Output:                 TSV file containing the image, the respective
                        meta-data.

Notes:                  https://commons.wikimedia.org/wiki/API:Main_page
                        No rate limit specified.
"""

import argparse
import calendar
import logging
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse

import lxml.html as html

import modules.etlMods as etl_mods

logging.basicConfig(
    format='%(asctime)s: [%(levelname)s - MediaWiki API] =======> %(message)s',
    level=logging.INFO)

LIMIT = 40
DELAY = 5.0  # time delay (in seconds)
FILE = 'wmc_{}.tsv'.format(int(time.time()))
WM_HOST = 'commons.wikimedia.org'
SOURCE = 'wikimedia'


def get_image_batch(start_date, end_date, continue_=None):
    logging.info(
        'Processing image batch, continue token: {}'.format(continue_))

    endpoint = (
        'https://{0}/w/api.php?action=query&generator=allimages'
        '&prop=imageinfo&gailimit={1}&gaisort=timestamp&gaistart={2}T00:00:00Z'
        '&gaiend={3}T00:00:00Z&iiprop=url|user|dimensions|extmetadata'
        '&iiurlwidth=300&format=json'
    ).format(WM_HOST, LIMIT, start_date, end_date)

    if continue_:
        endpoint = '{}&gaicontinue={}'.format(endpoint, continue_)

    request = etl_mods.requestContent(endpoint)
    if request and request.get('query'):
        continue_token = request.get('continue', {}).get('gaicontinue')
        result = request.get('query', {}).get('pages')

        return continue_token, result

    return None, None


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


def extract_creator_info(image_info):
    artist_string = image_info\
        .get('extmetadata', {})\
        .get('Artist', {})\
        .get('value', '')

    if not artist_string:
        return (None, None)

    artist_elem = html.fromstring(artist_string)
    # We take all text to replicate what is shown on Wikimedia Commons
    artist_text = ''.join(artist_elem.xpath('//text()')).strip()
    url_list = list(artist_elem.iterlinks())
    artist_url = cleanse_url(url_list[0][2]) if url_list else None
    return (artist_text, artist_url)


def get_image_info_dict(image_data):
    image_info_list = image_data.get('imageinfo')
    if image_info_list:
        image_info = image_info_list[0]
    else:
        image_info = {}
    return image_info


def create_meta_data_dict(image_data):
    meta_data = {}
    image_info = get_image_info_dict(image_data)
    description = image_info\
        .get('extmetadata', {})\
        .get('ImageDescription', {})\
        .get('value')
    if description:
        description_text = ' '.join(
            html.fromstring(description).xpath('//text()')).strip()
        meta_data['description'] = description_text
    return meta_data


def get_license(image_info, image_url):
    license_url = image_info\
        .get('extmetadata', {})\
        .get('LicenseUrl', {})\
        .get('value', '')\
        .strip()
    if license_url:
        parsed_license_url = urlparse(license_url)
        license, version = etl_mods.getLicense(
            parsed_license_url.netloc, parsed_license_url.path, image_url)
    else:
        license, version = None, None
    return (license, version)


def process_image_data(image_data):
    foreign_id = image_data.get('pageid')
    logging.info('Processing page ID: {}'.format(foreign_id))

    image_info = get_image_info_dict(image_data)

    foreign_landing_url = image_info.get('descriptionshorturl')
    image_url = image_info.get('url')
    thumbnail = image_info.get('thumburl')
    width = image_info.get('width')
    height = image_info.get('height')
    license, license_version = get_license(image_info, image_url)
    creator, creator_url = extract_creator_info(image_info)
    title = image_data.get('title')
    meta_data = create_meta_data_dict(image_data)

    return etl_mods.create_tsv_list_row(
        foreign_identifier=foreign_id,
        foreign_landing_url=foreign_landing_url,
        image_url=image_url,
        thumbnail=thumbnail,
        width=width,
        height=height,
        license_=license,
        license_version=license_version,
        creator=creator,
        creator_url=creator_url,
        title=title,
        meta_data=meta_data,
        provider=SOURCE,
        source=SOURCE
    )


def exec_job(param):
    total_images = 0
    is_valid = True
    continue_token = None

    logging.info(
        'Processing date: {} to {}'.format(
            param.get('start'), param.get('end')))

    continue_token, image_batch = get_image_batch(
        param.get('start'), param.get('end'))

    while is_valid and image_batch:
        startTime = time.time()
        row_generator = (process_image_data(i) for i in image_batch.values())
        extracted = [row for row in row_generator if row]
        total_images += len(extracted)

        logging.info(
            'Extracted {} CC licensed images. Total images: {}'.format(
                len(extracted), total_images))

        etl_mods.writeToFile(extracted, FILE)
        etl_mods.delayProcessing(startTime, DELAY)

        if not continue_token:
            is_valid = False
            break

        continue_token, image_batch = get_image_batch(
            param.get('start'), param.get('end'), continue_token)

    logging.info('Total images: {}'.format(total_images))


def main():
    logging.info('Begin: MediaWiki API requests')

    param = None

    parser = argparse.ArgumentParser(
        description='MediaWiki API Job', add_help=True)
    parser.add_argument(
        '--mode',
        choices=['default'],
        help='Identify images uploaded the previous day [default]')
    parser.add_argument(
        '--date',
        type=lambda dt: datetime.strptime(dt, '%Y-%m-%d'),
        help='Identify images uploaded on a date (format: YYYY-MM-DD).')
    parser.add_argument(
        '--month',
        type=lambda dt: datetime.strptime(dt, '%Y-%m'),
        help='Identify images uploaded during a month (format: YYYY-MM).')

    args = parser.parse_args()
    if args.date:
        param = {}
        param['start'] = args.date.strftime('%Y-%m-%d')
        param['end'] = datetime.strftime(
            datetime.strptime(
                param['start'], '%Y-%m-%d') + timedelta(days=1),
            '%Y-%m-%d')

    elif args.month:
        param = {}
        param['start'] = args.month.strftime('%Y-%m-01')
        days = calendar.monthrange(args.month.year, args.month.month)[1]
        param['end'] = datetime.strftime(
            datetime.strptime(
                param['start'], '%Y-%m-%d') + timedelta(days=days),
            '%Y-%m-%d')

    elif args.mode:

        if str(args.mode) == 'default':  # the previous day
            param = {}
            param['start'] = datetime.strftime(
                datetime.now() - timedelta(days=1), '%Y-%m-%d')
            param['end'] = datetime.strftime(
                datetime.strptime(
                    param['start'], '%Y-%m-%d') + timedelta(days=1),
                '%Y-%m-%d')
        else:
            logging.warning('Invalid option')
            logging.info('Terminating!')

    # run the job and identify all CC licensed images
    if param:
        exec_job(param)

    logging.info('Terminated!')


if __name__ == '__main__':
    main()

import logging
import os
import re
import requests
import time
import json
import argparse
import random
from datetime import datetime, timedelta
import sys
from urllib.parse import urlparse

PATH    = os.environ['OUTPUT_DIR']

def writeToFile(_data, _name, output_dir=PATH):
    outputFile = '{}{}'.format(output_dir, _name)

    if len(_data) < 1:
        return None

    logging.info('Writing to file => {}'.format(outputFile))

    with open(outputFile, 'a') as fh:
        for line in _data:
            if line:
                fh.write('\t'.join(line) + '\n')


def sanitizeString(_data):
    if _data is None:
        return ''
    else:
        _data = str(_data)

    _data       = _data.strip()
    _data       = _data.replace('"', "'")
    _data       = re.sub(r'\n|\r', ' ', _data)
    #_data      = re.escape(_data)

    backspaces  = re.compile('\b+')
    _data       = backspaces.sub('', _data)
    _data       = _data.replace('\\', '\\\\')

    return re.sub(r'\s+', ' ', _data)


def delayProcessing(_startTime, _maxDelay):
    minDelay = 1.0

    #subtract time elapsed from the requested delay
    elapsed       = float(time.time()) - float(_startTime)
    delayInterval = round(_maxDelay - elapsed, 3)
    waitTime      = max(minDelay, delayInterval) #time delay between requests.

    logging.info('Time delay: {} second(s)'.format(waitTime))
    time.sleep(waitTime)


def requestContent(_url, _headers=None):
    #TODO: pass the request headers and params in a dictionary

    logging.info('Processing request: {}'.format(_url))

    try:
        response = requests.get(_url, headers=_headers)

        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            logging.warning('Unable to request URL: {}. Status code: {}'.format(url, response.status_code))
            return None

    except Exception as e:
        logging.error('There was an error with the request.')
        logging.info('{}: {}'.format(type(e).__name__, e))
        return None


def getLicense(_domain, _path, _url):

    if 'creativecommons.org' not in _domain:
        logging.warning('The license for the following work -> {} is not issued by Creative Commons.'.format(_url))
        return [None, None]

    pattern   = re.compile('/(licenses|publicdomain)/([a-z\-?]+)/(\d\.\d)/?(.*?)')
    if pattern.match(_path.lower()):
        result  = re.search(pattern, _path.lower())
        license = result.group(2).lower().strip()
        version = result.group(3).strip()

        if result.group(1) == 'publicdomain':
            if license == 'zero':
                license = 'cc0';
            elif license == 'mark':
                license = 'pdm'
            else:
                logging.warning('License not detected!')
                return [None, None]

        elif (license == ''):
            logging.warning('License not detected!')
            return [None, None]


        return [license, version]

    return [None, None]

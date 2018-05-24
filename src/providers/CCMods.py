import sys
import gzip
import StringIO
import requests
import logging
import re

logging.getLogger('CCModule')
logging.basicConfig(format='%(asctime)s: [%(levelname)s - CCModule] =======> %(message)s', level=logging.INFO)


def getLicense(_str):

    pattern   = re.compile('/(licenses|publicdomain)/([a-z\-?]+)/(\d\.\d)/?(.*?)')
    if pattern.match(_str):
        result  = re.search(pattern, _str)
        license = result.group(2).lower()
        version = result.group(3)

        if result.group(1) == 'publicdomain':
            if license == 'zero':
                license = 'cc0';
            elif license == 'mark':
                license = 'pdm'
            else:
                logging.warning('License not detected!')
                return None

        return [license, version]

    return None


def getWARCRecord(_file, _offset, _length):
    _offset = int(str(_offset))
    _length = int(str(_length))
    _file   = str(_file)

    rnge    = 'bytes={}-{}'.format(_offset, (_offset + _length - 1))
    uri     = 'https://commoncrawl.s3.amazonaws.com/{}'.format(_file)

    try:
        response    = requests.get(uri, headers={'Range': rnge})

    except Exception as e:
        logging.error('{}: {}'.format(type(e).__name__, e))
        return None

    else:
        content     = StringIO.StringIO(response.content)
        fh          = gzip.GzipFile(fileobj=content)

        return fh.read()


#print getWARCRecord('crawl-data/CC-MAIN-2017-09/segments/1487501172447.23/warc/CC-MAIN-20170219104612-00388-ip-10-171-10-108.ec2.internal.warc.gz', 823569443, 54223)

#print getLicense('/publicdomain/mark/werw/')

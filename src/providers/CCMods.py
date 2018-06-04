import sys
import gzip
import StringIO
import requests
import logging
import re
from pyspark.sql import SQLContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import concat, col, lit


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

def getProviderData(_provider, _input):
    spk          = SparkSession.builder.getOrCreate()
    dataDF       = spk.read.parquet(_input)
    providerDF   = dataDF.select(concat('provider_domain', 'content_path').alias('url'), \
                                 concat('warc_segment', lit('/warc/'), 'warc_filename').alias('warc_filename'), \
                                 'content_offset', 'deflate_length')\
                        .where(col('provider_domain').like('%{}'.format(_provider)))\
                        .drop_duplicates(['url'])

    providerData = providerDF.rdd.map(lambda row: '\t'.join([str(col) for col in row])).collect() #convert dataframe into a list of tab delimited elements

    return providerData



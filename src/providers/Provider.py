import re
import sys
import gzip
import json
import StringIO
import requests
import logging
from pyspark.sql import SQLContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import concat, col, lit


logging.basicConfig(format='%(asctime)s - %(name)s: [%(levelname)s] =======> %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class Provider:

    def __init__(self, _name, _domain, _cc_index):
        """
        Initialize a Provider with their name, domain and the common crawl index that contains their data.
        Subsequently, validate the common crawl index parameter before initializing the job.

        Parameters
        ------------------
        _name:      string
            The provier's name

        _domain:    string
            The provider's domain/uri

        _cc_index:  string
            The common crawl index


        Returns
        ------------------
        None

        """
        self.name                   = _name
        self.domain                 = _domain
        self.crawlIndex             = None
        self.data                   = None

        self.provider               = ''
        self.source                 = ''
        self.foreign_identifier     = ''
        self.foreign_landing_url    = ''
        self.url                    = ''
        self.thumbnail              = ''
        self.width                  = ''
        self.height                 = ''
        self.filesize               = ''
        self.license                = ''
        self.license_version        = ''
        self.creator                = ''
        self.creator_url            = ''
        self.title                  = ''
        self.meta_data              = {}
        self.watermarked            = 'f'
        self.translation_available  = 'f'



        pattern = re.compile('CC-MAIN-\d{4}-\d{2}')

        if not pattern.match(_cc_index):
            logger.error('Invalid common crawl index format -> {}'.format(_cc_index))

        else:
            self.crawlIndex = _cc_index


    def __repr__(self):
        return 'Provider("{}", "{}", "{}")'.format(self.name, self.domain, self.crawlIndex)


    def __str__(self):
        keys = sorted(self.imageMetaData.keys())
        return '\t'.join([self.imageMetaData[key] if self.imageMetaData[key] is not None else 'NULL' for key in keys])


    def clearFields(self):
        self.provider               = ''
        self.source                 = ''
        self.foreignIdentifier      = ''
        self.foreignLandingURL      = ''
        self.url                    = ''
        self.thumbnail              = ''
        self.width                  = ''
        self.height                 = ''
        self.filesize               = ''
        self.license                = ''
        self.licenseVersion         = ''
        self.creator                = ''
        self.creatorURL             = ''
        self.title                  = ''
        self.metaData               = {}
        self.watermarked            = 'f'
        self.translation_available  = 'f'


    def formatOutput(self):
        return [
            self.foreignIdentifier,
            self.foreignLandingURL,
            self.url,
            self.thumbnail,
            self.width,
            self.height,
            self.filesize,
            self.license,
            self.licenseVersion,
            self.creator,
            self.creatorURL,
            self.title,
            json.dumps(self.metaData),
            self.watermarked,
            self.translation_available,
            self.provider,
            self.source
            ]


    @property
    def input(self):
        if self.crawlIndex is None:
            raise ValueError('Common Crawl index not specified!')

        return '../output/{}'.format(self.crawlIndex)


    @property
    def output(self):
        if self.crawlIndex is None:
            raise ValueError('Common Crawl index not specified!')

        return 'transformed/{}/{}'.format(self.crawlIndex, self.name.lower())


    def getForeignID(self, _str):
        foreignID = re.search('.*?/(\d+)/?$', _str)

        try:
            return foreignID.group(1)
        except:
            logger.error('Identifier not detected in: {}'.format(_str))
            return None


    def getLicense(self, _domain, _path, _url):

        if 'creativecommons.org' not in _domain:
            logger.warning('The license for the following work -> {} is not issued by Creative Commons.'.format(_url))
            return [None, None]

        pattern   = re.compile('/(licenses|publicdomain)/([a-z\-?]+)/(\d\.\d)/?(.*?)')
        if pattern.match(_path):
            result  = re.search(pattern, _path)
            license = result.group(2).lower()
            version = result.group(3)

            if result.group(1) == 'publicdomain':
                if license == 'zero':
                    license = 'cc0';
                elif license == 'mark':
                    license = 'pdm'
                else:
                    logger.warning('License not detected!')
                    return [None, None]

            return [license, version]

        return None


    def validateContent(self, _default, _html=None, _property=None):

        if _html:
            return _html.attrs[_property].strip().encode('unicode-escape')
        else:
            return _default


    def getWARCRecord(self, _file, _offset, _length):
        _offset = int(str(_offset))
        _length = int(str(_length))
        _file   = str(_file)

        rnge    = 'bytes={}-{}'.format(_offset, (_offset + _length - 1))
        uri     = 'https://commoncrawl.s3.amazonaws.com/{}'.format(_file)

        try:
            response    = requests.get(uri, headers={'Range': rnge})

        except Exception as e:
            logger.error('{}: {}'.format(type(e).__name__, e))
            return None

        else:
            content     = StringIO.StringIO(response.content)
            fh          = gzip.GzipFile(fileobj=content)

            return fh.read()


    def getData(self):
        spk         = SparkSession.builder.getOrCreate()
        dataDF      = spk.read.parquet(self.input)
        providerDF  = dataDF.select(concat('provider_domain', 'content_path').alias('url'), \
                                     concat('warc_segment', lit('/warc/'), 'warc_filename').alias('warc_filename'), \
                                     'content_offset', 'deflate_length')\
                            .where(col('provider_domain').like('%{}'.format(self.domain)))\
                            .dropDuplicates(['url'])

        providerData = providerDF.rdd.map(lambda row: '\t'.join([str(col) for col in row])).collect() #convert dataframe into a list of tab delimited elements

        return providerData


    def filterData(self, _data, _condition=None):

        if _condition:
            data = filter(lambda x: _condition in x.split('\t')[0], _data)
            self.data = data
        else:
            self.data = _data

        return self.data


    def getMetaData(self, _html, _url):
        #stub - each child should override this method.
        """

        Parameters
        ------------------
        _html: string
            The HTML page that was extracted from Common Crawls WARC file.

        _url: string
            The url for the webpage.


        Returns
        ------------------
        A tab separated string which contains the meta data that was extracted from the HTML.

        """
        pass


    def saveData(self, _data):
        spk = SparkSession.builder.getOrCreate()
        df  = spk.createDataFrame(_data)#.map(lambda x: tuple(x.split('\t'))))
        #df.write.mode('overwrite').options(sep='\t').csv(self.output)
        df.write.mode('overwrite').options(sep='\t', quote='').csv(self.output)


    def extractHTML(self, _iter):
        """

        Parameters
        ------------------
        _iter: iterator object
            The iterator for the RDD partition that was assigned to the current process.


        Returns
        ------------------
        metaData: generator
            The associated meta data for each url which contains:
                The content provider, content source, an image identifier,
                the url for both the webpage and the image file,
                the creative commons license and version for the artwork,
                the name of the artist, the title for the artwork
                and a json string with additional meta-data.
        """

        for row in _iter:
            data        = row.split('\t')
            metaData    = None

            content     = self.getWARCRecord(data[1].strip(), data[2].strip(), data[3].strip())

            if content:
                metaData = self.getMetaData(content.strip(), data[0].strip())

                if metaData:
                    yield metaData


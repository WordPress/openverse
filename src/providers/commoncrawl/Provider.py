import re
import sys
import gzip
import json
from io import StringIO, BytesIO
import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from pyspark.sql import SQLContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import concat, col, lit, when

logging.basicConfig(format='%(asctime)s - %(name)s: [%(levelname)s] =======> %(message)s', level=logging.INFO)

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
        self.tags                   = {}
        self.popularityMetrics      = {}
        self.translationAvailable   = 'f'
        self.watermarked            = 'f'



        pattern = re.compile('CC-MAIN-\d{4}-\d{2}')

        if not pattern.match(_cc_index):
            logging.error(f'Invalid common crawl index format -> {_cc_index}'))

        else:
            self.crawlIndex = _cc_index


    def __repr__(self):
        return f'Provider("{self.name}", "{self.domain}", "{self.crawlIndex}")'


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
        self.metaData               = ''
        self.tags                   = ''
        self.popularityMetrics      = ''
        self.translationAvailable   = None
        self.watermarked            = 'f'


    @property
    def getTags(self):
        maxTags = 20
        if 'tags' in self.metaData:
            self.tags = self.metaData['tags']
            del self.metaData['tags']

            return [{'name': self.sanitizeString(tag), 'provider': self.provider} for tag in list(set(self.tags.split(',')))[:maxTags]]
        else:
            return self.tags


    @property
    def formatOutput(self):
        if self.translationAvailable == True:
            if not self.metaData:
                self.metaData = dict()
            self.metaData['alternate_language_available'] = 't'

        #format the tags
        self.tags       = self.getTags

        if self.metaData:
            self.metaData.update((key, self.sanitizeString(val) if isinstance(val, str) else val) for key,val in self.metaData.items())


        yield [
            self.url if not self.foreignIdentifier else self.foreignIdentifier,
            self.foreignLandingURL if self.foreignLandingURL else '\\N',
            self.url if self.url else '\\N',
            self.thumbnail if self.thumbnail else '\\N',
            int(float(self.width)) if self.width else '\\N',
            int(float(self.height)) if self.height else '\\N',
            self.filesize if self.filesize else '\\N',
            self.license if self.license else '\\N',
            self.licenseVersion if self.licenseVersion else '\\N',
            self.sanitizeString(self.creator) if self.creator else '\\N',
            self.creatorURL if self.creatorURL else '\\N',
            self.sanitizeString(self.title) if self.title else '\\N',
            json.dumps(self.metaData, ensure_ascii=False) if self.metaData else '\\N',
            json.dumps(self.tags, ensure_ascii=False) if self.tags else '\\N',
            #json.dumps(self.popularityMetrics, ensure_ascii=False) if self.popularityMetrics else '\\N',
            self.watermarked,
            self.provider,
            self.source
            ]


    @property
    def input(self):
        if self.crawlIndex is None:
            raise ValueError('Common Crawl index not specified!')

        return f'../../output/{self.crawlIndex}'


    @property
    def output(self):
        if self.crawlIndex is None:
            raise ValueError('Common Crawl index not specified!')

        return f'image_data/{self.crawlIndex}/{self.name.lower()}'


    def getForeignID(self, _str):
        foreignID = re.search('.*?/(\d+)/?$', _str)

        try:
            return foreignID.group(1)
        except:
            logging.error(f'Identifier not detected in: {_str}')
            return None


    def getLicense(self, _domain, _path, _url):

        if 'creativecommons.org' not in _domain:
            logging.warning(f'The license for the following work -> {_url} is not issued by Creative Commons.')
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


    def validateContent(self, _default, _html=None, _property=None):

        if _html:
            return self.sanitizeString(_html.attrs[_property])
        else:
            return _default


    def sanitizeString(self, _data):
        if _data is None:
            return ''

        _data       = _data.strip()
        _data       = _data.replace('"', "'")
        _data       = re.sub(r'\n|\r', ' ', _data)

        backspaces  = re.compile('\b+')
        _data       = backspaces.sub('', _data)
        _data       = _data.replace('\\', '\\\\')

        return re.sub(r'\s+', ' ', _data)


    def getWARCRecord(self, _file, _offset, _length):
        _offset = int(str(_offset))
        _length = int(str(_length))
        _file   = str(_file)

        rnge    = f'bytes={_offset}-{(_offset + _length - 1)}'
        uri     = f'https://commoncrawl.s3.amazonaws.com/{_file}'

        try:
            response    = requests.get(uri, headers={'Range': rnge})
            content     = BytesIO(response.content)
            fh          = gzip.GzipFile(fileobj=content)

            return fh.read()

        except (IOError, Exception) as e:
            logging.error(f'{type(e).__name__}: {e}')
            return None


    def getData(self):
        spk         = SparkSession.builder.getOrCreate()
        dataDF      = spk.read.parquet(self.input)
        providerDF  = dataDF.select(concat(concat('provider_domain', 'content_path'), \
                            when(col('content_query_string') != '', concat(lit('?'), col('content_query_string')))\
                            .otherwise(lit(''))).alias('url'), \
                            concat('warc_segment', lit('/warc/'), 'warc_filename').alias('warc_filename'), \
                                     'content_offset', 'deflate_length')\
                            .where(col('provider_domain').like(f'%{self.domain}'))\
                            .dropDuplicates(['url'])

        providerData = providerDF.rdd.map(lambda row: '\t'.join([str(col) for col in row])).collect() #convert dataframe into a list of tab delimited elements

        return providerData


    def filterData(self, _data, _condition=None):

        if _condition:
            data        = filter(lambda x: _condition.lower() in x.split('\t')[0].lower(), _data)
            self.data   = list(data)
        else:
            self.data   = _data

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

        dataDF = _data.toDF(['foreign_identifier', 'foreign_landing_url',
                        'url', 'thumbnail', 'width', 'height', 'filesize', 'license',
                        'license_version', 'creator', 'creator_url', 'title', 'meta_data',
                        'tags', 'watermarked', 'provider', 'source'])

        #remove duplicate image urls
        result = dataDF.dropDuplicates(['provider', 'url'])

        #remove duplicate foreign IDs
        result = result.dropDuplicates(['provider', 'foreign_identifier'])

        #write to file
        result.coalesce(1).write.mode('append').options(sep='\t', quote='').csv(self.output)


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

        logging.basicConfig(format='%(asctime)s - %(name)s: [%(levelname)s] =======> %(message)s', level=logging.INFO)

        for row in _iter:
            data        = row.split('\t')
            metaData    = None

            content     = self.getWARCRecord(data[1].strip(), data[2].strip(), data[3].strip())

            if content:
                metaData = self.getMetaData(content.strip(), data[0].strip())

                if metaData:
                    yield metaData
                else:
                    logging.warning(f'Content not found for url: {data[0].strip()}, warc file: {data[1].strip()}, offset: {data[2].strip()}, length: {data[3].strip()}.')

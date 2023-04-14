#Test Cases
#Common Crawl Index: CC-MAIN-2018-13

import unittest
import pyspark
from pyspark.sql import SQLContext
from mock import patch, MagicMock
from archive.ExtractCCLinks import CCLinks
import shutil
import os.path
from io import StringIO
import types


class WarcArchive:
    rec_headers = {}
    content     = {}

    def content_stream(self):
        return StringIO(WarcArchive.content)


#Unit Testing
class Test_CCLinks_v1(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        #initialize class once
        cls.cclinks = CCLinks('CC-MAIN-2018-13', 5)


    def setUp(self):
        self.index          = None
        self.watPaths       = open('tests/sample_wat.paths').read().split()
        self.cclinks.output = 'tests/output/{}/test_parquet'.format(self.cclinks.crawlIndex) #overwrite output directory

        self.warcArchive = WarcArchive()


    def tearDown(self):
        del self.warcArchive

        if os.path.exists(self.cclinks.output):
            shutil.rmtree(self.cclinks.output)


    @classmethod
    def tearDownClass(cls):
        del cls.cclinks


    #successful test - loading the WAT files
    @patch('src.ExtractCCLinks.requests.get')
    @patch('src.ExtractCCLinks.gzip.GzipFile')
    def test_loadWATFile_success(self, mockContents, mockGet):
        self.index                  = 'CC-MAIN-2018-13'
        mockContents.return_value   = open('tests/sample_wat.paths')
        mockGet.return_value        = MagicMock(status_code=200, content='', url=self.cclinks.url)

        response = self.cclinks.loadWATFile()
        mockGet.assert_called_with('https://commoncrawl.s3.amazonaws.com/crawl-data/{}/wat.paths.gz'.format(self.index))
        self.assertEqual(type(response), list)
        self.assertEqual(response, self.watPaths)


    #failure test - trigger the exception handling
    @patch('src.ExtractCCLinks.requests.get')
    @patch('src.ExtractCCLinks.gzip.GzipFile')
    def test_loadWATFile_exception(self, mockContents,  mockGet):
        mockContents.return_value   = ''
        mockGet.return_value        = MagicMock(status_code=200, content='', url=self.cclinks.url)

        self.assertRaises(Exception, self.cclinks.loadWATFile())


    def test_generateParquet(self):
        data = [['ace.uoc.edu',
                '/items/browse',
                'sort_field=added&sort_dir=d&page=19',
                'i.creativecommons.org',
                '/l/by-nc-nd/4.0/88x31.png',
                'crawl-data/CC-MAIN-2018-13/segments/1521257644271.19',
                'CC-MAIN-20180317035630-20180317055630-00001.warc.gz',
                int('9837227'),int('7159'),'{"Images":15,"Links":{}}'
                ],
                ['awoiaf.westeros.org',
                '/index.php',
                'title=Riverrun&action=credits',
                'creativecommons.org',
                '/licenses/by-sa/3.0/',
                'crawl-data/CC-MAIN-2018-13/segments/1521257644271.19',
                'CC-MAIN-20180317035630-20180317055630-00001.warc.gz',
                int('29581578'),int('7070'),
                '{"Images":3,"Links":{"www.westeros.org":1,"creativecommons.org":1,"www.mediawiki.org":2}}'
                ]]

        self.cclinks.generateParquet(data)
        self.assertTrue(os.path.exists(self.cclinks.output))

    @patch('src.ExtractCCLinks.boto3')
    @patch('src.ExtractCCLinks.ArchiveIterator')
    def test_processFile_botoParams(self, mockWarcio, mockBoto3):
        self.testKey        = 'crawl-data/CC-MAIN-2018-13/segments/1521257644271.19/wat/CC-MAIN-20180317035630-20180317055630-00006.warc.wat.gz'
        self.mockWarcFiles  = MagicMock()
        self.mockWarcFiles.__iter__.return_value = [self.testKey]

        self.cclinks.processFile(self.mockWarcFiles)

        s3 = mockBoto3.resource('s3')
        s3.meta.client.head_bucket('commoncrawl')
        mockBoto3.resource.assert_called_with('s3') #check s3 connection
        mockBoto3.resource().meta.client.head_bucket.assert_called_with('commoncrawl') #check bucket


    @patch('src.ExtractCCLinks.boto3')
    @patch('src.ExtractCCLinks.requests.get')
    @patch('src.ExtractCCLinks.ArchiveIterator')
    @patch('src.ExtractCCLinks.json.loads')
    def test_processFile_success(self, mockJSON, mockWarcio, mockGet, mockBoto3):
        self.testKey        = 'crawl-data/CC-MAIN-2018-13/segments/1521257644271.19/wat/test_CC-MAIN-20180317035630-20180317055630-00000.warc.wat.gz'
        self.mockWarcFiles  = MagicMock()
        self.mockWarcFiles.__iter__.return_value = [self.testKey]

        jsonData = {'rec_headers':{'Content-Type': 'application/json', 'WARC-Date' : '2014-08-02T09:52:13Z', 'Format' : 'WARC'},
                'content': {'Envelope': {'WARC-Header-Metadata': {'WARC-Type': 'response', 'WARC-Target-URI' : 'http://news.bbc.co.uk/2/hi/africa/3414345.stm'},
                    'Payload-Metadata': {'HTTP-Response-Metadata':
                        {'HTML-Metadata':
                            {'Links' : [
                                {
                                    'url' : 'http://newsimg.bbc.co.uk/nol/shared/img/v3/bbc_logo.gif',
                                    'alt' : 'BBC News',
                                    'path' : 'IMG@/src'
                                },
                                {
                                    'path' : 'A@/href',
                                    'url' : 'http://news.bbc.co.uk/'
                                },
                                {
                                    'path' : 'A@/href',
                                    'url' : 'https://creativecommons.org/publicdomain/zero/1.0/'
                                }]}}}},
                            'Container' : {
                                'Offset' : '213390650',
                                'Filename' : 'CC-MAIN-20140728011800-00009-ip-10-146-231-18.ec2.internal.warc.gz',
                                'Gzip-Metadata' : {
                                    'Footer-Length' : '8',
                                    'Header-Length' : '10',
                                    'Deflate-Length' : '11830'}
                    }}}

        self.warcArchive.rec_headers = jsonData['rec_headers']
        self.warcArchive.content     = jsonData['content']
        mockJSON.return_value        = self.warcArchive.content

        self.warcRecord              = [self.warcArchive]
        mockGet.return_value         = MagicMock(raw=self.warcRecord, url='https://commoncrawl.s3.amazonaws.com/{}'.format(self.testKey))
        mockWarcio.return_value      = self.warcRecord

        self.result = self.cclinks.processFile(self.mockWarcFiles)
        #self.assertTrue(self.result)
        self.assertEqual(type(self.result), types.GeneratorType)


    @patch('src.ExtractCCLinks.boto3')
    @patch('src.ExtractCCLinks.requests.get')
    @patch('src.ExtractCCLinks.ArchiveIterator')
    def test_processFile_invalidContentType(self, mockWarcio, mockGet, mockBoto3):
        self.testKey        = 'crawl-data/CC-MAIN-2018-13/segments/1521257644271.19/wat/CC-MAIN-20180317035630-20180317055630-00011.warc.wat.gz'
        self.mockWarcFiles  = MagicMock()
        self.mockWarcFiles.__iter__.return_value = [self.testKey]

        jsonData = {'rec_headers':{'Content-Type': 'application/http', 'WARC-Date' : '2014-08-02T09:52:13Z', 'Format' : 'WARC'}}

        self.warcArchive.rec_headers = jsonData['rec_headers']
        self.warcRecord              = [self.warcArchive]
        mockGet.return_value         = MagicMock(raw=self.warcRecord, url='https://commoncrawl.s3.amazonaws.com/{}'.format(self.testKey))
        mockWarcio.return_value      = self.warcRecord
        self.result = self.cclinks.processFile(self.mockWarcFiles)
        self.assertFalse(list(self.result))



#Integration Testing
class Test_CCLinks_v2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        #load sample warc files
        fh           = open('tests/sample_wat.paths')
        cls.watPaths = fh.readlines()

        #initialize class
        cls.cclinks = CCLinks('CC-MAIN-2018-13', 5)
        cls.cclinks.output = 'tests/output/{}/parquet'.format(cls.cclinks.crawlIndex)

        #remove output directory
        if os.path.exists(cls.cclinks.output):
            shutil.rmtree('tests/output')

        #init pyspark
        conf   = pyspark.SparkConf().setMaster('local[*]').setAppName('Test_ExtractCCLinks')
        cls.sc = pyspark.SparkContext.getOrCreate(conf=conf)


    @classmethod
    def tearDownClass(cls):
        cls.sc.stop()


    def test_processFlow(self):
        print('Initialize spark process')

        rdd    = self.sc.parallelize(self.watPaths, self.cclinks.numPartitions)
        result = rdd.mapPartitions(self.cclinks.processFile)

        self.cclinks.generateParquet(result)
        result.saveAsTextFile(self.cclinks.output.replace('parquet', 'text')) #write human-readable output


        self.summarizeOutput()

    def summarizeOutput(self):
        s   = SQLContext(self.sc)
        res = s.read.parquet(self.cclinks.output)

        totalLinks  = res.count()
        uniqueContentQuery = res.drop_duplicates(subset=['provider_domain', 'content_path', 'content_query_string']).count()
        uniqueContent = res.drop_duplicates(subset=['provider_domain', 'content_path']).count()


        res.registerTempTable('test_deeds')
        summary = s.sql('SELECT provider_domain, count(*) AS total, count(distinct content_path) AS unique_content_path, count(distinct content_query_string) AS unique_query_string FROM test_deeds GROUP BY provider_domain ORDER BY total DESC LIMIT 100')
        summary.write.mode('overwrite').format('csv').option('header', 'true').save(self.cclinks.output.replace('parquet', 'summary'))

        fh = open('{}/total'.format(self.cclinks.output.replace('parquet', 'summary')), 'w')
        fh.write('Total records: {}\r\n'.format(totalLinks))
        fh.write('Total unique content path: {}\r\n'.format(uniqueContent))
        fh.write('Total unique query strings: {}\r\n'.format(uniqueContentQuery))
        fh.close()


if __name__ == '__main__':
    unittest.main()

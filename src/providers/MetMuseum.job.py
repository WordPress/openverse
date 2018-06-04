"""
Data Transformation: Process the extracted links for the Met Museum.

Identify all licensed content (i.e. images) and their associated meta-data by
scraping the html from Common Crawl's WARC files.
"""
from pyspark import SparkContext
import requests
import StringIO
from bs4 import BeautifulSoup
import re
import gzip
import json
from urlparse import urlparse
from CCMods import *


class MetMuseum:
    logging.getLogger('MetMuseumJob')
    logging.basicConfig(format='%(asctime)s: [%(levelname)s - MetMuseumJob] =======> %(message)s', level=logging.INFO)


    def __init__(self, _cc_index):
        """
        Initialize the Met Museum job by validating the common crawl index parameter.

        Parameters
        ------------------
        _CC_index: string
            The common crawl index


        Returns
        ------------------
        None

        """

        self.crawlIndex = None
        pattern         = re.compile('CC-MAIN-\d{4}-\d{2}')

        if not pattern.match(_cc_index):
            logging.error('Invalid common crawl index format.')

        else:
            self.crawlIndex = _cc_index

        self.input  = '../output/{}'.format(self.crawlIndex)
        self.output = 'transformed/{}.met'.format(self.crawlIndex)


    def getTombstone(self, _html, _url):
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

        soup                = BeautifulSoup (_html, 'html.parser')
        tombstone           = {}
        src                 = None
        license             = None
        version             = None


        try:
            src = [anchor['href'] for anchor in soup.find_all('a', href=True) if 'creativecommons.org' in anchor['href']]

            if src:
                ccInfo              = urlparse(src[0])
                license, version    = getLicense(ccInfo.path)

            else:
                logging.warning('License not detected in url: {}'.format(_url))
                return None

            imgs                = soup.find_all(attrs = {'ng-src': True})
            tombstone['image']  = re.search("(?P<url>https?://[^\s]+)", imgs[0]['ng-src']).group("url").replace("')}}", "")

        except Exception as e:
            logging.warning('{}:{} in url:{}'.format(type(e).__name__, e, _url))

            return None

        else:
            tombstone['title'] = soup.select("h1.collection-details__object-title")[0].string

            x = soup.select(".collection-details__tombstone")[0]
            for row in x.find_all("dl"):
                try:
                    val = row.select(".collection-details__tombstone--value")[0].text.encode('unicode-escape')
                    key = row.select(".collection-details__tombstone--label")[0].text.lower().replace (":", "").replace(" " ,"_")

                    tombstone[key] = val

                except Exception as ex:
                    logging.warning('{}:{} in url:{}'.format(type(ex).__name__, ex, _url))

            try:
                desc    = soup.select('div.collection-details__label')[0].string
                details = soup.select('div.collection_details__facets')

            except Exception as ex2:
                logging.warning('{}:{} in url:{}'.format(type(ex2).__name__, ex2, _url))

            else:
                if desc:
                    tombstone['description'] = desc.encode('unicode-escape').strip()

                for item in details:
                    lbl = item.select('label')[0].string
                    lbl = re.sub('(\s\/\s)|(\s+)', '_', lbl).lower()
                    obj = item.select('a')
                    obj = [re.sub('\(.*?\)', '', i.text) for i in obj]
                    obj = ','.join([str(o.encode('unicode-escape')).strip() for o in obj])
                    tombstone[lbl] = obj

            foreign_id = re.search('.*?/(\d+)/?$', _url)

            try:
                foreign_id = foreign_id.group(1)
            except:
                logging.error('Identifier not detected in url: {}'.format(_url))
                return None

            provider    = 'metmuseum'
            source      = 'commoncrawl'
            imageURL    = ' '
            creator     = ' '
            title       = ' '
            url         = soup.find('meta', {'property': 'og:url'})

            if url:
                url = url.attrs['content']
            else:
                url = _url

            if 'image' in tombstone:
                imageURL = tombstone['image'].encode('unicode-escape')
                del tombstone['image']

            if 'artist_maker_culture' in tombstone:
                creator = tombstone['artist_maker_culture']
                del tombstone['artist_maker_culture']

            if 'title' in tombstone and tombstone['title'] is not None:
                title = tombstone['title'].encode('unicode-escape')
                del tombstone['title']


            return '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(provider, source, foreign_id, url, imageURL, license, version, creator, title, json.dumps(tombstone))


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

            content     = getWARCRecord(data[1].strip(), data[2].strip(), data[3].strip())

            if content:
                metaData = self.getTombstone(content.strip(), data[0].strip())

                if metaData:
                    yield metaData


def main():
    if len(sys.argv) < 2:
        logging.error('Invalid arguments provided.')
        logging.error('Provide the common crawl index.')
        sys.exit()

    args        = sys.argv[1]
    crawlIndex  = args.strip()

    met = MetMuseum(crawlIndex.upper())


    if met.crawlIndex is None:
        sys.exit()

    sc   = SparkContext(appName='Met Museum Job')

    #load the data
    data = getProviderData('metmuseum.org', met.input)

    #filter by url to get the collection
    data = filter(lambda x: 'art/collection/' in x.split('\t')[0], data)

    #create RDD
    rdd  = sc.parallelize(data, sc.defaultParallelism)

    #begin spark process
    rdd.mapPartitions(met.extractHTML).saveAsTextFile(met.output)
    sc.stop()


if __name__ == '__main__':
    main()

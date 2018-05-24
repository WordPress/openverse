"""
Data Transformation: Phase 2 - Process the extracted links for the Met Museum.

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

        pattern = re.compile('CC-MAIN-\d{4}-\d{2}')

        if not pattern.match(_cc_index):
            logging.error('Invalid common crawl index format.')
            sys.exit()
        else:
            self.crawlIndex = _cc_index

        self.input  = 'extracted/{}.met'.format(self.crawlIndex)
        self.output = self.input.replace('extracted', 'transformed')


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
        tombstone['source'] = _url
        domain              = None
        src                 = None
        license             = None
        version             = None


        try:
            src = [anchor['href'] for anchor in soup.find_all('a', href=True) if 'creativecommons.org' in anchor['href']]

        except Exception as e:
            logging.warning('No hyperlink(s) to Creative Commons.')
            logging.warning('{}:{}'.format(type(e).__name__, e))

            return None

        else:

            if src:
                ccInfo                  = urlparse(src[0])
                license, version        = getLicense(ccInfo.path)

            else:
                logging.warning('License not detected in url: {}'.format(_url))
                return None

            imgs               = soup.find_all(attrs = {'ng-src': True})
            tombstone['image'] = re.search("(?P<url>https?://[^\s]+)", imgs[0]['ng-src']).group("url").replace("')}}", "")
            tombstone['title'] = soup.select("h1.collection-details__object-title")[0].string.encode('unicode-escape')

            x = soup.select(".collection-details__tombstone")[0]
            for row in x.find_all("dl"):
                try:
                    val = row.select(".collection-details__tombstone--value")[0].text.encode('unicode-escape')
                    key = row.select(".collection-details__tombstone--label")[0].text.lower().replace (":", "").replace(" " ,"_")

                    tombstone[key] = val

                except Exception as ex:
                    logging.warning('{}:{}'.format(type(ex).__name__, ex))

            try:
                desc    = soup.select('div.collection-details__label')[0].string
                details = soup.select('div.collection_details__facets')

            except Exception as ex2:
                logging.warning('{}:{}'.format(type(ex2).__name__, ex2))

            else:
                if desc:
                    tombstone['description'] = desc.strip().encode('unicode-escape')

                for item in details:
                    lbl = item.select('label')[0].string
                    lbl = re.sub('(\s\/\s)|(\s+)', '_', lbl).lower()
                    obj = item.select('a')
                    obj = [re.sub('\(.*?\)', '', i.text.encode('unicode-escape')) for i in obj]
                    obj = ','.join([str(o).strip() for o in obj])
                    tombstone[lbl] = obj

            foreign_id = re.search('.*?/(\d+)/?$', _url)

            try:
                foreign_id = foreign_id.group(1)
            except:
                logging.error('Identifier not detected in url: {}'.format(_url))
                return None

            provider    = 'metmuseum'
            source      = 'commoncrawl'
            imageURL    = tombstone['image']
            creator     = tombstone['artist_maker_culture']
            title       = tombstone['title']


            del tombstone['image']
            del tombstone['artist_maker_culture']
            del tombstone['title']


            return '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(provider, source, foreign_id, _url, imageURL, license, version, creator, title, json.dumps(tombstone))


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

            content  = getWARCRecord(data[1].strip(), data[2].strip(), data[3].strip())

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

    sc  = SparkContext(appName='Met Museum Job')
    rdd = sc.textFile(met.input, sc.defaultParallelism)
    rdd.mapPartitions(met.extractHTML).saveAsTextFile(met.output)
    sc.stop()


if __name__ == '__main__':
    main()

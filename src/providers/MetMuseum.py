"""
Data Transformation: Process the extracted links for the Met Museum.

Identify all licensed content (i.e. images) and their associated meta-data by
scraping the html from Common Crawl's WARC files.
"""
from Provider import Provider
import requests
from bs4 import BeautifulSoup
from urlparse import urlparse
import logging
import sys
import re


logging.basicConfig(format='%(asctime)s - %(name)s: [%(levelname)s] =======> %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class MetMuseum(Provider):

    def __init__(self, _name, _domain, _cc_index):
        Provider.__init__(self, _name, _domain, _cc_index)


    def getMetaData(self, _html, _url):
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

        self.clearFields()

        try:
            src = [anchor['href'] for anchor in soup.find_all('a', href=True) if 'creativecommons.org' in anchor['href']]

            if src:
                ccInfo                                  = urlparse(src[0])
                license, version                        = self.getLicense(ccInfo.netloc, ccInfo.path, _url)
                self.license        = license
                self.licenseVersion = version

            else:
                logger.warning('License not detected in url: {}'.format(_url))
                return None


            collectionImage = soup.find('a', attrs={'name': '#collectionImage'})
            if collectionImage:
                img         = collectionImage.findChild('img')

                if img:
                    if 'ng-src' in img.attrs:
                        imageURL = re.search("currImage.selectedOrDefaultPreview\('(.*?)'\)", img.attrs['ng-src']).group(1).encode('unicode-escape')
                    else:
                        imageURL = self.validateContent('', img, 'src')

                    self.url                        = imageURL
                    tombstone['image_alt_text']     = self.validateContent('', img, 'alt')
                    thumbnail                       = imageURL.replace('/web-large/', '/web-additional/')
                    self.thumbnail                  = thumbnail

            else:
                logger.warning('Image not detected in url: {}'.format(_url))
                return None


        except Exception as e:
            logger.warning('{}:{} in url:{}'.format(type(e).__name__, e, _url))

            return None

        else:
            clsPrefix  = ''
            #check the prefix for the html class
            if soup.select('div[class^=collection-details__]'):
                clsPrefix = 'collection-details__'

            elif soup.select('div[class^=artwork__]'):
                clsPrefix = 'artwork__'

            else:
                logger.warning('Schema change detected => provider:{} url:{}'.format(self.name, _url))
                return None


            tombstone['title'] = soup.select('h1.{}object-title'.format(clsPrefix))[0].string

            x = soup.select('.{}tombstone'.format(clsPrefix))[0]
            for row in x.find_all("dl"):
                try:
                    val = row.select('.{}tombstone--value'.format(clsPrefix))[0].text.strip().encode('unicode-escape')
                    key = row.select('.{}tombstone--label'.format(clsPrefix))[0].text.lower().replace (':', '').replace(' ' ,'_').strip().encode('unicode-escape')

                    tombstone[key] = val

                except Exception as ex:
                    logger.warning('{}:{} in url:{}'.format(type(ex).__name__, ex, _url))

            try:
                desc    = soup.select('div.{}label'.format(clsPrefix))[0]
                details = soup.select('div.{}facets'.format(clsPrefix))

            except Exception as ex2:
                logger.warning('{}:{} in url:{}'.format(type(ex2).__name__, ex2, _url))

            else:
                if desc and desc.text.strip():
                    tombstone['description'] = desc.text.strip().encode('unicode-escape')

                for item in details:
                    lbl = item.select('label')[0].string
                    lbl = re.sub('(\s\/\s)|(\s+)', '_', lbl).lower().strip().encode('unicode-escape')
                    obj = item.select('a')
                    obj = [re.sub('\(.*?\)', '', i.text) for i in obj]
                    obj = ','.join([str(o.encode('unicode-escape')).strip() for o in obj])
                    tombstone[lbl] = obj


            self.foreignLandingURL  = self.validateContent(_url, soup.find('meta', {'property': 'og:url'}), 'content')
            foreignID               = self.getForeignID(self.foreignLandingURL)

            if foreignID:
                self.foreignIdentifier = foreignID.strip()
            else:
                logger.warning('Identifier not detected in: {}'.format(_url))
                return None


            if 'artist_maker_culture' in tombstone:
                self.creator = tombstone['artist_maker_culture'].strip().encode('unicode-escape')
                del tombstone['artist_maker_culture']

            if 'title' in tombstone and tombstone['title'] is not None:
                self.title = tombstone['title'].strip().encode('unicode-escape')
                del tombstone['title']


            if tombstone:
                self.metaData = tombstone


            self.provider  = self.name
            self.source    = 'commoncrawl'


            return self.formatOutput()


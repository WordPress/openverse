"""
Content Provider:       The Metropolitan Museum of Art

ETL Process:            Identify all public domain artworks, in the Met collection,
                        by scraping the html from Common Crawl's WARC files.

Output:                 TSV file containing images of artworks and their respective meta-data.
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
        formatted           = None
        extracted           = []

        self.clearFields()

        #identify the license
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


            '''collectionImage = soup.find('a', attrs={'name': '#collectionImage'})
            if collectionImage:
                img         = collectionImage.findChild('img')

                if img:
                    if 'ng-src' in img.attrs:
                        imageURL = re.search("currImage.selectedOrDefaultPreview\('(.*?)'\)", img.attrs['ng-src']).group(1)
                    else:
                        imageURL = self.validateContent('', img, 'src')

                    self.url                        = imageURL
                    tombstone['image_alt_text']     = self.validateContent('', img, 'alt')
                    thumbnail                       = imageURL.replace('/web-large/', '/web-additional/')
                    self.thumbnail                  = thumbnail

            else:
                logger.warning('Image not detected in url: {}'.format(_url))
                return None'''


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


            #get the title
            tombstone['title'] = soup.select('h1.{}object-title'.format(clsPrefix))[0].string

            #get the tombstone data
            x = soup.select('.{}tombstone'.format(clsPrefix))[0]
            for row in x.find_all("dl"):
                try:
                    val = row.select('.{}tombstone--value'.format(clsPrefix))[0].text.strip()
                    key = row.select('.{}tombstone--label'.format(clsPrefix))[0].text.lower().replace (':', '').replace(' ' ,'_').strip()

                    tombstone[key] = val

                except Exception as ex:
                    logger.warning('{}:{} in url:{}'.format(type(ex).__name__, ex, _url))

            desc    = soup.find('div', {'class': '{}label'.format(clsPrefix)})
            details = soup.find_all('div', {'class': '{}facets'.format(clsPrefix)})

            #get the summary/description of the artwork
            if desc and desc.contents[0].strip():
                desc = desc.contents[0].strip()
                tombstone['description'] = desc

            #get the meta data
            for item in details:
                lbl = item.select('label')[0].string
                lbl = re.sub('(\s\/\s)|(\s+)', '_', lbl).lower().strip()
                obj = item.select('a')
                obj = [re.sub('\(.*?\)', '', i.text) for i in obj]
                obj = ','.join([str(o).strip() for o in obj])
                tombstone[lbl] = obj


            #obtain the url from the HTML meta tag or default to common crawl's url
            self.foreignLandingURL  = self.validateContent(_url, soup.find('meta', {'property': 'og:url'}), 'content')
            foreignID               = self.getForeignID(self.foreignLandingURL)

            #extract the foreign identifer
            '''if foreignID:
                self.foreignIdentifier = foreignID.strip()
            else:
                logger.warning('Identifier not detected in: {}'.format(_url))
                return None''' #the foreign ID will be the image url


            if 'artist' in tombstone:
                self.creator = tombstone['artist'].strip()
                del tombstone['artist']

            if 'title' in tombstone and tombstone['title'] is not None:
                self.title = tombstone['title'].strip()
                del tombstone['title']


            self.provider   = self.name
            self.source     = 'commoncrawl'


            #get the images and thumbnails
            images = soup.find_all('img', {'class': 'met-carousel__item__thumbnail'})
            if not images:
                images = soup.find_all('img', {'id': '{}image'.format(clsPrefix)})
            if images:
                for img in images:
                    self.thumbnail  = ''
                    self.url        = ''
                    self.metaData   = {}

                    if img:
                        if len(images) == 1:
                            if 'src' in img.attrs:
                                imageURL = self.validateContent('', img, 'src')
                                self.url = imageURL

                                if '/web-large/' in imageURL:
                                    self.thumbnail = imageURL.replace('/web-large/', '/web-additional/')

                            if 'alt' in img.attrs:
                                tombstone['image_alt_text'] = self.validateContent('', img, 'alt')

                        else:
                            if 'src' in img.attrs:
                                self.thumbnail = self.validateContent('', img, 'src')

                            if 'data-superjumboimage' in img.attrs:
                                self.url                = self.validateContent('', img, 'data-superjumboimage')
                                self.foreignIdentifier  = self.url

                            if 'alt' in img.attrs:
                                tombstone['image_alt_text'] = self.validateContent('', img, 'alt')

                    else:
                        logger.warning('Image not detected in url: {}'.format(_url))
                        continue


                    if tombstone:
                        self.metaData = tombstone

                    extracted.extend(self.formatOutput)


            return extracted


"""
Content Provider:       IHA Holiday Ads

ETL Process:            Identify images of vacation rentals that are available under a
                        Creative Commons license.

Output:                 TSV file containing images of artworks and their respective meta-data.
"""

from Provider import Provider
import logging
from bs4 import BeautifulSoup
from urlparse import urlparse
import json
import re


logging.basicConfig(format='%(asctime)s - %(name)s: [%(levelname)s] =======> %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class IHA(Provider):

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

        soup                = BeautifulSoup(_html, 'html.parser') #NB: the HTML for this website has been updated (the common crawl data is not the most recent version)
        otherMetaData       = {}
        src                 = None
        license             = None
        version             = None
        imageURL            = None
        tags                = None
        extracted           = []



        slider = soup.find('div', {'class': 'ph'})
        if slider:
            content = slider.find_all('span', {'class': 'swiper-slide'})
            for imageData in content:
                self.clearFields()

                self.watermarked            = 't'
                self.translationAvailable   = True
                self.provider               = self.name
                self.source                 = 'commoncrawl'

                foreign_url     = soup.find('meta', {'property': 'og:url'})
                if foreign_url:
                    self.foreignLandingURL = self.validateContent(_url, foreign_url, 'content')


                #get the license
                licenseInfo = imageData.find('a', {'rel': 'license', 'href': True})
                if licenseInfo:
                    ccURL               = urlparse(licenseInfo.attrs['href'].strip())
                    license, version    = self.getLicense(ccURL.netloc, ccURL.path, _url)

                    if not license:
                        logger.warning('License not detected in url: {}'.format(_url))
                        continue

                    self.license          = license
                    self.licenseVersion   = version


                #get the image
                image = imageData.findChild('img')
                if image:
                    self.thumbnail                  = self.validateContent('', image, 'src')
                    self.metaData['image_alt_text'] = self.validateContent('', image, 'alt')
                    self.width                      = self.validateContent('', image, 'width')
                    self.height                     = self.validateContent('', image, 'height')
                    self.title                      = self.validateContent('', image, 'title')


                if 'about' in imageData.attrs:
                    self.url = imageData.attrs['about'].strip().encode('unicode-escape')

                    if self.url == '':
                        logger.warning('Image not detected in url: {}'.format(_url))
                        continue

                #get the attribution info
                author = imageData.find('span', {'class': 'auth'})
                if author:
                    self.creator = author.text.strip().encode('unicode-escape').replace('\\xa9', '').strip()


                tags = soup.find('meta', {'name': 'keywords'})
                if tags:
                    self.metaData['tags']   = self.validateContent('', tags, 'content')


                extracted.extend(self.formatOutput)

        return extracted



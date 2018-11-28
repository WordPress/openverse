"""
Content Provider:       DeviantArt

ETL Process:            Identify the various artworks that are
                        available under a Creative Commons license.

Output:                 TSV file containing images of artworks and their respective meta-data.
"""
from Provider import Provider
import logging
from bs4 import BeautifulSoup
from urlparse import urlparse
import re


logging.basicConfig(format='%(asctime)s - %(name)s: [%(levelname)s] =======> %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class DeviantArt(Provider):

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

        soup                = BeautifulSoup(_html, 'html.parser')
        otherMetaData       = {}
        license             = None
        version             = None
        imageURL            = None
        formatted           = None

        self.clearFields()

        #verify the license
        licenseInfo = soup.find('a', {'rel': 'license', 'href': True})
        if licenseInfo:
            ccURL               = urlparse(licenseInfo.attrs['href'].strip())
            license, version    = self.getLicense(ccURL.netloc, ccURL.path, _url)

            if not license:
                logger.warning('License not detected in url: {}'.format(_url))
                return None

            self.license          = license
            self.licenseVersion   = version


            #locate the image
            imgProperty = soup.find('meta', {'property': 'og:image'})
            if imgProperty:
                imageURL    = self.validateContent('', imgProperty, 'content')
                if 'main/logo/card_black_large.png' in imageURL:
                    logger.info('Image not available. Image url: {}'.format(_url))
                    return None

                imgWidth    = self.validateContent('', soup.find('meta', {'property': 'og:image:width'}), 'content')
                imgHeight   = self.validateContent('', soup.find('meta', {'property': 'og:image:height'}), 'content')

                self.url        = imageURL
                self.width      = imgWidth
                self.height     = imgHeight
            else:
                logger.warning('Image not detected in url: {}'.format(_url))
                return None


            #get the title
            self.title = self.validateContent('', soup.find('meta', {'property': 'og:title'}), 'content')

            #creator
            creator = soup.find('a', {'class':'u regular username', 'href':True})
            if creator:
                self.creatorURL = self.validateContent('', creator, 'href')
                self.creator    = creator.text.strip()


            #description
            description = soup.find('div', {'class': 'text block'})
            if description and description.text.strip():
                otherMetaData['description'] = description.text.strip()


            self.foreignLandingURL = self.validateContent(_url, soup.find('meta', {'property': 'og:url'}), 'content')

            foreignID = soup.find('div', {'class':'dev-page-view view-mode-normal'})
            if foreignID:
                self.foreignIdentifier = foreignID.attrs['gmi-deviationid'].strip()
            else:
                logger.warning('Identifier not detected in: {}'.format(_url))
                return None

            self.provider   = self.name
            self.source     = 'commoncrawl'

            if otherMetaData:
                self.metaData   = otherMetaData


            formatted = list(self.formatOutput)

            return formatted


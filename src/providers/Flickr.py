"""
Content Provider:       Flickr

ETL Process:            Identify all images that are available under a Creative
                        Commons license.

Output:                 TSV file containing images of artworks and their respective meta-data.
"""

from Provider import Provider
import logging
from bs4 import BeautifulSoup
from urlparse import urlparse
import re


logging.basicConfig(format='%(asctime)s - %(name)s: [%(levelname)s] =======> %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class Flickr(Provider):

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
        formatted           = []

        self.clearFields()

        #verify license
        licenseInfo = soup.find('a', {'class': 'photo-license-url', 'href': True})
        if licenseInfo:
            ccURL               = urlparse(licenseInfo.attrs['href'].strip())
            license, version    = self.getLicense(ccURL.netloc, ccURL.path, _url)

            if not license:
                logger.warning('License not detected in url: {}'.format(_url))
                return None

            self.license            = license
            self.licenseVersion     = version


            #get the image
            imgProperty = soup.find('meta', {'property': 'og:image'})
            if imgProperty:
                imageURL    = self.validateContent('', imgProperty, 'content')
                if 's.yimg.com/pw/images/photo_unavailable_copyright.gif' in imageURL:
                    logger.info('Image has been removed due to a claim of copyright / IP infringement. Image url: {}'.format(_url))
                    return None

                imgWidth    = self.validateContent('', soup.find('meta', {'property': 'og:image:width'}), 'content')
                imgHeight   = self.validateContent('', soup.find('meta', {'property': 'og:image:height'}), 'content')

                self.url       = imageURL
                self.width     = imgWidth
                self.height    = imgHeight
            else:
                logger.warning('Image not detected in url: {}'.format(_url))
                return None


            #Title
            self.title = self.validateContent('', soup.find('meta', {'property': 'og:title'}), 'content')


            self.foreignLandingURL  = self.validateContent(_url, soup.find('meta', {'property': 'og:url'}), 'content')
            foreignID               = self.getForeignID(self.foreignLandingURL)

            if foreignID:
                self.foreignIdentifier = foreignID.strip()
            else:
                logger.warning('Identifier not detected in: {}'.format(_url))
                return None


            #additional meta data
            photoMeta = soup.find_all('meta', {'property': re.compile('^flickr_photos:.*?')})

            for pMeta in photoMeta:
                key                 = pMeta.attrs['property'].replace('flickr_photos:', '').replace(':', '_').lower()
                otherMetaData[key]  = pMeta.attrs['content'].strip().encode('unicode-escape')


            #creator info
            owner           = soup.find('a', {'class': 'owner-name truncate'})
            self.creator    = owner.string.strip().encode('unicode-escape')

            if otherMetaData['by']:
                self.creatorURL = otherMetaData['by']
                del otherMetaData['by']

            #description
            desc     = soup.find('h2', {'class': ' meta-field photo-desc '})
            if desc:
                info = desc.find_all('p')
                res  = ' '.join([x.text for x in info])
                res  = re.sub('\s+', ' ', res.encode('unicode-escape'))

                otherMetaData['description'] = res


            keywords            = soup.find('meta', {'name': 'keywords'})
            if keywords:
                otherMetaData['tags']   = keywords.attrs['content'].strip().encode('unicode-escape')


            self.provider  = self.name
            self.source    = 'commoncrawl'

            if otherMetaData:
                self.metaData = otherMetaData


            formatted = list(self.formatOutput)

            return formatted


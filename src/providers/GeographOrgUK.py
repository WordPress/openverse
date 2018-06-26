from Provider import Provider
import logging
from bs4 import BeautifulSoup
from urlparse import urlparse
import re


logging.basicConfig(format='%(asctime)s - %(name)s: [%(levelname)s] =======> %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class GeographOrgUK(Provider):

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

        self.clearFields()

        licenseInfo = soup.find('a', {'rel': 'license', 'href': True})
        if licenseInfo:
            ccURL               = urlparse(licenseInfo.attrs['href'].strip())
            license, version    = self.getLicense(ccURL.netloc, ccURL.path, _url)

            if not license:
                logger.warning('License not detected in url: {}'.format(_url))
                return None

            self.license            = license
            self.licenseVersion     = version

            #get the image
            mainImage = soup.find('div', {'id': 'mainphoto'})
            if mainImage:
                imgSRC                          = mainImage.findChild('img')
                imageURL                        = self.validateContent('', imgSRC, 'src')
                imgWidth                        = self.validateContent('', imgSRC, 'width')
                imgHeight                       = self.validateContent('', imgSRC, 'height')

                self.url       = imageURL
                self.width     = imgWidth
                self.height    = imgHeight

            else:
                logger.warning('Image not detected in url: {}'.format(_url))
                return None


            #get the title
            title = soup.find('strong', {'property': 'dct:title'})
            if title:
                self.title = title.text.strip().encode('unicode-escape')


            #Creator
            creatorInfo = soup.find('a', {'rel': 'author', 'href': True})
            if creatorInfo:
                self.creator        = creatorInfo.text.strip().encode('unicode-escape')
                self.creatorURL     = '{}{}'.format(self.domain, creatorInfo.attrs['href'])


            #Keywords/tags
            tagInfo = soup.find_all('span', {'class': 'tag'})
            if tagInfo:
                tags                    = ','.join(tag.text.strip().encode('unicode-escape') for tag in tagInfo)
                otherMetaData['tags']   = tags


            #get geographic location
            latitude    = self.validateContent(None, soup.find('abbr', {'class': 'latitude'}), 'title')
            longitude   = self.validateContent(None, soup.find('abbr', {'class': 'longitude'}), 'title')
            if latitude and longitude:
                otherMetaData['latitude']   = latitude
                otherMetaData['longitude']  = longitude


            #date taken
            exifData = soup.find('span', {'itemprop': 'exifData'})
            if exifData:
                otherMetaData['date_taken'] = exifData.text.strip().encode('unicode-escape')


            #description/caption
            caption = soup.find('div', {'itemprop': 'description'})
            if caption:
                otherMetaData['description'] = caption.text.strip().encode('unicode-escape')


            self.foreignLandingURL = self.validateContent(_url, soup.find('link', {'rel': 'canonical', 'href': True}), 'href')

            foreignID = self.getForeignID(self.foreignLandingURL)

            if foreignID:
                self.foreignIdentifier = foreignID.strip()
            else:
                logger.warning('Identifier not detected in: {}'.format(_url))
                return None


            self.provider  = self.name
            self.source    = 'commoncrawl'

            if otherMetaData:
                self.metaData = otherMetaData


            return self.formatOutput()


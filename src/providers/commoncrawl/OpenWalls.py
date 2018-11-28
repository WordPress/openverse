"""
Content Provider:       Open Walls

ETL Process:            N/A

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


class OpenWalls(Provider):

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
        src                 = None
        license             = None
        version             = None
        imageURL            = None
        formatted           = None

        self.clearFields()
        self.watermarked = 't'

        imageDetails = soup.find_all('div', {'class': 'view_image_row'})
        if imageDetails:
            for row in imageDetails:

                key = row.find('div', {'class': 'view_image_info_edit_left'})
                key = key.text.strip().encode('unicode-escape').lower()

                if key[len(key)-1] == ':':
                    key = key.replace(':', '')
                    key = key.replace(' ', '_')

                if key == 'licence':
                    val                 = row.find('a', {'href': True})
                    ccURL               = urlparse(val.attrs['href'].strip())
                    license, version    = self.getLicense(ccURL.netloc, ccURL.path, _url)


                    if not license:
                        logger.warning('License not detected in url: {}'.format(_url))
                        return None

                    self.license            = license
                    self.licenseVersion     = version
                    continue

                else:

                    val = row.find('div', {'class': 'view_image_info_edit_right'})
                    val = val.text.strip()

                    if key == 'title':
                        self.title = val
                        continue

                    elif key == 'uploader':
                        #creator info
                        self.creator = re.sub('\(.*?\)', '', val)
                        continue

                    elif key == 'tags':
                        val = re.sub('\n', ',', val)


                otherMetaData[key] = val.encode('unicode-escape')

        imgContent = soup.find_all('div', {'class': 'view_image_info_save_resolution'})
        if imgContent and (len(imgContent) > 1):
            imgSRC  = imgContent[1].findChild('a')
            img     = imgSRC.attrs['href'].strip().encode('unicode-escape')

            if img:
                self.url                = '{}{}'.format(self.domain, img)
                self.width, self.height = [x for x in imgSRC.text.strip().split('x')]

                if not (self.width.isdigit() and self.height.isdigit()):
                    self.width  = ''
                    self.height = ''

        if self.url == '':
            logger.warning('Image not detected in url: {}'.format(_url))
            return None


        imageID = soup.find('form', {'name': 'delete'})

        if imageID:
            foreignID               = imageID['action'].strip().split('?id=')[1]
            self.foreignIdentifier  = foreignID


        description = soup.find('meta', {'name': 'description'})
        if description:
            description                  = description['content'].strip().encode('unicode-escape')
            otherMetaData['description'] = description


        if 'website' in otherMetaData:
            self.creatorURL = otherMetaData['website']
            del otherMetaData['website']


        self.foreignLandingURL              = _url
        self.provider                       = self.name
        self.source                         = 'commoncrawl'

        if otherMetaData:
            self.metaData   = otherMetaData


        formatted = list(self.formatOutput)

        return formatted


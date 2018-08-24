"""
Content Provider:       Soft Icons

ETL Process:            Identify all icons and icon sets that are available under a
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

class SoftIcons(Provider):

    def __init__(self, _name, _domain, _cc_index):
        Provider.__init__(self, _name, _domain, _cc_index)


    def filterData(self, _data):
        #filter data to obtain the icon set.
        data    = filter(lambda x: len(x.split('\t')[0].split('/')) == 3, _data) #format domain/content path/ user set
        self.data = data

        return self.data


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
        extracted           = []


        self.clearFields()

        details = soup.find('table', {'class': 'collection_desc'})
        if details:
            details = details.find_all('tr')

            for row in details:
                cols = row.findChildren('td')

                if cols[0].text.strip().lower().encode('unicode-escape') == 'author:':
                    authorInfo = cols[1].find('a')
                    if authorInfo:
                        self.creatorURL = '{}{}'.format(self.domain, authorInfo.attrs['href']).encode('unicode-escape')
                        self.creator    = authorInfo.attrs['href'].split('/')[2].encode('unicode-escape')

                elif cols[0].text.strip().lower().encode('unicode-escape') == 'license:':
                    licenseInfo         = cols[1].find('a')
                    ccURL               = urlparse(licenseInfo.attrs['href'].strip())
                    license, version    = self.getLicense(ccURL.netloc, ccURL.path, _url)

                    if not license:
                        logger.warning('License not detected in url: {}'.format(_url))
                        return None

                    self.license            = license
                    self.licenseVersion     = version

            #get the icon sets
            iconSet = soup.find('table', {'class': 'icon_img_text'}).find_all('td', {'class': 'icon_logo'})
            for icon in iconSet:
                self.foreignLandingURL  = ''
                self.url                = ''
                self.title              = ''
                self.width              = ''
                self.height             = ''
                self.metaData           = {}
                self.provider           = self.name
                self.source             = 'commoncrawl'

                iconInfo = icon.findChild('a')
                if iconInfo:
                    self.foreignLandingURL = '{}{}'.format(self.domain, self.validateContent('', iconInfo, 'href'))

                imageInfo = iconInfo.findChild('img')
                if imageInfo:
                    self.url                        = self.validateContent('', imageInfo, 'src')
                    self.title                      = self.validateContent('', imageInfo, 'title')
                    self.width                      = self.validateContent('', imageInfo, 'width')
                    self.height                     = self.validateContent('', imageInfo, 'height')
                    self.metaData['image_alt_text'] = self.validateContent('', imageInfo, 'alt')

                self.metaData['icon_set'] = _url
                if self.url == '':
                    logger.warning('Image not detected in url: {}'.format(_url))
                    continue

                #description
                description = soup.find('meta', {'name': 'description'})
                if description:
                    self.metaData['description'] = self.validateContent('', description, 'content')


                #keywords
                keywords = soup.find('meta', {'name': 'keywords'})
                if keywords:
                    self.metaData['keywords'] = self.validateContent('', keywords, 'content')


                extracted.extend(self.formatOutput)

            return extracted

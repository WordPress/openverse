"""
Content Provider:       Icon Finder

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


class IconFinder(Provider):

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

        self.clearFields()

        details = soup.find('section', {'class': 'iconset-details-list'})
        if details:
            details = details.find('table')
        else:
            return None

        if details:
            details = details.find_all('tr')

            for row in details:
                cols = row.findChildren('td')

                #verify the license
                if cols[0].text.strip().lower().encode('unicode-escape') == 'license:':
                    licenseInfo         = cols[1].find('a')
                    ccURL               = urlparse(licenseInfo.attrs['href'].strip())
                    license, version    = self.getLicense(ccURL.netloc, ccURL.path, _url)

                    if not license:
                        logger.warning('License not detected in url: {}'.format(_url))
                        return None

                    self.license            = license
                    self.licenseVersion     = version

                elif cols[0].text.strip().lower().encode('unicode-escape') == 'category:':
                    categories              = cols[1].find_all('a')
                    tags                    = ','.join([category.text.strip().encode('unicode-escape') for category in categories])


            author = soup.find('meta', {'name': 'author'})
            if author:
                self.creator = self.validateContent('', author, 'content')

            authorURL = soup.find('span', {'class': 'author-title'})
            if authorURL:
                authorURL       = authorURL.find('a', {'href': True})
                self.creatorURL = authorURL.attrs['href']

                if self.creatorURL[0] == '/':
                    self.creatorURL = '{}{}'.format(self.domain, self.creatorURL)


            #get the icon set
            iconSet = soup.find_all('a', {'class': 'iconlink'})
            for icon in iconSet:
                self.foreignLandingURL  = ''
                self.foreignIdentifier  = ''
                self.url                = ''
                self.title              = ''
                self.width              = ''
                self.height             = ''
                self.metaData           = {}
                self.provider           = self.name
                self.source             = 'commoncrawl'

                link                    = self.validateContent('', icon, 'href')
                href                    = link.split('#')
                self.foreignLandingURL  = '{}{}'.format(self.domain, href[0])

                imageID = link.split('/')
                if imageID and len(imageID) > 3:
                    self.foreignIdentifier = imageID[2]

                #image title
                title = self.validateContent('', icon, 'title')
                if title:
                    self.title = title

                #iconset url
                iconset = soup.find('meta', {'property': 'og:url'})
                if iconset:
                    self.metaData['icon_set'] = self.validateContent(_url, iconset, 'content')


                if len(href) > 1:
                    dimensions              = href[1].split('=')

                    if dimensions and len(dimensions) > 1:
                        self.width          = dimensions[1]
                        self.height         = dimensions[1]
                    self.title              = self.validateContent('', icon, 'title')

                imageInfo = icon.findChild('img')
                if imageInfo:
                    self.url = self.validateContent('', imageInfo, 'src')

                    if self.url == '':
                        logger.warning('Image not detected in url: {}'.format(_url))
                        continue

                    self.metaData['image_alt_text'] = self.validateContent('', imageInfo, 'alt')


                #tags/keywords
                if tags:
                    self.metaData['tags']   = tags


                extracted.extend(self.formatOutput)

        return extracted



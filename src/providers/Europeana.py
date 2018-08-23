"""
Content Provider:       Europeana (G.L.A.M.)

ETL Process:            Identify artworks that are available under a Creative
                        Commons license or in the public domain.

Output:                 TSV file containing images of artworks and their respective meta-data.
"""

from Provider import Provider
import logging
from bs4 import BeautifulSoup
from urlparse import urlparse
import urllib2
import json
import re


logging.basicConfig(format='%(asctime)s - %(name)s: [%(levelname)s] =======> %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class Europeana(Provider):

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
        tags                = None
        extracted           = []

        self.clearFields()

        #get galleries, record, exhibitions
        if '/galleries/' in _url:

            gallery = soup.find_all('div', {'class': 'masonry-item'})
            for item in gallery:
                self.clearFields()
                self.translationAvailable   = True
                self.provider               = self.name
                self.source                 = 'commoncrawl'
                license                     = None
                version                     = None


                imageInfo = item.findChild('img')
                if 'data-src' in imageInfo.attrs:
                    tmpDataSrc  = imageInfo.attrs['data-src']
                    #tmpSrc      = imageInfo.attrs['src']
                    if tmpDataSrc:
                        tmpImgSrc = urllib2.unquote(tmpDataSrc).split('&view=') #urllib2.unquote(tmpSrc).split('&uri=')
                        if len(tmpImgSrc) > 1:
                            img         = tmpImgSrc[1]
                            self.url    = img

                    if self.url == '':
                        logger.warning('Image not detected in url: {}'.format(_url))
                        continue


                licenseInfo = item.findChild('a', {'class': 'license'})
                if licenseInfo and 'href' in licenseInfo.attrs:
                    ccURL               = urlparse(licenseInfo.attrs['href'].strip())
                    license, version    = self.getLicense(ccURL.netloc, ccURL.path, _url)

                if not license:
                    logger.warning('License not detected in url: {}'.format(_url))
                    continue

                self.license            = license
                self.licenseVersion     = version


                title = item.findChild('div', {'class': 'image-title'})
                if title:
                    self.title = title.text.strip().encode('unicode-escape')


                creatorInfo = item.findChild('div', {'class': 'image-creator'})
                if creatorInfo:
                    self.creator = creatorInfo.text.strip().encode('unicode-escape')

                gelleryMetaData = item.findChild('div', {'class': 'image-meta'}) #soup.find('meta', {'property': 'og:url'})
                if gelleryMetaData:
                    gelleryMetaData = gelleryMetaData.find_all('span', {'class':'title'})#
                    for meta in gelleryMetaData:
                        if meta.findChild('a'):
                            currentURL = meta.findChild('a')

                            if currentURL:
                                self.foreignLandingURL = self.validateContent('', currentURL, 'href')
                                break

                galleryURL = soup.find('meta', {'property': 'og:url'})
                if galleryURL:
                    self.metaData['set'] = self.validateContent(_url, galleryURL, 'content')

                    if self.foreignLandingURL == '':
                        self.foreignLandingURL = self.metaData['set']

                extracted.extend(self.formatOutput)


        elif '/record/' in _url:
            record = soup.find_all('div', {'class': 'single-item-thumb'})
            if not record:
                record = soup.find_all('div', {'class': 'mlt-img-div height-to-width'})

            licenseInfo = soup.find('div', {'class': 'info-license'})
            if licenseInfo:
                licenseInfo = licenseInfo.findChild('a', {'class': 'license'})
                if 'href' in licenseInfo.attrs:
                    ccURL               = urlparse(licenseInfo.attrs['href'].strip())
                    license, version    = self.getLicense(ccURL.netloc, ccURL.path, _url)

                    if not license:
                        logger.warning('License not detected in url: {}'.format(_url))
                        return None


            title = ''
            titleInfo = soup.find('div', {'class': 'object-title'})
            if titleInfo:
                titleInfo = titleInfo.findChild('h2')
                if titleInfo:
                    title = titleInfo.text.strip().encode('unicode-escape')


            imageMetaData   = soup.find_all('div', {'class': 'data-section cf'})
            tmpMetaData     = {}
            if imageMetaData:
                for meta in imageMetaData:
                    section = meta.findChild('h3')
                    if section and (section.text.strip().encode('unicode-escape').lower().strip() in ['contributors', 'classifications', 'provenance', 'location', 'people']):

                        sectionInfo = meta.findChildren('li')
                        for info in sectionInfo:
                            key = info.find('h4')
                            if key:
                                key = key.text.replace(':', '').strip().encode('unicode-escape').lower().replace(' ', '_')
                                val = info.find('ul').text.strip().encode('unicode-escape')
                                tmpMetaData[key] = val

            if record:

                for rec in record:

                    self.clearFields()
                    self.translationAvailable   = True
                    self.provider               = self.name
                    self.source                 = 'commoncrawl'
                    self.license                = license
                    self.licenseVersion         = version
                    self.title                  = title
                    self.url                    = ''
                    self.width                  = ''
                    self.height                 = ''
                    self.thumbnail              = ''
                    self.foreignLandingURL      = ''
                    self.metaData               = tmpMetaData


                    #description
                    description = soup.find('meta', {'property': 'og:description'})
                    if description and ('content' in description.attrs):
                        self.metaData['description'] = self.validateContent('', description, 'content')


                    #foreign landing URL
                    foreignURL = ''
                    currentURL = soup.find('meta', {'property': 'og:url'})
                    if currentURL:
                        foreignURL = self.validateContent(_url, currentURL, 'content')

                    if foreignURL:
                        if len(record) > 1:
                            self.metaData['set'] = foreignURL

                        else:
                            self.foreignLandingURL  = foreignURL


                    tmpImgInfo = rec.findChild('a')#, {'class': re.compile(r'(.*?external-media.*?)')})
                    if tmpImgInfo:
                        self.foreignLandingURL = _url

                        imgSRC = tmpImgInfo.find('img')
                        tmpURL = ''

                        '''if 'href' in tmpImgInfo.attrs:
                            tmpLinkInfo = tmpImgInfo.attrs['href']
                            print urllib2.unquote(tmpLinkInfo.strip().encode('unicode-escape'))'''

                        '''if imgSRC and 'src' in imgSRC.attrs: #'href' in tmpImgInfo.attrs:
                            tmpURL = imgSRC.attrs['src'].strip().encode('unicode-escape')
                            tmpURL = urllib2.unquote(tmpURL)'''


                        if 'data-uri' in tmpImgInfo.attrs:
                            tmpURL = tmpImgInfo.attrs['data-uri'].strip().encode('unicode-escape')
                            tmpURL = urllib2.unquote(tmpURL)

                        '''if 'data-thumbnail' in tmpImgInfo.attrs:
                            thumbnail = tmpImgInfo.attrs['data-thumbnail'].strip().encode('unicode-escape')
                            thumbnail = urllib2.unquote(thumbnail)'''

                        if 'data-width' in tmpImgInfo.attrs:
                            self.width = tmpImgInfo.attrs['data-width'].strip().encode('unicode-escape')

                        if 'data-height' in tmpImgInfo.attrs:
                            self.height = tmpImgInfo.attrs['data-height'].strip().encode('unicode-escape')


                        if tmpURL:
                            tmpURL = re.split('https?://', tmpURL) #tmpURL.split('uri=')
                            if len(tmpURL) > 1:
                                tmpURL   = tmpURL[len(tmpURL)-1].strip()
                                self.url = tmpURL
                            else:
                                self.url = tmpURL[0]

                            '''if '/attachments/' in self.url:
                                foreignID = self.url.split('/attachments/')[1].lstrip('/')
                                if foreignID:
                                    foreignID               = foreignID.split('/')[0]
                                    self.foreignIdentifier  = foreignID'''


                        if ('show_jpg_image.pl' in self.url) or ('xantho.' in self.url):
                            self.url = ''

                        if self.url == '':
                            logger.warning('Image not detected in url: {}'.format(_url))
                            continue

                        extracted.extend(self.formatOutput)



        return extracted

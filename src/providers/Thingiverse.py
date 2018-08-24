"""
Content Provider:       Thingiverse

ETL Process:            Identify all 3D models that are available under a
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


class Thingiverse(Provider):

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


        #verify license
        licenseInfo = soup.find('a', {'rel': 'license'})
        if licenseInfo:
            ccURL               = urlparse(licenseInfo.attrs['href'].strip())
            license, version    = self.getLicense(ccURL.netloc, ccURL.path, _url)

            if not license:
                logger.warning('License not detected in url: {}'.format(_url))
                return None

            self.license            = license
            self.licenseVersion     = version


            foreignURL = soup.find('meta', {'property': 'og:url'})
            if foreignURL:
                self.foreignLandingURL = self.validateContent(_url, foreignURL, 'content')


            #title
            title = soup.find('span', {'property': 'dc:title'})
            if title:
                self.title = title.text.strip().encode('unicode-escape')


            #creator
            creatorInfo = soup.find('a', {'rel': 'cc:attributionURL'})
            if creatorInfo:
                self.creator    = creatorInfo.text.strip().encode('unicode-escape')
                self.creatorURL = self.validateContent('', creatorInfo, 'href')


            #tags
            tagsList = soup.find('div', {'class': re.compile('(thing-info-content )?thing-detail-tags-container')})
            if tagsList:
                tags                    = tagsList.find_all('a')
                tags                    = ','.join([tag.text.strip().encode('unicode-escape') for tag in tags])
                self.metaData['tags']   = tags


            #remix
            #remix = soup.find_all('div', {'class': 'thumb-list justify justify-left'})
            #if remix:
                #remixedFrom = remix.findChildren('a', {'class': 'plain-link'})



            #description
            description = soup.find('meta', {'name': 'description'})
            if description:
                self.metaData['description'] = self.validateContent('', description, 'content')


            self.provider           = self.name
            self.source             = 'commoncrawl'


            slider = soup.find('span', {'class': 'gallery-slider'})
            if slider is None:
                slider = soup.find('div', {'class': 'thing-slides'})

            if slider:
                slider = slider.findChildren('div')

                if len(list(set(slider))) > 1:
                    self.metaData['set']    = self.foreignLandingURL


                for slide in list(set(slider)):
                    self.url                = ''
                    self.foreignIdentifier  = ''
                    self.thumbnail          = ''

                    if 'data-thumb' in slide.attrs:
                        self.thumbnail = self.validateContent('', slide, 'data-thumb')
                    elif 'data-thumb-url' in slide.attrs:
                        self.thumbnail = self.validateContent('', slide, 'data-thumb-url')


                    if 'data-large' in slide.attrs:
                        self.url = self.validateContent('', slide, 'data-large')

                    elif 'data-large-url' in slide.attrs:
                        self.url = self.validateContent('', slide, 'data-large-url')

                    elif 'data-medium-url' in slide.attrs:
                        self.url = self.validateContent('', slide, 'data-medium-url')

                    if self.url == '':
                        slideImg = slide.findChild('img')

                        if slideImg:
                            if 'data-img' in slideImg.attrs:
                                self.url = self.validateContent('', slideImg, 'data-img')
                            elif 'src' in slideImg.attrs:
                                self.url = self.validateContent('', slideImg, 'src')


                    if self.url == '':
                        logger.warning('Image not detected in url: {}'.format(_url))
                        continue


                    self.foreignIdentifier  = self.url
                    extracted.extend(self.formatOutput)


            return extracted


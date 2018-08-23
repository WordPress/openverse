"""
Content Provider:       Encyclopedia of Life (EOL)

ETL Process:            Identify images, of the various life forms on earth, that
                        are available under any Creative Commons license.

Output:                 TSV file containing images of artworks and their respective meta-data.
"""
from Provider import Provider
import logging
from bs4 import BeautifulSoup, NavigableString
from urlparse import urlparse
import json
import re


logging.basicConfig(format='%(asctime)s - %(name)s: [%(levelname)s] =======> %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class EOL(Provider):

    def __init__(self, _name, _domain, _cc_index):
        Provider.__init__(self, _name, _domain, _cc_index)


    def filterData(self, _data, _condition=None):
        data        = filter(lambda x: filter(lambda y: y in x.split('\t')[0], ['/pages/', '/data_objects/']), _data)
        self.data   = data

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

        soup                = BeautifulSoup(_html, 'html.parser') #NB: the HTML for this website has been updated (the common crawl data is not the most recent version)
        otherMetaData       = {}
        src                 = None
        license             = None
        version             = None
        imageURL            = None
        tags                = None
        extracted           = []

        self.clearFields()


        self.provider       = self.name
        self.source         = 'commoncrawl'

        #get the tags
        tags = soup.find('meta', {'name': 'keywords'})
        if tags:
            self.metaData['tags']   = self.validateContent('', tags, 'content')


        #title
        title = soup.find('meta', {'property': 'og:title'})
        if title:
            self.title = self.validateContent('', title, 'content').split(' - ')[0].strip()


        currentURL = soup.find('meta', {'property': 'og:url'})
        if currentURL:
            tmpURL = self.validateContent('', currentURL, 'content')
            if '/data_objects/' in _url:
                self.foreignLandingURL = tmpURL
                foreignID = self.getForeignID(tmpURL)
                if foreignID:
                    self.foreignIdentifier = foreignID.strip().encode('unicode-escape')

            else:
                self.metaData['set'] = tmpURL


        #description/summary
        overview = soup.find('div', {'class': re.compile('article( overview)?')})
        if overview:
            details = overview.findChild('div', {'class': 'copy'})
            if details:
                self.metaData['description'] = details.text.split('.')[0].strip().replace('<i>', '').replace('</i>', '').encode('unicode-escape')

                moreInfo = overview.findChild('div', {'class': 'header'})
                if moreInfo:
                    infoURL = moreInfo.find('a')
                    if infoURL:
                        self.metaData['more_information'] = '{}{}'.format(self.domain, infoURL.attrs['href'])

        #get the image
        if '/data_objects/' in _url:
            img = soup.find('div', {'class': 'media'})
            if img:
                img         = img.findChild('a')
                if img:
                    self.url    = self.validateContent('', img, 'href')
                else:
                    logger.warning('Image not detected in url: {}'.format(_url))
                    return None


            #verify the license
            sourceInfo = soup.find('div', {'class': 'article source'})
            if sourceInfo:
                licenseDetails = sourceInfo.findChild('a', {'href': re.compile('creativecommons.org')})
                if licenseDetails:
                    ccURL               = urlparse(licenseDetails.attrs['href'].strip())
                    license, version    = self.getLicense(ccURL.netloc, ccURL.path, _url)

                    if not license:
                        logger.warning('License not detected in url: {}'.format(_url))
                        return None

                    self.license            = license
                    self.licenseVersion     = version


                #credits
                owner = sourceInfo.find('p', {'title': 'Rights holder'})
                if owner:
                    self.metaData['rights_holder'] = owner.text.strip().encode('unicode-escape').replace('\\xa9', '').strip()

                articleInfo = sourceInfo.find_all('p', {'title': None})
                if articleInfo:

                    for aInfo in articleInfo:
                        if aInfo:
                            aInfo = re.sub('<br/>', '</p><p>', aInfo.prettify())
                            aInfo = BeautifulSoup (aInfo, 'html.parser')


                            for tmpInfo in aInfo.find_all('p'):
                                key = tmpInfo.text.split(':')[0].lower().strip().encode('unicode-escape').replace(' ', '_')
                                key = key.replace('view_source', 'source')

                                sourceURL = None

                                if tmpInfo.findChild('a'):
                                    sourceURL = tmpInfo.findChild('a')['href'].strip().encode('unicode-escape')

                                    if sourceURL[0] == '/':
                                        sourceURL = '{}{}'.format(self.domain, sourceURL)

                                if key in ['supplier', 'source'] and sourceURL is not None:
                                    self.metaData[key] = sourceURL

                                elif key in ['publisher', 'contributor', 'location_created', 'photographer', 'author', 'latitude', 'longitude']:
                                    self.metaData[key] = tmpInfo.text.split(':')[1].strip().encode('unicode-escape').replace('\\xa9', '').strip()
                                    if sourceURL:
                                        self.metaData['{}_url'.format(key)] = sourceURL

                                elif key == 'creator':
                                        self.creator = tmpInfo.text.split(':')[1].strip().encode('unicode-escape').replace('\\xa9', '').strip()
                                        if sourceURL:
                                            self.creatorURL = sourceURL

            formatted = list(self.formatOutput)
            return formatted


        #classification
        classification = soup.find('div', {'class': 'browsable classifications'})
        if classification:
            current = classification.findChild('span', {'class': 'current'})

            if current and current.i:
                self.metaData['classification'] = current.i.text.strip().encode('unicode-escape')


        dataTable = soup.find('div', {'class': 'data_div'})
        if dataTable:
            dataTable = dataTable.find_all('tr')

            for row in dataTable:
                if len(row.find_all('td')) > 1:
                    key = row.th.text.lower().strip().encode('unicode-escape').replace(' ', '_')
                    val = row.find_all('td')[1].contents[0].strip().encode('unicode-escape')


        #images
        images = soup.find('div', {'class': 'images'})
        if images:
            images = images.find_all('div', {'class': 'image'})

            for imageInfo in images:
                self.foreignIdentifier  = ''
                self.foreignLandingURL  = ''
                self.thumbnail          = ''
                self.url                = ''
                self.license            = ''
                self.licenseVersion     = ''
                self.creator            = ''

                if 'image_alt_text' in self.metaData:
                    del self.metaData['image_alt_text']

                if 'source' in self.metaData:
                    del self.metaData['source']

                if 'supplier' in self.metaData:
                    del self.metaData['supplier']


                imgDetails = imageInfo.find('a')
                if imgDetails:
                    foreignID = self.getForeignID(imgDetails.attrs['href'])
                    if foreignID:
                        self.foreignIdentifier = foreignID.strip().encode('unicode-escape')

                    self.foreignLandingURL = '{}{}'.format(self.domain, imgDetails.attrs['href'].strip().encode('unicode-escape'))

                    imgProperty = imgDetails.findChild('img')
                    if imgProperty:
                        dataID                          = imgProperty.attrs['data-data-object-id'].strip().encode('unicode-escape')

                        if 'data-thumb' in imgProperty.attrs:
                            self.thumbnail              = imgProperty.attrs['data-thumb'].strip().encode('unicode-escape')

                        if 'src' in imgProperty.attrs:
                            self.url                        = imgProperty.attrs['src'].strip().encode('unicode-escape')

                        else:
                            logger.warning('Image not detected in url: {}'.format(_url))
                            continue


                        if 'alt' in imgProperty.attrs:
                            self.metaData['image_alt_text'] = imgProperty.attrs['alt'].strip().encode('unicode-escape')
                    else:
                        logger.warning('Image not detected in url: {}'.format(_url))
                        continue


                        if dataID <> foreignID:
                            self.foreignIdentifier = ''


                    #verify license
                    licenseInfo = imageInfo.find('div', {'class': 'attribution'})
                    if licenseInfo:
                        licenseDetails      = licenseInfo.findChild('a')
                        if licenseDetails:
                            ccURL               = urlparse(licenseDetails.attrs['href'].strip())
                            license, version    = self.getLicense(ccURL.netloc, ccURL.path, _url)

                        if not license:
                            logger.warning('License not detected in url: {}'.format(_url))
                            continue

                        self.license            = license
                        self.licenseVersion     = version


                        #credits
                        ownerInfo = licenseInfo.find('div', {'class': 'copy'})
                        if ownerInfo:
                            ownerInfo = ownerInfo.findChildren('p')
                            for owner in ownerInfo:
                                if 'class' in owner.attrs:
                                    self.creator = owner.text.strip().encode('unicode-escape').replace('\\xa9', '').replace('Copyright', '').strip()
                                else:
                                    source = owner.findChild('a') #get the image source or supplier
                                    if source:
                                        srcURL = source.attrs['href'].strip().encode('unicode-escape')
                                        if srcURL[0] == '/':
                                            srcURL = '{}{}'.format(self.domain, srcURL)
                                        key = owner.contents[0].lower().strip().replace(':', '').replace(' ', '_')
                                        val = srcURL

                                        if (key == 'source') or (key == 'supplier'):
                                            self.metaData[key] = val

                    extracted.extend(self.formatOutput)


                else:
                    logger.warning('Image not detected in url: {}'.format(_url))
                    continue


        return extracted


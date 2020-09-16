from Provider import *


logging.basicConfig(format='%(asctime)s - %(name)s: [%(levelname)s - CAPL] =======> %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class CAPL(Provider):

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

        #single image
        imgInfo = soup.find('div', {'class': 'singleimage'})

        if imgInfo:
            self.clearFields()
            self.translationAvailable   = True
            self.provider               = 'CAPL'
            self.source                 = 'commoncrawl'

            #verify the license
            licenseInfo = imgInfo.findChild('a', {'rel': 'license', 'href': True})

            if licenseInfo:
                ccURL               = urlparse(licenseInfo.attrs['href'])
                license, version    = self.getLicense(ccURL.netloc, ccURL.path, _url)

            if not license:
                logging.warning('License not detected in url: {}'.format(_url))
                return None

            self.license            = license
            self.licenseVersion     = version

            #verify the image
            imgURL  = imgInfo.findChild('span', {'class': 'alternateImages'})
            if imgURL:
                #get image and thumbnail
                lgImage = imgURL.find('span', {'class': 'directLink'})
                if lgImage:
                    lgImage         = self.validateContent('', lgImage.a, 'href')
                    lgImage         = re.sub(r'(/m/)|(/s/)', '/l/', lgImage)

                self.url = lgImage

                #get the image dimensions
                #imgHolder   = imgInfo.findChild('span', {'class': 'imgHolder'})
                #if imgHolder:
                #    imgDimensions = imgHolder.img
                #    if self.validateContent(None, imgDimensions, 'src') in lgImage:
                #        width       = self.sanitizeString(self.validateContent('', imgDimensions, 'width'))
                #        height      = self.sanitizeString(self.validateContent('', imgDimensions, 'height'))
                #        self.width  = width if width else ''
                #        self.height = height if height else ''

                self.thumbnail  = self.url.replace('/l/', '/m/')

            if not self.url:
                logging.warning('Image not detected in url: {}'.format(_url))
                return None


            #get the foreign URL
            self.foreignLandingURL = re.sub(r'(size=m)|(size=s)', 'size=l', _url).strip()

            #set the foreign ID to the image URL
            self.foreignIdentifier = self.url

            #creator info
            self.creator = 'Michael R. Shaughnessy'


            #title info
            titleInfo = imgInfo.findChildren('div', {'class': 'line'})
            for title in titleInfo:
                if self.validateContent('', title.span, 'lang') == 'en':
                    self.title = self.sanitizeString(title.span.text)

                elif title and self.validateContent('', title.span, 'lang') != 'en':
                    key                 = title.text.split(':')[0]
                    key                 = key.replace('Description', 'title').lower().strip()
                    key                 = re.sub(r'\s+', ' ', key)
                    key                 = re.sub(r'\s', '_', key)
                    key                 = key.replace('(', '').replace(')', '')
                    otherMetaData[key]  = self.sanitizeString(title.span.text)

            if not self.title:
                logging.warning('Title not detected in url: {}'.format(_url))
                return None


            if otherMetaData:
                self.metaData = otherMetaData

            return self.formatOutput

        else:
            #multiple images
            imgList = soup.find_all('div', {'class': re.compile('(light item)|(dark item)')})

            if imgList:
                for imgDetails in imgList:
                    self.clearFields()
                    self.translationAvailable   = True
                    self.provider               = 'CAPL'
                    self.source                 = 'commoncrawl'


                    details = imgDetails.findChild('div', {'class': 'image'})
                    if details:
                        #verify the license
                        licenseInfo = details.find('a', {'rel': 'license', 'href': True})

                        if licenseInfo:
                            ccURL               = urlparse(licenseInfo.attrs['href'])
                            license, version    = self.getLicense(ccURL.netloc, ccURL.path, _url)

                        if not license:
                            logging.warning('License not detected in url: {}'.format(_url))
                            continue

                        self.license            = license
                        self.licenseVersion     = version


                    imgURL  = details.find('a', {'data-rel': 'lightbox[results]', 'href': True})
                    if imgURL:
                        lgImage         = self.validateContent('', imgURL, 'href')
                        lgImage         = re.sub(r'(/m/)|(/s/)', '/l/', lgImage)
                        self.url        = '{}/{}'.format(self.domain, lgImage)
                        self.thumbnail  = self.url.replace('/l/', '/m/')

                    if not self.url:
                        logging.warning('Image not detected in url: {}'.format(_url))
                        continue


                    #title info
                    titleInfo = imgDetails.findChildren('div', {'class': 'line'})
                    for title in titleInfo:
                        if self.validateContent('', title.span, 'lang') == 'en':
                            self.title = self.sanitizeString(title.span.text)

                        elif title and self.validateContent('', title.span, 'lang') != 'en':
                            key                 = title.text.split(':')[0]
                            key                 = key.replace('Description', '').lower().strip()
                            key                 = re.sub(r'\s+', ' ', key)
                            key                 = re.sub(r'\s', '_', key)
                            key                 = key.replace('(', '').replace(')', '')
                            key                 = '{}_title'.format(key)
                            otherMetaData[key]  = self.sanitizeString(title.span.text)

                    if not self.title:
                        logging.warning('Title not detected in url: {}'.format(_url))
                        continue

                    #get the foreign URL
                    foreignURL = details.find('span', {'class': 'imgTxt'})
                    if foreignURL:
                        foreignURL = foreignURL.findChildren('a', {'href': True})
                        for fURL in foreignURL:
                            if fURL.text.strip().lower() == 'l':
                                self.foreignLandingURL = '{}/{}'.format(self.domain, self.validateContent('', fURL, 'href'))

                    #set the foreign ID to the image URL
                    self.foreignIdentifier = self.url

                    #creator info
                    self.creator = 'Michael R. Shaughnessy'


                    if otherMetaData:
                        self.metaData = otherMetaData

                    extracted.extend(self.formatOutput)


                return extracted

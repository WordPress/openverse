from Provider import *


logging.basicConfig(format='%(asctime)s - %(name)s: [%(levelname)s - Thorvaldsens Museum] =======> %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class ThorvaldsensMuseum(Provider):

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
        self.provider               = self.name
        self.source                 = 'commoncrawl'
        self.translationAvailable   = True

        #verify the license
        licenseInfo = soup.find('a', {'rel': 'license', 'href': True})
        if licenseInfo:
            ccURL               = urlparse(licenseInfo.attrs['href'].strip())
            license, version    = self.getLicense(ccURL.netloc, ccURL.path, _url)

            if not license:
                logging.warning(f'License not detected in url: {_url}')
                return None

            self.license            = license
            self.licenseVersion     = version

            #get the image
            if 'about' in licenseInfo.attrs:
                imageURL  = self.validateContent('', licenseInfo, 'about')


        if not imageURL:
            logging.warning(f'Image not detected in url: {_url}')
            return None
        else:
            self.url        = imageURL
            self.thumbnail  = imageURL.replace('/large/', '/small/')

            #get dimensions
            imgDimensions = soup.find('img', {'src': imageURL})
            if imgDimensions:
                self.width  = self.validateContent('', imgDimensions, 'width')
                self.height = self.validateContent('', imgDimensions, 'height')
                self.title  = self.sanitizeString(self.validateContent('', imgDimensions, 'alt'))

        #get title info
        #titleInfo = soup.find('a', {'class': 'enlarge'})
        #if titleInfo:
            #self.title              = self.validateContent('', titleInfo, 'title')
            #self.foreignIdentifier  = self.validateContent('', titleInfo, 'data-id').lstrip('work_resource_')

        self.foreignLandingURL = _url

        #get creator info
        artistInfo = soup.find('div', {'class': 'artists'})
        if artistInfo:
            self.creator    = self.sanitizeString(artistInfo.contents[0])
            self.creatorURL = self.validateContent('', artistInfo.findChild('a', {'class': 'standard', 'href': True}), 'href')


        return self.formatOutput

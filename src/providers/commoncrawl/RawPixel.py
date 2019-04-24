from Provider import *


logging.basicConfig(format='%(asctime)s - %(name)s: [%(levelname)s - RawPixel] =======> %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class RawPixel(Provider):

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


        imgInfo = soup.find_all('figure', {'class': re.compile('^(rowgrid-image teaser-item relative lazyload photo_grid)|(rowgrid-image rawpixel-image teaser-item lazyload relative photo_grid)$|()')})

        for info in imgInfo:
            self.clearFields()
            self.provider       = self.name
            self.source         = 'commoncrawl'

            #verify the licenses
            licenseInfo = info.findChild('a', {'rel': re.compile('^license'), 'href': True})

            if licenseInfo:
                ccURL               = urlparse(licenseInfo.attrs['href'])
                license, version    = self.getLicense(ccURL.netloc, ccURL.path, _url)

            if not license:
                logging.warning('License not detected in url: {}'.format(_url))
                continue

            self.license            = license
            self.licenseVersion     = version

            #extract the image
            imgInfo = info.findChild('img', {'class': 'lazyload'})
            if imgInfo:
                self.url        = imgInfo.get('data-pin-media')
                self.width      = imgInfo.get('width')
                self.height     = imgInfo.get('height')

                tmpthumbInfo    = imgInfo.get('data-srcset', '')
                imgList         = tmpthumbInfo.split(', ')

                if len(imgList) > 1:
                    self.thumbnail  = imgList[-1].strip()

            if not self.url:
                logging.warning('Image not detected in url: {}'.format(_url))
                continue


            #get image ID, landing page and title
            self.foreignIdentifier = info.get('data-node')

            titleInfo = info.findChild('a', {'class': 'img-link', 'href': True})
            if titleInfo:
                self.title = self.validateContent('', titleInfo, 'title')

            self.foreignLandingURL = self.sanitizeString(self.validateContent(_url, titleInfo, 'href'))


            extracted.extend(self.formatOutput)


        return extracted


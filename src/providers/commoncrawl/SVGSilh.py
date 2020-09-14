from Provider import *


logging.basicConfig(format='%(asctime)s - %(name)s: [%(levelname)s - SVGSilh] =======> %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class SVGSilh(Provider):

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
        A tab separated string which contains the CC0 content that was extracted from the HTML.

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


        svgList = soup.find_all('div', {'class': 'card mb-3 box-shadow h-100'})
        if svgList:
            for item in svgList:
                self.clearFields()
                self.provider               = self.name
                self.source                 = 'commoncrawl'
                self.translationAvailable   = True
                self.metaData               = {}

                licenseInfo = item.findChild('a', {'rel': 'license', 'href': True})
                if licenseInfo:
                    ccURL               = urlparse(licenseInfo.attrs['href'].strip())
                    license, version    = self.getLicense(ccURL.netloc, ccURL.path, _url)

                    if not license:
                        logging.warning(f'License not detected in url: {_url}'))
                        continue

                    elif (license.lower() != 'cc0'):
                        logging.warning(f'CC0 license not detected in url: {_url}')
                        continue

                    self.license            = license
                    self.licenseVersion     = version

                #get image info
                imageInfo   = item.a.img #findChid('a', {'title': 'Download SVG file', 'href': True})
                domain      = soup.find_all('meta', {'property': 'og:image'})

                if domain:
                    domain  =  self.validateContent('', domain[0], 'content').split('/png')[0]

                if self.provider.lower()  in domain:
                    imageURL = f'{domain}{self.validateContent('', imageInfo, 'src').replace('svg', 'png')}'
                    self.url = imageURL

                if not self.url:
                    logging.warning(f'Image not detected in url: {_url}')
                    continue

                foreignURL = item.findChild('a', href=re.compile(r'/image/\d+.html'))
                if foreignURL:
                    foreignURL              = self.validateContent('', foreignURL, 'href')
                    self.foreignLandingURL  = f'{domain}{foreignURL}'

                #get svg
                self.metaData['svg'] = f'{domain}{self.validateContent('', imageInfo, 'src')}'


                tagInfo = item.findChild('p', {'property': 'dct:title'})
                if tagInfo:
                    tagsList                = tagInfo.findChildren('a', text=True) #find_all('a', {'class': 'text-muted', 'text': True})
                    tags                    = ','.join(list(self.sanitizeString(tag.text) for tag in tagsList))
                    self.metaData['tags']   = tags

                titleInfo = soup.find('meta', {'property': 'og:description'})
                if titleInfo:
                    title       = self.validateContent('', titleInfo, 'content').split(' - ')[0]
                    self.title  = self.sanitizeString(title.split('(')[0])


                extracted.extend(self.formatOutput)


        if extracted:
            return extracted
        else:
            return None

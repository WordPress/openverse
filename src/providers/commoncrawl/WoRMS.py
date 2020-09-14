from Provider import *
from urllib.parse import parse_qs


logging.basicConfig(format='%(asctime)s - %(name)s: [%(levelname)s - WoRMS] =======> %(message)s', level=logging.INFO)


class WoRMS(Provider):

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
        formatted           = []
        width               = ''
        height              = ''

        self.clearFields()
        self.provider       = self.name
        self.source         = 'commoncrawl'

        urlInfo             = soup.find('div', {'id': 'photogallery_share'})
        if urlInfo:
            foreignURL      = urlparse(urlInfo.attrs['data-url'])
            foreignID       = parse_qs(foreignURL.query)['pic'], urlInfo.attrs['data-url']

            if len(foreignID) > 1 and foreignID[0]:
                self.foreignIdentifier = foreignID[0][0]

            if foreignURL:
                self.foreignLandingURL = urlInfo.attrs['data-url']
            else:
                self.foreignLandingURL = _url


        if 'p=image' in _url:
            #if on the image details page
            imgInfo = soup.find('div', {'id': 'photogallery_resized_img'})
            if imgInfo:
                #verify the license
                licenseInfo = imgInfo.findChild('meta', {'itemprop': 'license'})
                if licenseInfo:
                    ccURL               = urlparse(licenseInfo.attrs['content'])
                    license, version    = self.getLicense(ccURL.netloc, ccURL.path, _url)


                if not license:
                    logging.warning(f'License not detected in url: {_url}')
                    return None


                self.license        = license
                self.licenseVersion = version


                #get the image details
                imgDetails = imgInfo.findChild('img')
                if imgDetails:
                    self.url        = imgDetails.attrs['src']

                    if 'width' in imgDetails.attrs:
                        width           = self.sanitizeString(self.validateContent('', imgDetails, 'width'))

                    if 'height' in imgDetails.attrs:
                        height          = self.sanitizeString(self.validateContent('', imgDetails, 'height'))


                    self.thumbnail  = self.url.replace('resized', 'thumbs')
                    self.title      = self.sanitizeString(imgDetails.attrs['title'].strip())

                else:
                    logging.warning(f'Image not detected in url: {_url}')
                    return None

            try:
                self.width  = int(float(str(width)))

            except ValueError:
                logging.warning(f'Error extracting the image dimensions => {imgDetails}')
                self.width  = '0' #temporary bug fix

            try:
                self.height = int(float(str(height)))

            except ValueError:
                logging.warning(f'Error extracting the image dimensions => {imgDetails}')
                self.height  = '0' #temporary bug fix


            #get the meta-data

            #title   = soup.find('div', {'class': 'photogallery_caption photogallery_title'})
            #if title:
                #self.title = title.text.strip()

            desc    = soup.find('span', {'class': 'photogallery_caption photogallery_descr'})
            if desc:
                descText = desc.findChild('span', {'class': 'photogallery_caption photogallery_text'})
                if descText and descText.text.strip():
                    otherMetaData['description'] = self.sanitizeString(descText.text.strip())


            authorInfo = soup.find('span', {'class': 'photogallery_caption photogallery_author'})
            if authorInfo:
                author = authorInfo.findChild('a')

                if author:
                    self.creator    = self.sanitizeString(author.text.strip())
                    self.creatorURL = author.attrs['href']

                else:
                    author = authorInfo.findChild('span', {'class': 'photogallery_caption photogallery_text'})
                    if author and author.text.strip():
                        self.creator = author.text.strip()


            #taxa temporarily excluded. That info may not be from a verifiable source.

            if otherMetaData:
                self.metaData = otherMetaData


            formatted = list(self.formatOutput)

            return formatted

        elif 'p=taxdetails' in _url:
            #get the image tab on the taxonomy page
            return None #unable to verify the image license from this page (only text)

        else:
            return None

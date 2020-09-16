"""
Content Provider:       DeviantArt

ETL Process:            Identify the various artworks that are
                        available under a Creative Commons license.

Output:                 TSV file containing images of artworks and their
                        respective meta-data.
"""

# from Provider import *  # *imports create problems with flake8
from Provider import Provider, logging, BeautifulSoup, urlparse, re


logging.basicConfig(
    format=(
        '%(asctime)s - %(name)s: [%(levelname)s - DeviantArt] '
        '=======> %(message)s'),
    level=logging.INFO)


class DeviantArt(Provider):

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
        A tab separated string which contains the meta data that was extracted
        from the HTML.

        """

        soup = BeautifulSoup(_html, 'html.parser')
        otherMetaData = {}
        license = None
        version = None
        imageURL = None
        formatted = None

        self.clearFields()

        # verify the license
        licenseInfo = soup.find('a', {'rel': 'license', 'href': True})
        if licenseInfo:
            ccURL = urlparse(licenseInfo.attrs['href'].strip())
            license, version = self.getLicense(ccURL.netloc, ccURL.path, _url)

            if not license:
                logging.warning(f'License not detected in url: {_url}')
                return None

            self.license = license
            self.licenseVersion = version

            # locate the image
            imgProperty = soup.find('meta', {'property': 'og:image'})
            if imgProperty:
                imageURL = self.validateContent('', imgProperty, 'content')
                if 'main/logo/card_black_large.png' in imageURL:
                    logging.info(f'Image not available. Image url: {_url}')
                    return None

                imgWidth = self.validateContent('', soup.find(
                    'meta', {'property': 'og:image:width'}), 'content')
                imgHeight = self.validateContent('', soup.find(
                    'meta', {'property': 'og:image:height'}), 'content')

                self.url = imageURL
                self.width = imgWidth
                self.height = imgHeight
            else:
                logging.warning(f'Image not detected in url: {_url}')
                return None

            # get the title
            self.title = self.sanitizeString(self.validateContent(
                '', soup.find('meta', {'property': 'og:title'}), 'content'))

            # creator
            creatorInfo = soup.find('small', {'class': 'author'})
            if creatorInfo:
                creator = creatorInfo.findChild(
                    'a', {'class': re.compile('username$'), 'href': True})
                if creator:
                    self.creatorURL = self.validateContent('', creator, 'href')
                    self.creator = self.sanitizeString(creator.text.strip())

            # description
            description = soup.find('div', {'class': 'text block'})
            if description and description.text.strip():
                otherMetaData['description'] = (
                    self.sanitizeString(description.text.strip()))

            self.foreignLandingURL = self.validateContent(
                _url, soup.find('meta', {'property': 'og:url'}), 'content')

            foreignID = soup.find(
                'div', {'class': 'dev-page-view view-mode-normal'})
            if foreignID:
                self.foreignIdentifier = (
                    foreignID.attrs['gmi-deviationid'].strip())
            else:
                logging.warning(f'Identifier not detected in: {_url}')
                return None

            self.provider = self.name
            self.source = 'commoncrawl'

            if otherMetaData:
                self.metaData = otherMetaData

            formatted = list(self.formatOutput)

            return formatted

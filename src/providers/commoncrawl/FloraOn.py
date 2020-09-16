"""
Content Provider:       Flora-On

ETL Process:            Identify images of plant species that are available
                        under a Creative Commons license.

Output:                 TSV file containing images of artworks and their
                        respective meta-data.
"""

# from Provider import *  # *imports create problems with flake8
from Provider import Provider, logging, BeautifulSoup, urlparse


logging.basicConfig(
    format=(
        '%(asctime)s - %(name)s: [%(levelname)s - Flora-On] '
        '=======> %(message)s'),
    level=logging.INFO)


class FloraOn(Provider):

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
        # imageURL = None  # Assigned but never used
        extracted = []

        photoList = soup.find('div', {'id': 'fotochooser'})

        if photoList:
            for photo in photoList.find_all('div', {'class': 'thumbnail'}):
                self.clearFields()
                self.watermarked = 't'

                licenseInfo = photo.find('a', {'rel': 'license'})
                ccURL = urlparse(licenseInfo.attrs['href'].strip())
                license, version = self.getLicense(
                    ccURL.netloc, ccURL.path, _url)

                if not license:
                    logging.warning(f'License not detected in url: {_url}')
                    continue

                self.license = license
                self.licenseVersion = version

                # get the image
                imageInfo = photo.find('img', {'class': 'image', 'src': True})
                if imageInfo:
                    self.url = self.validateContent('', imageInfo, 'src')
                    otherMetaData['image_alt_text'] = (
                        self.validateContent('', imageInfo, 'alt'))
                    if self.url:
                        sdstrip = self.domain.strip('%')
                        self.url = f'{sdstrip}/{self.url}'
                    else:
                        logging.warning(f'Image not detected in url: {_url}')
                        continue

                    imgWidth = photo.find('input', {'name': 'wid'})
                    if imgWidth:
                        self.width = self.validateContent(
                            '', imgWidth, 'value')

                    imgHeight = photo.find('input', {'name': 'hei'})
                    if imgHeight:
                        self.height = self.validateContent(
                            '', imgHeight, 'value')

                    titleInfo = soup.find('span', {'class': 'especie'})
                    if titleInfo:
                        self.title = titleInfo.text.strip().lower()

                    authorInfo = photo.find('input', {'name': 'aut'})
                    self.creator = self.validateContent(
                        '', authorInfo, 'value')

                    self.foreignLandingURL = _url
                    self.provider = self.name
                    self.source = 'commoncrawl'

                    # get the details
                    details = soup.find('div', {'id': 'fic-ecologia'}) \
                                  .find_all('div', {'class': 'fic-detalhe'})
                    if details:
                        for detail in details:
                            key = detail.find('div', {'class': 'head'}) \
                                        .text.strip().lower().replace(' ', '_')
                            val = detail.find('div', {'class': 'content'}) \
                                        .text.strip()
                            otherMetaData[key] = val

                    # related species
                    species = soup.find('div', {'id': 'detalhes-especie'})
                    if species:
                        key = species.find(
                            'span', {'class': 'showtooltip big'})
                        if key:
                            key = key.text.strip().lower().replace(' ', '_')
                            related = species.find_all('i')
                            val = ','.join([
                                x.text.strip() for x in related if
                                x.text.strip() != 'Download'])
                            otherMetaData[key] = val

                    if otherMetaData:
                        self.metaData = otherMetaData

                    extracted.extend(self.formatOutput)

            return extracted

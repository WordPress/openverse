"""
Content Provider:       DigitaltMuseum

ETL Process:            Identify the various artworks and photographs that are
                        in the public domain or available under any Creative
                        Commons license.

Output:                 TSV file containing images of artworks and their
                        respective meta-data.
"""

# from Provider import *  # *imports create problems with flake8
from Provider import Provider, logging, BeautifulSoup, urlparse, re

logging.basicConfig(
    format=(
        '%(asctime)s - %(name)s: [%(levelname)s] - Digitalt Museum '
        '=======> %(message)s'),
    level=logging.INFO)


class DigitaltMuseum(Provider):

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
        # NB: the HTML for this website has been updated (the common crawl data
        # is not the most recent version)
        soup = BeautifulSoup(_html, 'html.parser')
        # otherMetaData = {}  # Assigned but never used
        # src = None  # Assigned but never used
        license = None
        version = None
        # imageURL = None  # Assigned but never used
        # tags = None  # Assigned but never used
        extracted = []

        self.clearFields()

        media = soup.find_all('li', {'class': 'media__item'})

        url = ''
        mediaURL = soup.find('meta', {'property': 'og:url'})
        if mediaURL:
            url = self.validateContent(_url, mediaURL, 'content')

        '''description = soup.find('meta', {'name': 'description'})
        if description:
            description = self.validateContent('', description, 'content')'''

        desc = ''
        description = soup.find('div', {'class': 'article__leadtext'})
        if description:
            description = description.find_all('p')
            if description:
                desc = description[0].text.strip()
                desc = desc.replace('Expand text', '').strip()

        title = ''
        titleInfo = soup.find('div', {'class': 'article__title'})
        if titleInfo:
            titleInfo = titleInfo.findChild('h1')
            if titleInfo:
                title = self.sanitizeString(titleInfo.text.strip())

        articleInfo = soup.find_all('section', {'class': 'article__metadata'})
        articleMetaData = {}
        if articleInfo:
            for meta in articleInfo:
                label = meta.findChild('h2')
                if label and label.text.strip() .lower() == 'metadata':
                    for mData in meta.findChildren('li'):
                        mData = mData.text.strip().replace('\\n', '').replace(
                            '\\t', '').replace('\s{2,}', '')  # .split(':')
                        mData = re.split('\s{2,}', mData)
                        if len(mData) > 1:
                            key = mData[0].lower().replace(' ', '_')
                            val = mData[1]
                            articleMetaData[key] = self.sanitizeString(val)

        # get tags - NA

        if media:
            for item in media:
                self.clearFields()
                self.provider = self.name
                self.source = 'commoncrawl'
                self.translationAvailable = True

                # verify license
                license = None
                version = ''

                licenseInfo = item.findChild(
                    'a', {'class': re.compile(r'(media__license.*?)')})
                if not licenseInfo:
                    licenseInfo = item.findChild(
                        'a', {'class': 'c-media-slider__license-link'})

                if licenseInfo:
                    ccURL = urlparse(licenseInfo.attrs['href'].strip())
                    license, version = self.getLicense(
                        ccURL.netloc, ccURL.path, _url)

                if not license:
                    logging.warning(f'License not detected in url: {_url}')
                    continue

                self.license = license
                self.licenseVersion = version
                self.title = title

                # get image
                imageInfo = item.findChild(
                    'a', {'class': 'module__media  media--image'})
                if not imageInfo:
                    imageInfo = item.findChild(
                        'a', {'class': 'module__media media--image'})

                if imageInfo:
                    self.foreignLandingURL = (
                        f'{self.domain}'
                        f'{self.validateContent("", imageInfo, "href")}')

                    img = imageInfo.find('img')
                    if img and 'src' in img.attrs:
                        self.url = self.validateContent('', img, 'src')

                    if img and 'alt' in img.attrs:
                        articleMetaData['image_alt_text'] = (
                            self.sanitizeString(self.validateContent(
                                '', img, 'alt')))

                if self.url == '':
                    logging.warning(f'Image not detected in url: {_url}')
                    continue

                # get owner info
                owner = item.findChild('i', {'class': 'media__credit'})
                if owner:
                    owner = owner.text.split(':')
                    if len(owner) > 1:
                        self.creator = self.sanitizeString(owner[1].strip())

                if len(media) > 1:
                    articleMetaData['set'] = url

                if description:
                    articleMetaData['description'] = self.sanitizeString(desc)

                if articleMetaData:
                    self.metaData = articleMetaData

                extracted.extend(self.formatOutput)

            return extracted

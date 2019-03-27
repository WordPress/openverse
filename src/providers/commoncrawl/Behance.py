"""
Content Provider:       Behance

ETL Process:            Identify curated galleries of images that are
                        available under a Creative Commons license.

Output:                 TSV file containing images of artworks and their respective meta-data.
"""
from Provider import *


logging.basicConfig(format='%(asctime)s - %(name)s: [%(levelname)s - Behance] =======> %(message)s', level=logging.INFO)


class Behance(Provider):

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
        src                 = None
        license             = None
        version             = None
        imageURL            = None
        extracted           = []
        otherMetaData       = {}

        self.clearFields()

        #verify license
        licenseInfo = soup.find('div', {'id': 'project-block-copyright'})
        if licenseInfo:
            licenseInfo         = licenseInfo.findChild('a')
            if licenseInfo:
                ccURL               = urlparse(licenseInfo.attrs['href'].strip())
                license, version    = self.getLicense(ccURL.netloc, ccURL.path, _url)

            if not license:
                logging.warning('License not detected in url: {}'.format(_url))
                return None

            self.license            = license
            self.licenseVersion     = version


        #title
        title = soup.find('div', {'class': 'project-title'})
        if title:
            self.title = title.text.strip()


        #url
        foreign_url = soup.find('meta', {'property': 'og:url'})
        if foreign_url:
            self.foreignLandingURL = self.validateContent(_url, foreign_url, 'content')


        #creator info
        owner = soup.find('meta', {'property': 'og:owners'})
        if owner:
            self.creator = self.validateContent('', owner, 'content')


        credits = soup.find('div', {'id': 'project-block-footer-credits'})
        if credits:
            creators = credits.find_all('div', {'class': re.compile('(rf-)?profile-item ')})
            creatorList = []

            for creator in creators:
                creatorDict = {}
                creatorInfo = creator.findChild('a', {'class': re.compile('(rf-)?profile-item__name js-mini-profile')})

                if creatorInfo:
                    creatorName         = creatorInfo.text.strip()
                    creatorDict['name'] = self.sanitizeString(creatorName)

                    creatorURL                  = creatorInfo.attrs['href'].strip()
                    creatorDict['creator_url']  = creatorURL

                location = creator.findChild('a', {'class': re.compile('(rf-)?profile-item__location beicons-pre beicons-pre-location'), 'href': True})
                if location:
                    link = location.attrs['href']

                    if link:
                        locationInfo = link.split('&')

                        for location in locationInfo:
                            if any(loc in location.strip().lower() for loc in ['country', 'state', 'city']):
                                loc = location.split('=')
                                creatorDict[loc[0].strip().lower()] = loc[1].strip().replace('+', ' ')

                creatorList.append(creatorDict)

            if creatorList:
                otherMetaData['owners'] = creatorList


        #tags
        tagInfo = soup.find_all('a', {'class': 'object-tag'})
        if tagInfo:
            tags                    = ','.join(tag.text.strip() for tag in tagInfo)
            otherMetaData['tags']   = tags


        #description
        description = soup.find('meta', {'name': 'description'})
        if description:
            otherMetaData['description'] = self.validateContent('', description, 'content')


        self.provider           = self.name
        self.source             = 'commoncrawl'
        otherMetaData['set']   = self.foreignLandingURL

        if otherMetaData:
            self.metaData = otherMetaData


        #get the images
        images = soup.find('div', {'id': 'project-modules'})
        if images:
            imageList = images.find_all('img')

            for img in imageList:
                self.url                = ''
                self.foreignIdentifier  = ''

                self.url = self.validateContent('', img, 'src')
                if self.url == '':
                    logging.warning('Image not detected in url: {}'.format(_url))
                    continue

                elif 'img/site/blank.png' not in self.url:
                    extracted.extend(self.formatOutput)


        return extracted


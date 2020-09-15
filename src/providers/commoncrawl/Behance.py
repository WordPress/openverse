"""
Content Provider:       Behance

ETL Process:            Identify curated galleries of images that are
                        available under a Creative Commons license.

Output:                 TSV file containing images of artworks and their respective meta-data.
"""
from Provider import *
import logging

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

        if not licenseInfo:
            licenseInfo = soup.find('div', {'class': 'ProjectCopyright-tooltipContent-LVf'})

        if licenseInfo:
            licenseInfo         = licenseInfo.findChild('a')
            if licenseInfo:
                ccURL               = urlparse(licenseInfo.attrs['href'].strip())
                license, version    = self.getLicense(ccURL.netloc, ccURL.path, _url)

        if not license:
            logging.warning(f'License not detected in url: {_url}')
            return None

        self.license            = license
        self.licenseVersion     = version


        #title
        title = soup.find('meta', {'property': 'og:title'})
        if title:
            self.title = self.sanitizeString(self.validateContent('', title, 'content'))


        #url
        foreign_url = soup.find('meta', {'property': 'og:url'})
        if foreign_url:
            self.foreignLandingURL = self.validateContent(_url, foreign_url, 'content')


        #creator info
        owner = soup.find('meta', {'property': 'og:owners'})
        if owner:
            self.creator = self.sanitizeString(self.validateContent('', owner, 'content'))


        creators = soup.find_all('div', {'class': 'rf-profile-item__info'})

        if not creators:
            creators = soup.find_all('div', {'class': 'ProjectOwnersInfo-userInfo-2WK'})

        if creators:
            creatorList = []

            for creator in list(set(creators)):
                creatorDict = {}
                creatorInfo = creator.find('a', {'class': re.compile('(rf-profile-item__name js-mini-profile)|(ProjectOwnersInfo-userName-2oz js-mini-profile)'), 'href': True})
                if creatorInfo:
                    creatorName                 = creatorInfo.text.strip()
                    creatorName                 = self.sanitizeString(self.sanitizeString(creatorName))
                    creatorDict['name']         = creatorName
                    creatorURL                  = creatorInfo.attrs['href'].strip()
                    creatorDict['creator_url']  = creatorURL

                    if self.creator.lower() == creatorName:
                        self.creatorURL = creatorURL


                location = creator.findChild('a', {'class': re.compile('(rf-profile-item__location beicons-pre beicons-pre-location)|(ProjectOwnersInfo-userLocation-_rE beicons-pre beicons-pre-location)'), 'href': True})

                if location:
                    link = location.attrs['href']

                    if link:
                        locationInfo = link.split('&')

                        for location in locationInfo:
                            if any(loc in location.strip().lower() for loc in ['country', 'state', 'city']):
                                loc = location.split('=')
                                creatorDict[loc[0].strip().lower()] = loc[1].strip().replace('+', ' ')

                if creatorDict and creatorDict not in creatorList:
                    creatorList.append(creatorDict)

            if creatorList:
                otherMetaData['owners']  = creatorList


        #tags
        tagInfo = soup.find_all('a', {'class': re.compile('(object-tag)|(ProjectTags-tagLink-Hh_)')})
        if tagInfo:
            otherMetaData['tags'] = ','.join(self.sanitizeString(tag.text.strip()) for tag in tagInfo)


        #description
        description = soup.find('meta', {'property': 'og:description'})
        if description:
            desc                         = self.sanitizeString(self.validateContent('', description, 'content'))
            otherMetaData['description'] = desc


        self.provider           = self.name
        self.source             = 'commoncrawl'
        otherMetaData['set']    = self.foreignLandingURL

        if otherMetaData:
            self.metaData = otherMetaData


        #get the popularity metrics
        '''popInfo = soup.find('div', {'class': 'Project-projectInfo-1yh'})
        if not popInfo:
            popInfo = soup.find('div', {'id': 'project-stats'})


        if popInfo:
            self.popularityMetrics = {}

            likes = popInfo.find('div', {'class': re.compile(r'beicons-pre-thumb$')})
            views = popInfo.find('div', {'class': re.compile(r'beicons-pre-eye$')})
            cmmts = popInfo.find('div', {'class': re.compile(r'beicons-pre-comment$')})

            if likes:
                self.popularityMetrics['likes'] = self.sanitizeString(likes.text)

            if views:
                self.popularityMetrics['views'] = self.sanitizeString(views.text)

            if cmmts:
                self.popularityMetrics['comments'] = self.sanitizeString(cmmts.text)'''


        #get the images
        images = soup.find('div', {'id': 'project-modules'})
        if images:
            imageList = images.find_all('img')

            for img in imageList:
                self.url                = ''
                self.foreignIdentifier  = ''

                self.url = self.validateContent('', img, 'src')
                if self.url == '':
                    logging.warning(f'Image not detected in url: {_url}')
                    continue

                elif 'img/site/blank.png' not in self.url:
                    extracted.extend(self.formatOutput)

        return extracted

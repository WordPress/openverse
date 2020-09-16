"""
Content Provider:       Science Museum - Historical exhibits and artworks

ETL Process:            Identify artworks that are available under a Creative
                        Commons license or in the public domain.

Output:                 TSV file containing images of artworks and their respective meta-data.
"""
from Provider import *


logging.basicConfig(format='%(asctime)s - %(name)s: [%(levelname)s - Science Museum UK] =======> %(message)s', level=logging.INFO)


class ScienceMuseum(Provider):

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
        self.provider       = self.name
        self.source         = 'commoncrawl'

        #verify the license
        licenseDetails = soup.find('div', {'class': 'cite__method'}) #soup.find('svg', {'class': 'icon icon-cc-zero'})
        if licenseDetails:
            imgLicense  = licenseDetails.findChild('img') #licenseDetails.parent
            if imgLicense and 'src' in imgLicense.attrs:
                imgLicense  = self.validateContent('', imgLicense, 'src').split('/')
                imgLicense  = imgLicense[len(imgLicense)-1].split('.')[0].lstrip('cc-')
                license     = imgLicense.lower()

            if not license:
                logging.warning('License not detected in url: {}'.format(_url))
                return None

            self.license = license


        url = soup.find('meta', {'property': 'og:url'})
        if url:
            self.foreignLandingURL = self.validateContent(_url, url, 'content')


        #get the title
        title = soup.find('meta', {'property': 'og:title'})
        if title:
            self.title = self.sanitizeString(self.validateContent('', title, 'content'))


        #description/summary
        description = soup.find('meta', {'property': 'og:description'})
        if description:
            otherMetaData['description'] = self.sanitizeString(self.validateContent('', description, 'content'))


        #credits/attribution info
        makerInfo = soup.find('dl', {'class': 'record-top__dl fact-maker'})
        if makerInfo:
            maker = makerInfo.findChild('a')

            if maker:
                makerName = self.sanitizeString(maker.text.strip())
                if makerName.lower() != 'unknown':
                    self.creator = makerName

                    if 'href' in maker.attrs:
                        self.creatorURL = self.validateContent('', maker, 'href')


        #meta data
        timeline = soup.find('dl', {'class': 'record-top__dl fact-Made'})
        if timeline:
            timeline = timeline.text.strip().replace('Made:', '').replace('Maker:', '').split('in')
            if len(timeline) > 1:
                otherMetaData['date']       = timeline[0].strip()
                otherMetaData['geography']  = timeline[1].strip()


        otherDetails = soup.find_all('dl', {'class': re.compile(r'(record-details.*?)')})
        if otherDetails:
            for detail in otherDetails:
                key = detail.findChild('dt').text.strip().lower().replace(' ', '_')
                key = key.rstrip(':')
                val = self.sanitizeString(detail.findChild('dd').text.strip())

                otherMetaData[key] = val


        records = soup.find_all('img', {'class': 'carousel__image'})
        if not records:
            records = soup.find_all('img', {'class': 'single_image'})

        if otherMetaData:
            self.metaData = otherMetaData


        if records:
            for record in records:
                self.url = ''

                if 'src' in record.attrs:
                    self.url = record.attrs['src'].strip()

                elif 'data-flickity-lazyload' in record.attrs:
                    self.url = record.attrs['data-flickity-lazyload'].strip()


                if self.url == '':
                    logging.warning('Image not detected in url: {}'.format(_url))
                    continue

                extracted.extend(self.formatOutput)


        return extracted

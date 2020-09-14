"""
Content Provider:       Animal Diversity Web (ADW)

ETL Process:            Identify all images that are available under a Creative
                        Commons license or in the public domain by scraping the
                        html from Common Crawl's WARC files.

Output:                 TSV file containing images of artworks and their respective meta-data.
"""
from Provider import *

logging.basicConfig(format='%(asctime)s - %(name)s: [%(levelname)s] - Animal Diversity Web =======> %(message)s', level=logging.INFO)



class AnimalDiversityWeb(Provider):


    def __init__(self, _name, _domain, _cc_index):
        Provider.__init__(self, _name, _domain, _cc_index)


    def filterData(self, _data, _condition=None):
        #Images can be located in three main content paths: /accounts, /collections, and /site.
        allowed = list(map(lambda x: f'{self.domain}{x}', ['/accounts/', '/collections/', '/site/']))
        data    = list(filter(lambda x: x.split('\t')[0].startswith(tuple(allowed)), _data))
        self.data = data

        return self.data


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
        formatted           = None

        self.clearFields()

        #identify the license
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
            imgProperty = soup.find('img', {'class': 'resource', 'src': True})
            if imgProperty:
                self.url     = self.validateContent('', imgProperty, 'src')
                if self.url:
                    self.url = f'{self.domain.strip('%')}{self.url}'

                self.width                      = self.validateContent('', imgProperty, 'data-width')
                self.height                     = self.validateContent('', imgProperty, 'data-height')
                otherMetaData['image_alt_text'] = self.validateContent('', imgProperty, 'alt')

            else:
                logging.warning(f'Image not detected in url: f{_url}')
                return None


            #get the title
            title = soup.find('meta', {'property': 'og:title'}).attrs['content']
            if title:
                self.title = title


            #get the meta data
            section = soup.find('section', {'class': 'metadata'})
            if section:
                info = section.find_all(['h3', 'p'])
                for key, item in enumerate(info):

                    if item.name == 'h3':
                        lbl = item.text.strip().lower().replace(' ', '_')
                        val = info[key + 1]
                        if val:
                            val                 = val.text.strip()
                            otherMetaData[lbl]  = val

                if 'conditions_of_use' in otherMetaData:
                    del otherMetaData['conditions_of_use']


            #get the keywords/tags
            keywords = soup.find_all('ul', {'class': re.compile('keywords( last)?')})
            tagsList = []
            for tag in keywords:
                element = tag.find('li', {'class': None})
                if element:
                    tagsList.extend(ele.strip() for ele in element.text.split('::'))

            tagsList = list(set(tagsList))
            otherMetaData['tags'] = ','.join(tagsList)


            #get the classification info
            classification = soup.find('div', {'class': 'classification well'})

            if classification:
                classType = classification.find('h3')
                if classType:
                    classType = classType.text.strip().lower()
                    classInfo = {}

                    for item in classification.find_all('li'):
                        rank  = item.find('span', {'class': 'rank'})
                        if rank:
                            rank = rank.text.strip().lower()

                        taxon = item.find('a', {'class': re.compile('^taxon-name.*?')})
                        if taxon:
                            taxon = taxon.text.strip()

                        vern  = item.find('span', {'class': 'vernacular-name'})
                        if vern:
                            vern = vern.text.strip()

                        classInfo[rank] = f'{taxon} / {vern}'

                    otherMetaData[classType] = classInfo


            related = soup.find('div', {'class': 'related navlist well'})
            if related:
                relTaxa = related.find('h3')
                if relTaxa:
                    relTaxa = relTaxa.text.strip().lower().replace(' ', '_')
                    taxa    = {}

                    for item in related.find_all('li'):
                        rank  = item.find('span', {'class': 'rank'})
                        if rank:
                            rank = rank.text.strip().lower()

                        taxon = item.find('a', {'class': re.compile('^taxon-name.*?')})
                        if taxon:
                            taxon = taxon.text.strip()

                        vern  = item.find('span', {'class': 'vernacular-name'})
                        if vern:
                            vern = vern.text.strip()
                        taxa[rank] = f'{taxon} / {vern}'

                    otherMetaData[relTaxa] = taxa


            self.foreignLandingURL = self.validateContent(_url, soup.find('meta', {'property': 'og:url'}), 'content')

            self.provider   = self.name
            self.source     = 'commoncrawl'

            if otherMetaData:
                self.metaData   = otherMetaData


            formatted = list(self.formatOutput)

            return formatted

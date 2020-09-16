"""
Content Provider:       Museums Victoria - Collections of palaeontology, zoology, indigenous cultures etc.

ETL Process:            Identify images and their respective meta data that are available under a
                        Creative Commons license.

Output:                 TSV file containing images of artworks and their respective meta-data.
"""
from Provider import *


logging.basicConfig(format='%(asctime)s - %(name)s: [%(levelname)s] - Museums Victoria =======> %(message)s', level=logging.INFO)

class MuseumVictoria(Provider):

    def __init__(self, _name, _domain, _cc_index):
        Provider.__init__(self, _name, _domain, _cc_index)


    def filterData(self, _data, _condition=None):
        #Images can be located in four main content paths: /species, /items, /articles, and /specimens.
        allowed = list(map(lambda x: '{}{}'.format(self.domain, x), ['/species/', '/items/', '/specimens/', '/articles/']))
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
        license             = None
        version             = None
        imageURL            = None
        formatted           = []
        extracted           = []

        self.clearFields()

        #validate license for the image
        licenseInfo = soup.find('span', attrs={'class': 'licence'})

        if licenseInfo and licenseInfo.findChild('a'):
            ccURL               = urlparse(licenseInfo.findChild('a').attrs['href'])
            license, version    = self.getLicense(ccURL.netloc, ccURL.path, _url)

            if not license:
                logging.warning('License not detected in url: {}'.format(_url))
                return None

            self.license            = license
            self.licenseVersion     = version


            #get the image
            imgProperty = soup.find('meta', {'property': 'og:image'})
            if imgProperty:
                imageURL        = self.validateContent('', imgProperty, 'content')
                imgWidth        = self.validateContent('', soup.find('meta', {'property': 'og:image:width'}), 'content')
                imgHeight       = self.validateContent('', soup.find('meta', {'property': 'og:image:height'}), 'content')

                self.url        = imageURL
                self.thumbnail  = [imageURL.replace('-medium', '-thumbnail') if '-medium.' in imageURL else ''][0]
                self.width      = imgWidth
                self.height     = imgHeight

            else:
                logging.warning('Image not detected in url: {}'.format(_url))
                return None


            self.title = self.sanitizeString(self.validateContent('', soup.find('meta', {'property': 'og:title'}), 'content'))


            #owner/credits
            creatorInfo     = soup.find('div', {'class':'creators'})
            if creatorInfo:
                creator = self.sanitizeString(creatorInfo.text.strip())

                if 'Photographer' in creator:
                    self.creator = creator.replace('Photographer:', '').strip()
                elif 'Artist' in creator:
                    self.creator = creator.replace('Artist:', '').strip()


            foreignID   = self.getForeignID(_url)

            if foreignID:
                self.foreignIdentifier = foreignID.strip()
            else:
                logging.warning('Identifier not detected in: {}'.format(_url))
                return None

            '''thumbnails  = soup.find_all('div', {'class': 'thumbnail'})
            if thumbnails:
                thumbnails                          = ['{}{}'.format(self.domain, x.img['src']) for x in thumbnails]
                allImages                           = [x.replace('-thumbnail', '-medium') for x in thumbnails]
                otherMetaData['thumbnails']         = ','.join(thumbnails)
                otherMetaData['additional_images']  = ','.join(allImages)'''


            #summary
            summary = soup.find('div', {'class': 'summary'})
            if summary:
                description = summary.findChild('p')
                if description:
                    description = description.text.strip()
                    otherMetaData['description'] = self.sanitizeString(description)


            #more information/details
            moreInfo = soup.find('div', {'class': 'detail'})
            if moreInfo:
                details = moreInfo.findChildren('li')
                for item in details:
                    lbl = item.find('h3').text.strip()
                    lbl = re.sub('(\s)', '_', lbl).lower()
                    val =  ','.join(re.sub(r'\s+', ' ', x.text).strip() for x in item.find_all('p'))

                    otherMetaData[lbl] = val


            self.provider               = self.name
            self.source                 = 'commoncrawl'
            self.foreignLandingURL      = _url

            #tags
            if otherMetaData:
                if 'keywords' in otherMetaData:
                    otherMetaData['tags'] = otherMetaData['keywords']
                    del otherMetaData['keywords']


                #if 'artist' in otherMetaData:
                    #self.creator = otherMetaData['artist'].split('-')[0].strip()
                    #del otherMetaData['artist']

                self.metaData = otherMetaData

            #get the additional images
            thumbnails = soup.find_all('div', {'class': 'thumbnail'})
            if thumbnails and len(thumbnails) > 1:
                for item in thumbnails:
                    img                     = item.findChild('img')
                    self.url                = ''
                    self.thumbnail          = ''
                    self.foreignIdentifier  = ''

                    if 'image_alt_text' in otherMetaData:
                        del otherMetaData['image_alt_text']

                    if 'src' in img.attrs:
                        self.thumbnail          = '{}{}'.format(self.domain.strip('%'), self.validateContent('', img, 'src'))
                        self.url                = self.thumbnail.replace('-thumbnail', '-medium')
                        self.foreignIdentifier  = self.url

                        if 'alt' in img.attrs:
                            otherMetaData['image_alt_text'] = self.validateContent('', img, 'alt')

                    else:
                        logging.warning('Image not detected in url: {}'.format(_url))
                        continue

                    self.metaData = otherMetaData
                    extracted.extend(self.formatOutput)


                return extracted
            else:
                formatted = list(self.formatOutput)

                return formatted

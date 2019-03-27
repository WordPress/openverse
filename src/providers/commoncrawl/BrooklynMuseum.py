from Provider import *


logging.basicConfig(format='%(asctime)s - %(name)s: [%(levelname)s - Brooklyn Museum] =======> %(message)s', level=logging.INFO)


class BrooklynMuseum(Provider):

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


        licenseInfo = soup.find('div', {'id': 'rights-statement'})

        if licenseInfo:
            ccURL               = urlparse(licenseInfo.findChild('a').attrs['href'])
            license, version    = self.getLicense(ccURL.netloc, ccURL.path, _url)

            if not license:
                logging.warning('License not detected in url: {}'.format(_url))
                return None

            self.license            = license
            self.licenseVersion     = version


        objectID = soup.find('input', {'id': 'tag-item-id'})
        if objectID and 'value' in objectID.attrs:
            self.foreignLandingURL = 'https://www.brooklynmuseum.org/opencollection/objects/{}'.format(objectID.attrs['value'])
        else:
            self.foreignLandingURL = _url


        objectInfo = soup.find('div', {'class': re.compile('.*?object-data')})
        if objectInfo:
            titleDiv = objectInfo.findChild('div', {'class': 'row'})
            if titleDiv and titleDiv.h1:
                self.title = titleDiv.h1.text.strip()


        tombstoneData = soup.find_all('div', {'class': 'row tombstone-data-row'})
        if tombstoneData:
            for row in tombstoneData:
                label = row.findChild('strong')

                if label:
                    content = row.text.replace('\r', ' ').replace('\n', ' ').strip()
                    content = content.replace(label.text, '')
                    content = re.sub('\s+', ' ', content).strip()

                    label   = label.text.strip().lower()
                    label   = label.replace(' ', '_')

                    if label == 'caption':
                        content = content.split('Creative Commons-BY')
                        content = content[0].strip()

                    elif label in ['rights_statement', 'record_completeness', 'image', 'museum_location']:
                        continue

                    elif label == 'catalogue_description':
                        label = 'description'

                    elif label in ['artist', 'maker']:
                        artistInfo = row.findChild('a')

                        if artistInfo:
                            artist = artistInfo.text.split(',')[0].strip()
                            artist = artist.replace('\n', '')

                            if artistInfo.attrs:
                                artistURL = artistInfo.attrs['href']
                                artistURL = 'https://www.brooklynmuseum.org{}'.format(artistURL)

                            if 'unknown' not in artist.lower():
                                self.creator    = artist
                                self.creatorURL = artistURL

                                continue

                    otherMetaData[label] = content

        tagsInfo = soup.find('div', {'class': 'row tags-area'})
        if tagsInfo:
            tagsList    = tagsInfo.findChildren('a')
            tags        = ','.join([tag.text.strip() for tag in tagsList])

            otherMetaData['tags']  = tags


        if otherMetaData:
            self.metaData = otherMetaData


        thumbnails = soup.find_all('div', {'class': 'thumbnail-wrapper'})
        if len(thumbnails) < 1:
            thumbnails = soup.find_all('article', {'class': 'thumbnail-wrapper'}) #backwards compatibility

        if len(thumbnails) > 1:
            otherMetaData['set'] = self.foreignLandingURL
            self.metaData        = otherMetaData

            for thumbnail in thumbnails:
                self.thumbnail          = ''
                self.url                = ''
                self.foreignIdentifier  = ''

                thumb = thumbnail.findChild('a', {'class': 'thumbnail img-responsive'})
                if thumb and 'href' in thumb.attrs:
                    self.thumbnail = thumb.attrs['href'].strip()

                imgInfo = thumbnail.findChild('img', {'class': 'thumbnail img-responsive'})
                if imgInfo and 'data-full-img-url' in imgInfo.attrs:
                    self.url = imgInfo.attrs['data-full-img-url'].strip()

                    if 'data-target' in imgInfo.attrs:
                        self.foreignIdentifier = imgInfo.attrs['data-target']
                    else:
                        self.foreignIdentifier = self.url

                else:
                    continue


                #do not save the image for the 404 page. This is just a precaution, the 'if statement' below never happen
                if 'brooklynmuseum.org/img/CUR.2009.26.jpg' in self.url:
                    continue

                extracted.extend(self.formatOutput)

        else:
            foreignID = None
            if objectID and 'value' in objectID.attrs:
                foreignID = objectID.attrs['value']


            imgInfo = soup.find('a', {'id': 'download-image-link'})
            if imgInfo:
                self.url = imgInfo.attrs['href'].strip()


                #do not save the image for the 404 page. This is just a precaution, the 'if statement' below never happen
                if 'brooklynmuseum.org/img/CUR.2009.26.jpg' in self.url:
                    return None

                thumbURL = re.sub(r'/(size\d{1})/', '/size2/', imgInfo.attrs['href'].strip())
                self.thumbnail = thumbURL

                if foreignID is None:
                    foreignID = self.url

                self.foreignIdentifier = foreignID

                extracted.extend(self.formatOutput)


            else:
                return None


        return extracted


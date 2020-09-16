"""
Content Provider:       Encyclopedia of Life (EOL)

ETL Process:            Identify images, of the various life forms on earth,
                        that are available under any Creative Commons license.

Output:                 TSV file containing images of artworks and their
                        respective meta-data.
"""
from Provider import *
import logging

logging.basicConfig(
    format=(
        '%(asctime)s - %(name)s: [%(levelname)s] - EOL =======> %(message)s'),
    level=logging.INFO)


class EOL(Provider):

    def __init__(self, _name, _domain, _cc_index):
        Provider.__init__(self, _name, _domain, _cc_index)

    def filterData(self, _data, _condition=None):
        data = list(filter(lambda x: filter(
            lambda y: y in x.split('\t')[0],
            ['/pages/', '/data_objects/']), _data))
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
        A tab separated string which contains the meta data that was extracted
        from the HTML.

        """
        # NB: the HTML for this website has been updated (the common crawl data
        # is not the most recent version)
        soup = BeautifulSoup(_html, 'html.parser')
        otherMetaData = {}
        src = None
        license = None
        version = None
        imageURL = None
        tags = None
        extracted = []

        self.clearFields()

        self.provider = self.name
        self.source = 'commoncrawl'

        # get the tags
        tags = soup.find('meta', {'name': 'keywords'})
        if tags:
            otherMetaData['tags'] = self.validateContent('', tags, 'content')

        # title
        title = soup.find('meta', {'property': 'og:title'})
        if title:
            self.title = self.validateContent(
                '', title, 'content').split(' - ')[0].strip()

        currentURL = soup.find('meta', {'property': 'og:url'})
        if currentURL:
            tmpURL = self.validateContent('', currentURL, 'content')
            if '/data_objects/' in _url:
                self.foreignLandingURL = tmpURL
                foreignID = self.getForeignID(tmpURL)
                if foreignID:
                    self.foreignIdentifier = foreignID.strip()

            else:
                otherMetaData['set'] = tmpURL

        # description/summary
        overview = soup.find(
            'div', {'class': re.compile('article( overview)?')})
        if overview:
            details = overview.findChild('div', {'class': 'copy'})
            if details:
                otherMetaData['description'] = details.text.split(
                    '.')[0].strip().replace('<i>', '').replace('</i>', '')

                moreInfo = overview.findChild('div', {'class': 'header'})
                if moreInfo:
                    infoURL = moreInfo.find('a')
                    if infoURL:
                        sdstrip = self.domain.strip('%')
                        otherMetaData['more_information'] = (
                            f'{sdstrip}{infoURL.attrs['href']}')

        # get the image
        if '/data_objects/' in _url:
            img = soup.find('div', {'class': 'media'})
            if img:
                img = img.findChild('a')
                if img:
                    self.url = self.validateContent('', img, 'href')
                else:
                    logging.warning(f'Image not detected in url: {_url}')
                    return None

            # verify the license
            sourceInfo = soup.find('div', {'class': 'article source'})
            if sourceInfo:
                licenseDetails = sourceInfo.findChild(
                    'a', {'href': re.compile('creativecommons.org')})
                if licenseDetails:
                    ccURL = urlparse(licenseDetails.attrs['href'].strip())
                    license, version = self.getLicense(
                        ccURL.netloc, ccURL.path, _url)

                    if not license:
                        logging.warning(f'License not detected in url: {_url}')
                        return None

                    self.license = license
                    self.licenseVersion = version

                # credits
                owner = sourceInfo.find('p', {'title': 'Rights holder'})
                if owner:
                    otherMetaData['rights_holder'] = (
                        owner.text.strip().replace('\\xa9', '').strip())

                articleInfo = sourceInfo.find_all('p', {'title': None})
                if articleInfo:

                    for aInfo in articleInfo:
                        if aInfo:
                            aInfo = re.sub(
                                '<br/>', '</p><p>', aInfo.prettify())
                            aInfo = BeautifulSoup(aInfo, 'html.parser')

                            for tmpInfo in aInfo.find_all('p'):
                                key = tmpInfo.text.split(
                                    ':')[0].lower().strip().replace(' ', '_')
                                key = key.replace('view_source', 'source')

                                sourceURL = None

                                if tmpInfo.findChild('a'):
                                    sourceURL = (
                                        tmpInfo.findChild('a')['href'].strip())

                                    if sourceURL[0] == '/':
                                        sdstrip = self.domain.strip('%')
                                        sourceURL = (f'{sdstrip}{sourceURL}')

                                if key in ['supplier', 'source'] and (
                                        sourceURL is not None):
                                    otherMetaData[key] = sourceURL

                                elif key in [
                                        'publisher', 'contributor',
                                        'location_created', 'photographer',
                                        'author', 'latitude', 'longitude']:
                                    otherMetaData[key] = tmpInfo.text.split(
                                        ':')[1].strip().replace(
                                            '\\xa9', '').strip()
                                    if sourceURL:
                                        otherMetaData[f'{key}_url'] = sourceURL

                                elif key == 'creator':
                                        self.creator = tmpInfo.text.split(
                                            ':')[1].strip().replace(
                                                '\\xa9', '').strip()
                                        if sourceURL:
                                            self.creatorURL = sourceURL

            if otherMetaData:
                self.MetaData = otherMetaData

            formatted = list(self.formatOutput)
            return formatted

        # classification
        classification = soup.find(
            'div', {'class': 'browsable classifications'})
        if classification:
            current = classification.findChild('span', {'class': 'current'})

            if current and current.i:
                otherMetaData['classification'] = current.i.text.strip()

        dataTable = soup.find('div', {'class': 'data_div'})
        if dataTable:
            dataTable = dataTable.find_all('tr')

            for row in dataTable:
                if len(row.find_all('td')) > 1:
                    key = row.th.text.lower().strip().replace(' ', '_')
                    val = row.find_all('td')[1].contents[0].strip()

        # images
        images = soup.find('div', {'class': 'images'})
        if images:
            images = images.find_all('div', {'class': 'image'})

            for imageInfo in images:
                self.foreignIdentifier = ''
                self.foreignLandingURL = ''
                self.thumbnail = ''
                self.url = ''
                self.license = ''
                self.licenseVersion = ''
                self.creator = ''

                if 'image_alt_text' in otherMetaData:
                    del otherMetaData['image_alt_text']

                if 'source' in otherMetaData:
                    del otherMetaData['source']

                if 'supplier' in otherMetaData:
                    del otherMetaData['supplier']

                imgDetails = imageInfo.find('a')
                if imgDetails:
                    foreignID = self.getForeignID(imgDetails.attrs['href'])
                    if foreignID:
                        self.foreignIdentifier = foreignID.strip()

                    # f'{self.domain.strip('%')}{imgDetails.attrs['href'].'
                    # f'strip()}'
                    self.foreignLandingURL = _url

                    imgProperty = imgDetails.findChild('img')
                    if imgProperty:
                        dataID = (
                            imgProperty.attrs['data-data-object-id'].strip())

                        if 'data-thumb' in imgProperty.attrs:
                            self.thumbnail = (
                                imgProperty.attrs['data-thumb'].strip())

                        if 'src' in imgProperty.attrs:
                            self.url = imgProperty.attrs['src'].strip()

                        else:
                            logging.warning(
                                f'Image not detected in url: {_url}')
                            continue

                        if 'alt' in imgProperty.attrs:
                            otherMetaData['image_alt_text'] = (
                                imgProperty.attrs['alt'].strip())
                    else:
                        logging.warning(f'Image not detected in url: {_url}')
                        continue

                        if dataID != foreignID:
                            self.foreignIdentifier = ''

                    # verify license
                    licenseInfo = imageInfo.find(
                        'div', {'class': 'attribution'})
                    if licenseInfo:
                        licenseDetails = licenseInfo.findChild('a')
                        if licenseDetails:
                            ccURL = urlparse(
                                licenseDetails.attrs['href'].strip())
                            license, version = self.getLicense(
                                ccURL.netloc, ccURL.path, _url)

                        if not license:
                            logging.warning(
                                f'License not detected in url: {_url}')
                            continue

                        self.license = license
                        self.licenseVersion = version

                        # credits
                        ownerInfo = licenseInfo.find('div', {'class': 'copy'})
                        if ownerInfo:
                            ownerInfo = ownerInfo.findChildren('p')
                            for owner in ownerInfo:
                                if 'class' in owner.attrs:
                                    self.creator = owner.text.strip() \
                                                        .replace('\\xa9', '') \
                                                        .replace(
                                                        'Copyright', '') \
                                                        .strip()
                                else:
                                    # get the image source or supplier
                                    source = owner.findChild('a')
                                    if source:
                                        srcURL = source.attrs['href'].strip()
                                        if srcURL[0] == '/':
                                            sdstrip = self.domain.strip('%')
                                            srcURL = (f'{sdstrip}{srcURL}')
                                        key = owner.contents[0].lower() \
                                                   .strip().replace(':', '') \
                                                   .replace(' ', '_')
                                        val = srcURL

                                        if (key == 'source') or (
                                                key == 'supplier'):
                                            otherMetaData[key] = val

                    if otherMetaData:
                        self.metaData = otherMetaData

                    extracted.extend(self.formatOutput)

                else:
                    logging.warning(f'Image not detected in url: {_url}')
                    continue

        return extracted

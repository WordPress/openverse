from collections import namedtuple
from datetime import datetime
import logging
import os

from common.licenses import licenses
from common.storage import util
from common.storage import columns

logger = logging.getLogger(__name__)

_IMAGE_TSV_COLUMNS = [
    # The order of this list maps to the order of the columns in the TSV.
    columns.StringColumn(
        name='foreign_identifier', required=False, size=3000, truncate=False
    ),
    columns.URLColumn(
        name='foreign_landing_url', required=True, size=1000
    ),
    columns.URLColumn(
        # `url` in DB
        name='image_url', required=True, size=3000
    ),
    columns.URLColumn(
        # `thumbnail` in DB
        name='thumbnail_url', required=False, size=3000
    ),
    columns.IntegerColumn(
        name='width', required=False
    ),
    columns.IntegerColumn(
        name='height', required=False
    ),
    columns.IntegerColumn(
        name='filesize', required=False
    ),
    columns.StringColumn(
        name='license_', required=True, size=50, truncate=False
    ),
    columns.StringColumn(
        name='license_version', required=True, size=25, truncate=False
    ),
    columns.StringColumn(
        name='creator', required=False, size=2000, truncate=True
    ),
    columns.URLColumn(
        name='creator_url', required=False, size=2000
    ),
    columns.StringColumn(
        name='title', required=False, size=5000, truncate=True
    ),
    columns.JSONColumn(
        name='meta_data', required=False
    ),
    columns.JSONColumn(
        name='tags', required=False
    ),
    columns.BooleanColumn(
        name='watermarked', required=False
    ),
    columns.StringColumn(
        name='provider', required=False, size=80, truncate=False
    ),
    columns.StringColumn(
        name='source', required=False, size=80, truncate=False
    )
]

Image = namedtuple(
    'Image',
    [c.NAME for c in _IMAGE_TSV_COLUMNS]
)

# Filter out tags that exactly match these terms. All terms should be
# lowercase.
TAG_BLACKLIST = {
    'no person',
    'squareformat'
}

# Filter out tags that contain the following terms. All entrees should be
# lowercase.
TAG_CONTAINS_BLACKLIST = {
    'flickriosapp',
    'uploaded',
    ':',
    '=',
    'cc0',
    'by',
    'by-nc',
    'by-nd',
    'by-sa',
    'by-nc-nd',
    'by-nc-sa',
    'pdm'
}


class ImageStore:
    """
    A class that stores image information from a given provider.

    Optional init arguments:
    provider:       String marking the provider in the `image` table of the DB.
    output_file:    String giving a temporary .tsv filename (*not* the
                    full path) where the image info should be stored.
    output_dir:     String giving a path where `output_file` should be placed.
    buffer_length:  Integer giving the maximum number of image information rows
                    to store in memory before writing them to disk.
    """

    def __init__(
            self,
            provider=None,
            output_file=None,
            output_dir=None,
            buffer_length=100
    ):
        logger.info(f'Initialized with provider {provider}')
        self._image_buffer = []
        self._total_images = 0
        self._PROVIDER = provider
        self._BUFFER_LENGTH = buffer_length
        self._NOW = datetime.now()
        self._OUTPUT_PATH = self._initialize_output_path(
            output_dir,
            output_file,
            provider,
        )

    def add_item(
            self,
            foreign_landing_url=None,
            image_url=None,
            thumbnail_url=None,
            license_url=None,
            license_=None,
            license_version=None,
            foreign_identifier=None,
            width=None,
            height=None,
            creator=None,
            creator_url=None,
            title=None,
            meta_data=None,
            raw_tags=None,
            watermarked='f',
            source=None
    ):
        """
        Add information for a single image to the ImageStore.

        Required Arguments:

        foreign_landing_url:  URL of page where the image lives on the
                              source website.
        image_url:            Direct link to the image file

        Semi-Required Arguments

        license_url:      URL of the license for the image on the
                          Creative Commons website.
        license_:         String representation of a Creative Commons
                          license.  For valid options, see
                          `common.license.constants.get_license_path_map()`
        license_version:  Version of the given license.  In the case of
                          the `publicdomain` license, which has no
                          version, one shoud pass
                          `common.license.constants.NO_VERSION` here.

        Note on license arguments: These are 'semi-required' in that
        either a valid `license_url` must be given, or a valid
        `license_`, `license_version` pair must be given. Otherwise, the
        image data will be discarded.

        Optional Arguments:

        thumbnail_url:       Direct link to a thumbnail-sized version of
                             the image
        foreign_identifier:  Unique identifier for the image on the
                             source site.
        width:               in pixels
        height:              in pixels
        creator:             The creator of the image.
        creator_url:         The user page, or home page of the creator.
        title:               Title of the image.
        meta_data:           Dictionary of meta_data about the image.
                             Currently, a key that we prefer to have is
                             `description`. If 'license_url' is included
                             in this dictionary, and `license_url` is
                             given as an argument, the argument will
                             replace the one given in the dictionary.
        raw_tags:            List of tags associated with the image
        watermarked:         A boolean, or 't' or 'f' string; whether or
                             not the image has a noticeable watermark.
        source:              If different from the provider.  This might
                             be the case when we get information from
                             some aggregation of images.  In this case,
                             the `source` argument gives the aggregator,
                             and the `provider` argument in the
                             ImageStore init function is the specific
                             provider of the image.
        """
        image = self._get_image(
            foreign_landing_url=foreign_landing_url,
            image_url=image_url,
            thumbnail_url=thumbnail_url,
            license_url=license_url,
            license_=license_,
            license_version=license_version,
            foreign_identifier=foreign_identifier,
            width=width,
            height=height,
            creator=creator,
            creator_url=creator_url,
            title=title,
            meta_data=meta_data,
            raw_tags=raw_tags,
            watermarked=watermarked,
            source=source
        )
        tsv_row = self._create_tsv_row(image)
        if tsv_row:
            self._image_buffer.append(tsv_row)
            self._total_images += 1
        if len(self._image_buffer) >= self._BUFFER_LENGTH:
            self._flush_buffer()

        return self._total_images

    def commit(self):
        """Writes all remaining images in the buffer to disk."""
        self._flush_buffer()

        return self._total_images

    def _initialize_output_path(self, output_dir, output_file, provider):
        if output_dir is None:
            logger.info(
                'No given output directory.  '
                'Using OUTPUT_DIR from environment.'
            )
            output_dir = os.getenv('OUTPUT_DIR')
        if output_dir is None:
            logger.warning(
                'OUTPUT_DIR is not set in the enivronment.  '
                'Output will go to /tmp.'
            )
            output_dir = '/tmp'

        if output_file is not None:
            output_file = str(output_file)
        else:
            output_file = (
                f'{provider}_{datetime.strftime(self._NOW, "%Y%m%d%H%M%S")}'
                f'.tsv'
            )

        output_path = os.path.join(output_dir, output_file)
        logger.info(f'Output path: {output_path}')
        return output_path

    def _get_total_images(self):
        return self._total_images

    """Get total images for directly using in scripts."""
    total_images = property(_get_total_images)

    def _get_image(
            self,
            foreign_identifier,
            foreign_landing_url,
            image_url,
            thumbnail_url,
            width,
            height,
            license_url,
            license_,
            license_version,
            creator,
            creator_url,
            title,
            meta_data,
            raw_tags,
            watermarked,
            source,
    ):
        valid_license_info = licenses.get_license_info(
            license_url=license_url,
            license_=license_,
            license_version=license_version
        )
        source = util.get_source(source, self._PROVIDER)
        meta_data = self._enrich_meta_data(
            meta_data,
            license_url=valid_license_info.url,
            raw_license_url=license_url
        )
        tags = self._enrich_tags(raw_tags)

        return Image(
            foreign_identifier=foreign_identifier,
            foreign_landing_url=foreign_landing_url,
            image_url=image_url,
            thumbnail_url=thumbnail_url,
            license_=valid_license_info.license,
            license_version=valid_license_info.version,
            width=width,
            height=height,
            filesize=None,
            creator=creator,
            creator_url=creator_url,
            title=title,
            meta_data=meta_data,
            tags=tags,
            watermarked=watermarked,
            provider=self._PROVIDER,
            source=source
        )

    def _create_tsv_row(
            self,
            image,
            columns=_IMAGE_TSV_COLUMNS
    ):
        row_length = len(columns)
        prepared_strings = [
            columns[i].prepare_string(image[i]) for i in range(row_length)
        ]
        logger.debug(f'Prepared strings list:\n{prepared_strings}')
        for i in range(row_length):
            if columns[i].REQUIRED and prepared_strings[i] is None:
                logger.warning(f'Row missing required {columns[i].NAME}')
                return None
        else:
            return '\t'.join(
                [s if s is not None else '\\N' for s in prepared_strings]
            ) + '\n'

    def _flush_buffer(self):
        buffer_length = len(self._image_buffer)
        if buffer_length > 0:
            logger.info(
                f'Writing {buffer_length} lines from buffer to disk.'
            )
            with open(self._OUTPUT_PATH, 'a') as f:
                f.writelines(self._image_buffer)
                self._image_buffer = []
                logger.debug(
                    f'Total Images Processed so far:  {self._total_images}'
                )
        else:
            logger.debug('Empty buffer!  Nothing to write.')
        return buffer_length

    def _tag_blacklisted(self, tag):
        """
        Tag is banned or contains a banned substring.
        :param tag: the tag to be verified against the blacklist
        :return: true if tag is blacklisted, else returns false
        """
        if type(tag) == dict:  # check if the tag is already enriched
            tag = tag.get('name')
        if tag in TAG_BLACKLIST:
            return True
        for blacklisted_substring in TAG_CONTAINS_BLACKLIST:
            if blacklisted_substring in tag:
                return True
        return False

    def _enrich_meta_data(self, meta_data, license_url, raw_license_url):
        if type(meta_data) != dict:
            logger.debug(
                f'`meta_data` is not a dictionary: {meta_data}'
            )
            enriched_meta_data = {
                'license_url': license_url, 'raw_license_url': raw_license_url
            }
        else:
            enriched_meta_data = meta_data
            enriched_meta_data.update(
                license_url=license_url, raw_license_url=raw_license_url
            )
        return enriched_meta_data

    def _enrich_tags(self, raw_tags):
        if type(raw_tags) != list:
            logger.debug('`tags` is not a list.')
            return None
        else:
            return [
                self._format_raw_tag(tag) for tag in raw_tags
                if not self._tag_blacklisted(tag)
            ]

    def _format_raw_tag(self, tag):
        if type(tag) == dict and tag.get('name') and tag.get('provider'):
            logger.debug(f'Tag already enriched: {tag}')
            return tag
        else:
            logger.debug(f'Enriching tag: {tag}')
            return {'name': tag, 'provider': self._PROVIDER}


class MockImageStore(ImageStore):
    """
    A class that mocks the role of the ImageStore class. This class replaces
    all functionality of ImageStore that calls the internet.

    For information about all arguments other than license_info refer to
    ImageStore class.

    Required init arguments:
    license_info:       A named tuple consisting of valid license info from
                        the test script in which MockImageStore is being used.
    """

    def __init__(
            self,
            provider=None,
            output_file=None,
            output_dir=None,
            buffer_length=100,
            license_info=None
    ):
        logger.info(f'Initialized with provider {provider}')
        super().__init__(provider=provider)
        self.license_info = license_info

    def _get_image(
            self,
            foreign_identifier,
            foreign_landing_url,
            image_url,
            thumbnail_url,
            width,
            height,
            license_url,
            license_,
            license_version,
            creator,
            creator_url,
            title,
            meta_data,
            raw_tags,
            watermarked,
            source,
    ):
        valid_license_info = self.license_info

        source = util.get_source(source, self._PROVIDER)
        meta_data = self._enrich_meta_data(
            meta_data,
            license_url=valid_license_info.url,
            raw_license_url=license_url
        )
        tags = self._enrich_tags(raw_tags)

        return Image(
            foreign_identifier=foreign_identifier,
            foreign_landing_url=foreign_landing_url,
            image_url=image_url,
            thumbnail_url=thumbnail_url,
            license_=valid_license_info.license,
            license_version=valid_license_info.version,
            width=width,
            height=height,
            filesize=None,
            creator=creator,
            creator_url=creator_url,
            title=title,
            meta_data=meta_data,
            tags=tags,
            watermarked=watermarked,
            provider=self._PROVIDER,
            source=source
        )

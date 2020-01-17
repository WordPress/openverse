from collections import namedtuple
from datetime import datetime
import logging

from storage import util
from storage import columns

logger = logging.getLogger(__name__)

_IMAGE_TSV_COLUMNS = [
    # The order of this list maps to the order of the columns in the TSV.
    columns.StringColumn(
        name='foreign_identifier',  required=False, size=3000, truncate=False
    ),
    columns.URLColumn(
        name='foreign_landing_url', required=True,  size=1000
    ),
    columns.URLColumn(
        # `url` in DB
        name='image_url',           required=True,  size=3000
    ),
    columns.URLColumn(
        # `thumbnail` in DB
        name='thumbnail_url',       required=False, size=3000
    ),
    columns.IntegerColumn(
        name='width',               required=False
    ),
    columns.IntegerColumn(
        name='height',              required=False
    ),
    columns.IntegerColumn(
        name='filesize',            required=False
    ),
    columns.StringColumn(
        name='license_',            required=True,  size=50,   truncate=False
    ),
    columns.StringColumn(
        name='license_version',     required=True,  size=25,   truncate=False
    ),
    columns.StringColumn(
        name='creator',             required=False, size=2000, truncate=True
    ),
    columns.URLColumn(
        name='creator_url',         required=False, size=2000
    ),
    columns.StringColumn(
        name='title',               required=False, size=5000, truncate=True
    ),
    columns.JSONColumn(
        name='meta_data',           required=False
    ),
    columns.JSONColumn(
        name='tags',                required=False
    ),
    columns.BooleanColumn(
        name='watermarked',         required=False
    ),
    columns.StringColumn(
        name='provider',            required=False, size=80,   truncate=False
    ),
    columns.StringColumn(
        name='source',              required=False, size=80,   truncate=False
    )
]


_Image = namedtuple(
    '_Image',
    [c.NAME for c in _IMAGE_TSV_COLUMNS]
)


class ImageStore:

    def __init__(self, provider=None, output_file_name=None):
        logging.info('Initialized with provider {}'.format(provider))
        self._image_buffer = []
        self._PROVIDER = provider
        self._NOW = datetime.now()
        if output_file_name:
            self._OUTPUT_FILE = output_file_name
        else:
            self._OUTPUT_FILE = '{}_{}.tsv'.format(
                provider, datetime.strftime(self._NOW, '%Y%m%d%H%M%S')
            )
        logging.info('Output file: {}'.format(self._OUTPUT_FILE))

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
            filesize=None,
            creator=None,
            creator_url=None,
            title=None,
            meta_data=None,
            raw_tags=None,
            watermarked='f',
            provider=None,
            source=None,
    ):
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
            filesize=filesize,
            creator=creator,
            creator_url=creator_url,
            title=title,
            meta_data=meta_data,
            raw_tags=raw_tags,
            watermarked=watermarked,
            provider=provider,
            source=source
        )
        if image:
            self._image_buffer.append(self._create_tsv_row(image))

    def commit(self):
        pass

    def _get_image(
            self,
            foreign_identifier=None,
            foreign_landing_url=None,
            image_url=None,
            thumbnail_url=None,
            width=None,
            height=None,
            filesize=None,
            license_url=None,
            license_=None,
            license_version=None,
            creator=None,
            creator_url=None,
            title=None,
            meta_data=None,  # TODO: Check if dict
            raw_tags=None,  # TODO: change to correct format
            watermarked='f',
            provider=None,
            source=None,
    ):
        license_, license_version = util.choose_license_and_version(
            license_url=license_url,
            license_=license_,
            license_version=license_version
        )

        provider, source = util.get_provider_and_source(
            source,
            provider,
            default=self._PROVIDER
        )

        return _Image(
                foreign_identifier=foreign_identifier,
                foreign_landing_url=foreign_landing_url,
                image_url=image_url,
                thumbnail_url=thumbnail_url,
                license_=license_,
                license_version=license_version,
                width=width,
                height=height,
                filesize=filesize,
                creator=creator,
                creator_url=creator_url,
                title=title,
                meta_data=meta_data,  # TODO: Enforce JSON
                tags=raw_tags,  # TODO: format tag list
                watermarked=watermarked,
                provider=provider,
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
        for i in range(row_length):
            if columns[i].REQUIRED and prepared_strings[i] is None:
                return None
        else:
            return '\t'.join(
                [s if s is not None else '\\N' for s in prepared_strings]
            ) + '\n'

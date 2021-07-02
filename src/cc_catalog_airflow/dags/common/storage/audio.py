from collections import namedtuple
import logging
from typing import Optional, Dict, Union

from common.storage import columns
from common.storage.media import MediaStore

logger = logging.getLogger(__name__)

AUDIO_TSV_COLUMNS = [
    # The order of this list maps to the order of the columns in the TSV.
    columns.StringColumn(
        name='foreign_identifier', required=False, size=3000, truncate=False
    ),
    columns.URLColumn(
        name='foreign_landing_url', required=True, size=1000
    ),
    columns.URLColumn(
        # `url` in DB
        name='audio_url', required=True, size=3000
    ),
    columns.URLColumn(
        # `thumbnail` in DB
        name='thumbnail_url', required=False, size=3000
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
        name='watermarked', required=False,
    ),
    columns.StringColumn(
        name='provider', required=False, size=80, truncate=False
    ),
    columns.StringColumn(
        name='source', required=False, size=80, truncate=False
    ),
    columns.StringColumn(
        name="ingestion_type", required=False, size=80, truncate=False
    ),
    columns.IntegerColumn(
        name='duration', required=False
    ),
    columns.IntegerColumn(
        name='bit_rate', required=False,
    ),
    columns.IntegerColumn(
        name='sample_rate', required=False,
    ),
    columns.StringColumn(
        name='category', required=False, size=80, truncate=False,
    ),
    columns.JSONColumn(
        name='genre', required=False,
    ),
    columns.JSONColumn(
        # set name, set thumbnail, position of audio in set, set url
        name='audio_set', required=False,
    ),
    columns.JSONColumn(
        # Alternative files: url, filesize, bit_rate, sample_rate
        name='alt_audio_files', required=False
    ),
]

Audio = namedtuple("Audio", [c.NAME for c in AUDIO_TSV_COLUMNS])


class AudioStore(MediaStore):
    """
    A class that stores audio information from a given provider.

    Optional init arguments:
    provider:       String marking the provider in the `audio` table of the DB.
    output_file:    String giving a temporary .tsv filename (*not* the
                    full path) where the audio info should be stored.
    output_dir:     String giving a path where `output_file` should be placed.
    buffer_length:  Integer giving the maximum number of audio information rows
                    to store in memory before writing them to disk.
    """

    def __init__(
        self,
        provider=None,
        output_file=None,
        output_dir=None,
        buffer_length=100,
        media_type="audio",
        tsv_columns=None,
    ):
        super().__init__(
            provider, output_file, output_dir, buffer_length, media_type
        )
        self.columns = AUDIO_TSV_COLUMNS \
            if tsv_columns is None else tsv_columns

    def add_item(
        self,
        foreign_landing_url: str,
        audio_url: str,
        thumbnail_url: Optional[str] = None,
        license_url: Optional[str] = None,
        license_: Optional[str] = None,
        license_version: Optional[str] = None,
        foreign_identifier: Optional[str] = None,
        creator: Optional[str] = None,
        creator_url: Optional[str] = None,
        title: Optional[str] = None,
        meta_data: Optional[Union[Dict, str]] = None,
        raw_tags: Optional[Union[list, str]] = None,
        watermarked: Optional[bool] = False,
        duration: Optional[int] = None,
        bit_rate: Optional[int] = None,
        sample_rate: Optional[int] = None,
        category: Optional[str] = None,
        genre: Optional[str] = None,
        audio_set: Optional[str] = None,
        set_position: Optional[int] = None,
        set_thumbnail: Optional[str] = None,
        set_url: Optional[str] = None,
        alt_audio_files: Optional[Dict] = None,
        source: Optional[str] = None,
        ingestion_type: Optional[str] = None,
    ):
        """
        Add information for a single audio to the AudioStore.

        Required Arguments:
        foreign_landing_url:  URL of page where the audio lives on the
                              source website.
        audio_url:            Direct link to the audio file

        Semi-Required Arguments
        license_url:      URL of the license for the audio on the
                          Creative Commons website.
        license_:         String representation of a Creative Commons
                          license.  For valid options, see
                          `common.license.constants.get_license_path_map()`
        license_version:  Version of the given license.  In the case of
                          the `publicdomain` license, which has no
                          version, one should pass
                          `common.license.constants.NO_VERSION` here.

        Note on license arguments: These are 'semi-required' in that
        either a valid `license_url` must be given, or a valid
        `license_`, `license_version` pair must be given. Otherwise, the
        audio data will be discarded.

        Optional Arguments:
        thumbnail_url:       Direct link to a thumbnail-sized version of
                             the audio
        foreign_identifier:  Unique identifier for the audio on the
                             source site.
        duration:            in milliseconds
        creator:             The creator of the audio.
        creator_url:         The user page, or home page of the creator.
        title:               Title of the audio.
        meta_data:           Dictionary of meta_data about the audio.
                             Currently, a key that we prefer to have is
                             `description`. If 'license_url' is included
                             in this dictionary, and `license_url` is
                             given as an argument, the argument will
                             replace the one given in the dictionary.
        raw_tags:            List of tags associated with the audio
        source:              If different from the provider.  This might
                             be the case when we get information from
                             some aggregation of audios.  In this case,
                             the `source` argument gives the aggregator,
                             and the `provider` argument in the
                             AudioStore init function is the specific
                             provider of the audio.
        """

        audio_set_data = {
            'audio_set': audio_set,
            'set_url': set_url,
            'set_position': set_position,
            'set_thumbnail': set_thumbnail
        }

        audio_data = {
            'foreign_landing_url': foreign_landing_url,
            'audio_url': audio_url,
            'thumbnail_url': thumbnail_url,
            'license_url': license_url,
            'license_': license_,
            'license_version': license_version,
            'foreign_identifier': foreign_identifier,
            'creator': creator,
            'creator_url': creator_url,
            'title': title,
            'meta_data': meta_data,
            'raw_tags': raw_tags,
            'watermarked': watermarked,
            'duration': duration,
            'bit_rate': bit_rate,
            'sample_rate': sample_rate,
            'category': category,
            'genre': genre,
            'audio_set': audio_set_data,
            'alt_audio_files': alt_audio_files,
            'source': source,
            'ingestion_type': ingestion_type,
        }

        audio = self._get_audio(**audio_data)
        if audio is not None:
            self.save_item(audio)
        return self.total_items

    def _get_audio(self, **kwargs) -> Optional[Audio]:
        """Validates audio information and returns Audio namedtuple"""
        audio_metadata = self.clean_media_metadata(**kwargs)
        if audio_metadata is None:
            return None
        return Audio(**audio_metadata)


class MockAudioStore(AudioStore):
    """
    A class that mocks the role of the AudioStore class. This class replaces
    all functionality of AudioStore that calls the internet.

    For information about all arguments other than license_info refer to
    AudioStore class.

    Required init arguments:
    license_info:       A named tuple consisting of valid license info from
                        the test script in which MockAudioStore is being used.
    """

    def __init__(
        self,
        provider=None,
        output_file=None,
        output_dir=None,
        buffer_length=100,
        license_info=None,
    ):
        logger.info(f"Initialized with provider {provider}")
        super().__init__(provider=provider)
        self.license_info = license_info

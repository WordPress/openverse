import logging
from collections import namedtuple
from typing import Dict, Optional, Union

from common.licenses.licenses import LicenseInfo
from storage.media import MediaStore
from storage.tsv_columns import CURRENT_AUDIO_TSV_COLUMNS


logger = logging.getLogger(__name__)

Audio = namedtuple("Audio", [c.name for c in CURRENT_AUDIO_TSV_COLUMNS])


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
        super().__init__(provider, output_file, output_dir, buffer_length, media_type)
        self.columns = CURRENT_AUDIO_TSV_COLUMNS if tsv_columns is None else tsv_columns

    def add_item(
        self,
        foreign_landing_url: str,
        audio_url: str,
        license_info: LicenseInfo,
        thumbnail_url: Optional[str] = None,
        filesize: Optional[int] = None,
        filetype: Optional[str] = None,
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
        category: Optional[list[str]] = None,
        genres: Optional[list[str]] = None,
        set_foreign_id: Optional[str] = None,
        audio_set: Optional[str] = None,
        set_position: Optional[int] = None,
        set_thumbnail: Optional[str] = None,
        set_url: Optional[str] = None,
        alt_files: Optional[Dict] = None,
        source: Optional[str] = None,
        ingestion_type: Optional[str] = None,
    ):
        """
        Add information for a single audio to the AudioStore.

        Required Arguments:

        foreign_landing_url:  URL of page where the audio lives on the
                              source website.
        audio_url:            Direct link to the audio file
        license_info:         LicenseInfo object that has
                              - the URL of the license for the audio,
                              - string representation of the license,
                              - version of the license,
                              - raw license URL that was by provider,
                                if different from canonical URL
        For valid options of license names, see
        `common.license.constants.get_license_path_map()`.

        To get the LicenseInfo object, use `get_license_info` with either
        (license_ and license_version) or (license_url) named parameters.
        In the case of the `publicdomain` license, which has no version,
        one should pass `common.license.constants.NO_VERSION` here.

        Audio data without the required parameters will be discarded.

        Optional Arguments:

        thumbnail_url:       Direct link to a thumbnail-sized version of
                             the audio.
        filesize:            Size of the main file in bytes
        filetype:            The filetype of the main file, eg. 'mp3', 'ogg'.
        foreign_identifier:  Unique identifier for the audio on the
                             source site.
        creator:             The creator of the audio.
        creator_url:         The user page, or home page of the creator.
        title:               Title of the audio.
        meta_data:           Dictionary of meta_data about the audio.
                             Currently, a key that we prefer to have is
                             `description`. If 'license_url' is included
                             in this dictionary, and `license_url` is
                             given as an argument, the argument will
                             replace the one given in the dictionary.
        raw_tags:            List of tags associated with the audio.
        watermarked:         True only if audio has a watermark.
        duration:            in milliseconds
        bit_rate:            Audio bit rate as int.
        sample_rate:         Audio sample rate as int.
        category:            List of categories such as 'music', 'sound'
                             or 'podcast'.
        genres:              List of genres
        set_foreign_id:      Unique identifier for the audio set on the
                             source site.
        audio_set:           The name of the set (album, pack) the audio
                             is part of
        set_position:        Position of the audio in the audio_set
        set_thumbnail:       URL of the audio_set thumbnail
        set_url:             URL of the audio_set
        alt_files:           A dictionary with information about alternative
                             files for the audio (different formats/ quality).
                             Dict with the following keys: url, filesize,
                             bit_rate, sample_rate
        source:              If different from the provider.  This might
                             be the case when we get information from
                             some aggregation of audios.  In this case,
                             the `source` argument gives the aggregator,
                             and the `provider` argument in the
                             AudioStore init function is the specific
                             provider of the audio.
        ingestion_type:      set programmatically
        """
        if audio_set is None:
            audio_set_data = None
        else:
            audio_set_data = {
                "title": audio_set,
                "foreign_landing_url": set_url,
                "thumbnail": set_thumbnail,
                "creator": creator,
                "creator_url": creator_url,
                "foreign_identifier": set_foreign_id,
            }

        audio_data = {
            "foreign_landing_url": foreign_landing_url,
            "audio_url": audio_url,
            "license_info": license_info,
            "thumbnail_url": thumbnail_url,
            "filesize": filesize,
            "filetype": filetype,
            "foreign_identifier": foreign_identifier,
            "creator": creator,
            "creator_url": creator_url,
            "title": title,
            "meta_data": meta_data,
            "raw_tags": raw_tags,
            "category": category,
            "watermarked": watermarked,
            "duration": duration,
            "bit_rate": bit_rate,
            "sample_rate": sample_rate,
            "genres": genres,
            "audio_set": audio_set_data,
            "set_position": set_position,
            "alt_files": alt_files,
            "source": source,
            "ingestion_type": ingestion_type,
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
        # Convert the `audio_url` key used in AudioStore, TSV and
        # provider API scripts into `url` key used in db
        audio_metadata["url"] = audio_metadata.pop("audio_url")
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

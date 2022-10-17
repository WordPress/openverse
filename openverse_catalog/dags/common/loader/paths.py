import re
from typing import Optional

from common.constants import MEDIA_TYPES


LEGACY_TSV_VERSION = "000"


def _extract_media_type(tsv_file_name: Optional[str]) -> str:
    """
    By default, the filename will be:
    `folder/provider_timestamp.tsv` for older version
    `folder/provider_<media_type>_timestamp.tsv` for newer version
    If we cannot extract `media_type`, we return `image`.
    :param tsv_file_name:
    :return: media type of the staged file, one of
    SUPPORTED_MEDIA_TYPES
    """
    try:
        media_type = tsv_file_name.split("/")[-1].split("_")[1]
        if media_type not in MEDIA_TYPES:
            media_type = "image"
    # None or no underscores
    except (AttributeError, IndexError):
        media_type = "image"
    return media_type


def get_tsv_version(tsv_file_name: str) -> str:
    """TSV file version can be deducted from the filename
    v0: without _vN_ in the filename
    v1+: has a _vN in the filename

    >>>get_tsv_version('/behance_image_20210906130355.tsv')
    '000'
    >>> get_tsv_version('/jamendo_audio_v005_20210906130355.tsv')
    '005'
    """

    version_pattern = re.compile(r"_v(\d+)_")
    if match := re.search(version_pattern, tsv_file_name):
        return match.group(1)
    return LEGACY_TSV_VERSION

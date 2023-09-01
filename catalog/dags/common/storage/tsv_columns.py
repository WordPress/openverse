from common.constants import AUDIO, IMAGE
from common.storage import columns as col
from common.storage.columns import Column
from common.utils import setup_kwargs_for_media_type


# Image has 'legacy' 000 version
# Audio versions start at 001
CURRENT_VERSION = {
    AUDIO: "002",
    IMAGE: "001",
}


# The order of columns in each list maps to the order of the columns in the TSV.
COLUMNS = {
    AUDIO: {
        "001": [
            # Legacy audio tsvs do not have an 'audio_set_foreign_identifier'.
            col.FOREIGN_ID,
            col.LANDING_URL,
            col.DIRECT_URL,
            col.THUMBNAIL,
            col.FILETYPE,
            col.FILESIZE,
            col.LICENSE,
            col.LICENSE_VERSION,
            col.CREATOR,
            col.CREATOR_URL,
            col.TITLE,
            col.META_DATA,
            col.TAGS,
            col.CATEGORY,
            col.WATERMARKED,
            col.PROVIDER,
            col.SOURCE,
            col.INGESTION_TYPE,
            col.DURATION,
            col.BIT_RATE,
            col.SAMPLE_RATE,
            col.GENRES,
            col.AUDIO_SET,
            col.SET_POSITION,
            col.ALT_FILES,
        ],
        "002": [
            col.FOREIGN_ID,
            col.LANDING_URL,
            col.DIRECT_URL,
            col.THUMBNAIL,
            col.FILETYPE,
            col.FILESIZE,
            col.LICENSE,
            col.LICENSE_VERSION,
            col.CREATOR,
            col.CREATOR_URL,
            col.TITLE,
            col.META_DATA,
            col.TAGS,
            col.CATEGORY,
            col.WATERMARKED,
            col.PROVIDER,
            col.SOURCE,
            col.INGESTION_TYPE,
            col.DURATION,
            col.BIT_RATE,
            col.SAMPLE_RATE,
            col.GENRES,
            col.AUDIO_SET,
            col.SET_POSITION,
            col.ALT_FILES,
            col.AUDIO_SET_FOREIGN_IDENTIFIER,
        ],
    },
    IMAGE: {
        # Legacy columns with `ingestion_type` column
        "000": [
            col.FOREIGN_ID,
            col.LANDING_URL,
            col.DIRECT_URL,
            col.THUMBNAIL,
            col.WIDTH,
            col.HEIGHT,
            col.FILESIZE,
            col.LICENSE,
            col.LICENSE_VERSION,
            col.CREATOR,
            col.CREATOR_URL,
            col.TITLE,
            col.META_DATA,
            col.TAGS,
            col.WATERMARKED,
            col.PROVIDER,
            col.SOURCE,
            col.INGESTION_TYPE,
        ],
        "001": [
            col.FOREIGN_ID,
            col.LANDING_URL,
            col.DIRECT_URL,
            col.THUMBNAIL,
            col.FILETYPE,
            col.FILESIZE,
            col.LICENSE,
            col.LICENSE_VERSION,
            col.CREATOR,
            col.CREATOR_URL,
            col.TITLE,
            col.META_DATA,
            col.TAGS,
            col.CATEGORY,
            col.WATERMARKED,
            col.PROVIDER,
            col.SOURCE,
            col.INGESTION_TYPE,
            col.WIDTH,
            col.HEIGHT,
        ],
    },
}

CURRENT_AUDIO_TSV_COLUMNS: list[Column] = COLUMNS[AUDIO][CURRENT_VERSION[AUDIO]]
CURRENT_IMAGE_TSV_COLUMNS: list[Column] = COLUMNS[IMAGE][CURRENT_VERSION[IMAGE]]
# This list is the same for all media types
REQUIRED_COLUMNS = [col for col in CURRENT_IMAGE_TSV_COLUMNS if col.required]


def setup_tsv_columns_for_media_type(func: callable) -> callable:
    """Provide media-type-specific TSV columns as a kwarg to the decorated function."""
    return setup_kwargs_for_media_type(
        {AUDIO: CURRENT_AUDIO_TSV_COLUMNS, IMAGE: CURRENT_IMAGE_TSV_COLUMNS},
        "tsv_columns",
    )(func)

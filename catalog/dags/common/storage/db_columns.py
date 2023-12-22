"""
This module contains the lists of database columns in the same order as in the
main media tables within the database.
"""
from common.constants import AUDIO, IMAGE
from common.storage import columns as col
from common.utils import setup_kwargs_for_media_type


# Columns that are only in the main table;
# not in the TSVs or loading table
NOT_IN_LOADING_TABLE = {
    col.IDENTIFIER,
    col.CREATED_ON,
    col.UPDATED_ON,
    col.LAST_SYNCED,
    col.REMOVED,
}

# The list of columns in main db table in the same order
IMAGE_TABLE_COLUMNS = [
    col.IDENTIFIER,
    col.CREATED_ON,
    col.UPDATED_ON,
    col.INGESTION_TYPE,
    col.PROVIDER,
    col.SOURCE,
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
    col.LAST_SYNCED,
    col.REMOVED,
    col.FILETYPE,
    col.CATEGORY,
    col.STANDARDIZED_POPULARITY,
]

AUDIO_TABLE_COLUMNS = [
    col.IDENTIFIER,
    col.CREATED_ON,
    col.UPDATED_ON,
    col.INGESTION_TYPE,
    col.PROVIDER,
    col.SOURCE,
    col.FOREIGN_ID,
    col.LANDING_URL,
    col.DIRECT_URL,
    col.THUMBNAIL,
    col.FILESIZE,
    col.LICENSE,
    col.LICENSE_VERSION,
    col.CREATOR,
    col.CREATOR_URL,
    col.TITLE,
    col.META_DATA,
    col.TAGS,
    col.WATERMARKED,
    col.LAST_SYNCED,
    col.REMOVED,
    col.DURATION,
    col.BIT_RATE,
    col.SAMPLE_RATE,
    col.CATEGORY,
    col.GENRES,
    col.AUDIO_SET,
    col.SET_POSITION,
    col.ALT_FILES,
    col.FILETYPE,
    col.STANDARDIZED_POPULARITY,
    col.AUDIO_SET_FOREIGN_IDENTIFIER,
]


DB_COLUMNS_BY_MEDIA_TYPE = {AUDIO: AUDIO_TABLE_COLUMNS, IMAGE: IMAGE_TABLE_COLUMNS}


def setup_db_columns_for_media_type(func: callable) -> callable:
    """Provide media-type-specific DB columns as a kwarg to the decorated function."""
    return setup_kwargs_for_media_type(DB_COLUMNS_BY_MEDIA_TYPE, "db_columns")(func)


DELETED_IMAGE_TABLE_COLUMNS = IMAGE_TABLE_COLUMNS + [col.DELETED_ON, col.DELETED_REASON]
DELETED_AUDIO_TABLE_COLUMNS = AUDIO_TABLE_COLUMNS + [col.DELETED_ON, col.DELETED_REASON]

DELETED_MEDIA_DB_COLUMNS_BY_MEDIA_TYPE = {
    AUDIO: DELETED_AUDIO_TABLE_COLUMNS,
    IMAGE: DELETED_IMAGE_TABLE_COLUMNS,
}


def setup_deleted_db_columns_for_media_type(func: callable) -> callable:
    """
    Provide media-type-specific deleted media DB columns as a kwarg to the decorated
    function.
    """
    return setup_kwargs_for_media_type(
        DELETED_MEDIA_DB_COLUMNS_BY_MEDIA_TYPE, "deleted_db_columns"
    )(func)

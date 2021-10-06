"""
This module contains the lists of database columns
in the same order as in the main image / audio databases.
"""
from storage import columns as col


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
]

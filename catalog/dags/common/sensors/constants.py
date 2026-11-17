from common.constants import PRODUCTION, STAGING


# These DagTags are used to identify DAGs which should not be run concurrently
# with one another.

# Used to identify DAGs for each environment which affect the Elasticsearch cluster
# and should not be run simultaneously
PRODUCTION_ES_CONCURRENCY_TAG = "production_elasticsearch_concurrency"
STAGING_ES_CONCURRENCY_TAG = "staging_elasticsearch_concurrency"

# Used to identify DAGs which affect the staging API database in such a
# way that they should not be run simultaneously
STAGING_DB_CONCURRENCY_TAG = "staging_api_database_concurrency"

ES_CONCURRENCY_TAGS = {
    PRODUCTION: PRODUCTION_ES_CONCURRENCY_TAG,
    STAGING: STAGING_ES_CONCURRENCY_TAG,
}

# The DAGs that have each concurrency tag. Tasks cannot look tags up in the metadata
# database, so they are listed here, and the DAG parsing tests check that this
# matches the tags the DAGs actually have.
CONCURRENCY_TAG_DAG_IDS = {
    PRODUCTION_ES_CONCURRENCY_TAG: [
        "audio_data_refresh",
        "create_filtered_audio_index",
        "create_filtered_image_index",
        "create_new_production_es_index",
        "image_data_refresh",
        "point_production_es_alias",
        "production_audio_data_refresh",
        "production_image_data_refresh",
    ],
    STAGING_ES_CONCURRENCY_TAG: [
        "create_new_staging_es_index",
        "create_proportional_by_source_staging_index",
        "point_staging_es_alias",
        "recreate_full_staging_index",
        "staging_audio_data_refresh",
        "staging_image_data_refresh",
    ],
    STAGING_DB_CONCURRENCY_TAG: [
        "recreate_full_staging_index",
        "staging_audio_data_refresh",
        "staging_database_restore",
        "staging_image_data_refresh",
    ],
}

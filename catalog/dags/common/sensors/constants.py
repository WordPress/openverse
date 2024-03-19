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

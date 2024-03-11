from common.constants import PRODUCTION, STAGING


# DagTags used to establish a concurrency group for each environment
PRODUCTION_ES_CONCURRENCY_TAG = "production_es_concurrency"
STAGING_ES_CONCURRENCY_TAG = "staging_es_concurrency"

ES_CONCURRENCY_TAGS = {
    PRODUCTION: PRODUCTION_ES_CONCURRENCY_TAG,
    STAGING: STAGING_ES_CONCURRENCY_TAG,
}

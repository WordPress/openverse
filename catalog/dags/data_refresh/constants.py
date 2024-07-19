from common.constants import PRODUCTION, STAGING


INDEXER_WORKER_COUNTS = {STAGING: 2, PRODUCTION: 6}

INDEXER_LAUNCH_TEMPLATES = {
    STAGING: "indexer-worker-pool-s",
    PRODUCTION: "indexer-worker-pool-p",
}

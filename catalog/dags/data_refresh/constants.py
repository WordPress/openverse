from common.constants import PRODUCTION, STAGING


INDEXER_WORKER_COUNTS = {STAGING: 2, PRODUCTION: 6}

INDEXER_WORKER_PORT = 8003

# Seconds to wait for the indexer worker API to respond to a request
INDEXER_WORKER_REQUEST_TIMEOUT = 60

INDEXER_LAUNCH_TEMPLATES = {
    STAGING: "indexer-worker-pool-s",
    PRODUCTION: "indexer-worker-pool-p",
}

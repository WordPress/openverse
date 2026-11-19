from datetime import timedelta

from common.constants import PRODUCTION, STAGING


INDEXER_WORKER_COUNTS = {STAGING: 2, PRODUCTION: 6}

INDEXER_WORKER_PORT = 8003

# Seconds to wait for the indexer worker API to respond to a request
INDEXER_WORKER_REQUEST_TIMEOUT = 60

# Retries for a reindex status check that fails, for example on a dropped connection
WAIT_FOR_REINDEXING_RETRIES = 3
WAIT_FOR_REINDEXING_RETRY_DELAY = timedelta(minutes=2)

INDEXER_LAUNCH_TEMPLATES = {
    STAGING: "indexer-worker-pool-s",
    PRODUCTION: "indexer-worker-pool-p",
}

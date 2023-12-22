"""Settings very specific to Openverse, used inside the API app."""

import hashlib

from decouple import config


FILTER_DEAD_LINKS_BY_DEFAULT = config(
    "FILTER_DEAD_LINKS_BY_DEFAULT", cast=bool, default=True
)

ENABLE_FILTERED_INDEX_QUERIES = config(
    "ENABLE_FILTERED_INDEX_QUERIES", cast=bool, default=False
)

# Whether to enable the image watermark endpoint
WATERMARK_ENABLED = config("WATERMARK_ENABLED", default=False, cast=bool)

# Log full Elasticsearch response
VERBOSE_ES_RESPONSE = config("DEBUG_SCORES", default=False, cast=bool)

# Whether to boost results by authority and popularity
USE_RANK_FEATURES = config("USE_RANK_FEATURES", default=True, cast=bool)

# The scheme to use for the hyperlinks in the API responses
API_LINK_SCHEME = config("API_LINK_SCHEME", default=None)

# The version of the API. The name is a bit misleading because we do not follow
# the semantic version specification.
API_VERSION = config("SEMANTIC_VERSION", default=hashlib.sha1(b"openverse").hexdigest())

OUTBOUND_USER_AGENT_TEMPLATE = config(
    "OUTBOUND_USER_AGENT_TEMPLATE",
    default=f"Openverse{{purpose}}/{API_VERSION} (https://wordpress.org/openverse)",
)

MAX_ANONYMOUS_PAGE_SIZE = 20
MAX_AUTHED_PAGE_SIZE = 500
MAX_PAGINATION_DEPTH = 20

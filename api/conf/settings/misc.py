"""Settings very specific to Openverse, used inside the API app."""

from decouple import config


SHOW_COLLECTION_DOCS = config("SHOW_COLLECTION_DOCS", cast=bool, default=True)

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

# The version of the API. We follow the semantic version specification.
API_VERSION = config("SEMANTIC_VERSION", default="Version not specified")

OUTBOUND_USER_AGENT_TEMPLATE = config(
    "OUTBOUND_USER_AGENT_TEMPLATE",
    default=f"Openverse{{purpose}}/{API_VERSION} (https://wordpress.org/openverse)",
)

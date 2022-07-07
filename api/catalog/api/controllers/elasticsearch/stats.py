import json
import logging
from typing import Literal

from django.core.cache import cache

from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import Search


parent_logger = logging.getLogger(__name__)


SOURCE_CACHE_TIMEOUT = 60 * 20  # seconds


def get_stats(index: Literal["image", "audio"]):
    """
    Given an index, find all available data sources and return their counts. This data
    is cached in Redis. See ``load_sample_data.sh`` for example of clearing the cache.

    :param index: the Elasticsearch index name
    :return: a dictionary mapping sources to the count of their media items
    """
    logger = parent_logger.getChild("get_stats")
    source_cache_name = "sources-" + index
    try:
        logger.debug(f"fetching source cache key={source_cache_name}")
        sources = cache.get(key=source_cache_name)
        if sources is not None:
            logger.debug(f"cache hit! returning sources={json.dumps(sources)}")
            return sources
        else:
            logger.debug("cache missed")
    except ValueError:
        # TODO: Improve error handling here.
        # What failed? Why? Do we need to address it?
        # Is this a critical issue? Why is this a "warning"?
        logger.warning("Source cache fetch failed")

    # Don't increase `size` without reading this issue first:
    # https://github.com/elastic/elasticsearch/issues/18838
    size = 100
    try:
        s = Search(using="default", index=index)
        s.aggs.bucket(
            "unique_sources",
            "terms",
            field="source.keyword",
            size=size,
            order={"_key": "desc"},
        )
        results = s.execute()
        buckets = results["aggregations"]["unique_sources"]["buckets"]
        sources = {result["key"]: result["doc_count"] for result in buckets}
    except NotFoundError:
        sources = {}

    if sources:
        logger.info(f"putting sources to cache key={source_cache_name}")
        cache.set(key=source_cache_name, timeout=SOURCE_CACHE_TIMEOUT, value=sources)

    logger.debug(f"sources={json.dumps(sources)}")
    return sources

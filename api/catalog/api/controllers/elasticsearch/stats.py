import logging as log
from typing import Literal

from django.core.cache import cache

from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import Search


SOURCE_CACHE_TIMEOUT = 60 * 20  # seconds


def get_stats(index: Literal["image", "audio"]):
    """
    Given an index, find all available data sources and return their counts. This data
    is cached in Redis. See ``load_sample_data.sh`` for example of clearing the cache.

    :param index: the Elasticsearch index name
    :return: a dictionary mapping sources to the count of their media items
    """

    source_cache_name = "sources-" + index
    try:
        sources = cache.get(key=source_cache_name)
        if sources is not None:
            return sources
    except ValueError:
        log.warning("Source cache fetch failed")

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
        cache.set(key=source_cache_name, timeout=SOURCE_CACHE_TIMEOUT, value=sources)

    return sources

from __future__ import annotations

import re
from math import ceil
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.cache import cache

import structlog
from decouple import config
from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import Q, Search
from elasticsearch_dsl.query import EMPTY_QUERY
from elasticsearch_dsl.response import Hit, Response
from redis.exceptions import ConnectionError

import api.models as models
from api.constants.media_types import OriginIndex, SearchIndex
from api.constants.search import SearchStrategy
from api.constants.sorting import INDEXED_ON
from api.controllers.elasticsearch.helpers import (
    ELASTICSEARCH_MAX_RESULT_WINDOW,
    get_es_response,
    get_query_slice,
    get_raw_es_response,
)
from api.utils import tallies
from api.utils.check_dead_links import check_dead_links
from api.utils.dead_link_mask import get_query_hash
from api.utils.search_context import SearchContext


# Using TYPE_CHECKING to avoid circular imports when importing types
if TYPE_CHECKING:
    from api.serializers.media_serializers import MediaSearchRequestSerializer

logger = structlog.get_logger(__name__)


NESTING_THRESHOLD = config("POST_PROCESS_NESTING_THRESHOLD", cast=int, default=5)
SOURCE_CACHE_TIMEOUT = 60 * 60 * 4  # 4 hours
FILTER_CACHE_TIMEOUT = 30
ENABLED_SOURCES_CACHE_KEY = "enabled_sources"
ENABLED_SOURCES_CACHE_VERSION = 2
DEFAULT_BOOST = 10000
DEFAULT_SEARCH_FIELDS = ["title", "description", "tags.name"]
DEFAULT_SQS_FLAGS = "AND|NOT|PHRASE|WHITESPACE"
UNUSED_SQS_FLAGS = [
    ("PRECEDENCE", r"\(.*\)"),
    ("ESCAPE", r"\\"),
    ("FUZZY|SLOP", r"~\d"),
    ("PREFIX", r"\*"),
]


def _quote_escape(query_string):
    """Ignore any unmatched quotes in the query supplied by the user."""

    num_quotes = query_string.count('"')
    if num_quotes % 2 == 1:
        return query_string.replace('"', '\\"')
    else:
        return query_string


def _post_process_results(
    s, start, end, page_size, search_results, filter_dead, nesting=0
) -> list[Hit] | None:
    """
    Perform some steps on results fetched from the backend.

    After fetching the search results from the back end, iterate through the
    results, perform image validation, and route certain thumbnails through our
    proxy.

    Keeps making new query requests until it is able to fill the page size.

    :param s: The Elasticsearch Search object.
    :param start: The start of the result slice.
    :param end: The end of the result slice.
    :param search_results: The Elasticsearch response object containing search
    results.
    :param filter_dead: Whether images should be validated.
    :param nesting: the level of nesting at which this function is being called
    :return: List of results.
    """

    if nesting > NESTING_THRESHOLD:
        logger.info(
            "Nesting threshold breached",
            nesting=nesting,
            start=start,
            end=end,
            page_size=page_size,
        )

    results = list(search_results)

    if filter_dead:
        to_validate = [res.url for res in search_results]
        query_hash = get_query_hash(s)
        check_dead_links(query_hash, start, results, to_validate)

        if len(results) == 0:
            # first page is all dead links
            return None

        if len(results) < page_size:
            """
            The variables in this function get updated in an interesting way.
            Here is an example of that for a typical query. Note that ``end``
            increases but start stays the same. This has the effect of slowly
            increasing the size of the query we send to Elasticsearch with the
            goal of backfilling the results until we have enough valid (live)
            results to fulfill the requested page size.

            ```
            page_size: 20
            page: 1

            start: 0
            end: 40 (DEAD_LINK_RATIO applied)

            end gets updated to end + end/2 = 60

            end = 90
            end = 90 + 45
            ```
            """
            if end >= search_results.hits.total.value:
                # Total available hits already exhausted in previous iteration
                return results

            end += int(end / 2)
            query_size = start + end
            if query_size > ELASTICSEARCH_MAX_RESULT_WINDOW:
                return results

            # subtract start to account for the records skipped
            # and which should not count towards the total
            # available hits for the query
            total_available_hits = search_results.hits.total.value - start
            if query_size > total_available_hits:
                # Clamp the query size to last available hit. On the next
                # iteration, if results are still insufficient, the check
                # to compare previous_query_size and total_available_hits
                # will prevent further query attempts
                end = search_results.hits.total.value

            s = s[start:end]
            search_response = get_es_response(s, es_query="postprocess_search")

            return _post_process_results(
                s, start, end, page_size, search_response, filter_dead, nesting + 1
            )

    return results[:page_size]


def get_enabled_sources_query() -> Q | None:
    """
    Get a query that only includes enabled sources.

    To exclude a source, set ``filter_content`` to ``True`` in the
    ``ContentProvider`` model in Django admin.
    The list of ``provider_identifier``s is cached in Redis with
    `:ENABLED_SOURCES_CACHE_VERSION:ENABLED_SOURCES_CACHE_KEY` key.
    """

    try:
        enabled_sources = cache.get(
            key=ENABLED_SOURCES_CACHE_KEY, version=ENABLED_SOURCES_CACHE_VERSION
        )
    except ConnectionError:
        logger.warning("Redis connect failed, cannot get cached enabled sources.")
        enabled_sources = None

    if not enabled_sources:
        # `ContentProvider` currently only handles _sources_, not providers.
        # TODO: This is a legacy naming convention that should be updated.
        # https://github.com/WordPress/openverse/issues/4346
        enabled_sources = list(
            models.ContentProvider.objects.filter(filter_content=False).values_list(
                "provider_identifier", flat=True
            )
        )

        try:
            cache.set(
                key=ENABLED_SOURCES_CACHE_KEY,
                version=ENABLED_SOURCES_CACHE_VERSION,
                timeout=FILTER_CACHE_TIMEOUT,
                value=enabled_sources,
            )
        except ConnectionError:
            logger.warning("Redis connect failed, cannot cache enabled sources.")

    if enabled_sources:
        return Q("terms", source=enabled_sources)
    return None


def get_index(
    exact_index: bool,
    origin_index: OriginIndex,
    search_params: MediaSearchRequestSerializer,
) -> SearchIndex:
    if exact_index:
        return origin_index

    include_sensitive_results = search_params.validated_data.get(
        "include_sensitive_results", False
    )
    if settings.ENABLE_FILTERED_INDEX_QUERIES and not include_sensitive_results:
        return f"{origin_index}-filtered"
    return origin_index


def create_search_filter_queries(
    search_params: MediaSearchRequestSerializer,
) -> dict[str, list[Q]]:
    """
    Create a list of Elasticsearch queries for filtering search results.
    The filter values are given in the request query string.
    We use ES filters (`filter`, `must_not`) because we don't need to
    compute the relevance score and the queries are cached for better
    performance.
    """
    queries = {"filter": [], "must_not": []}
    # Apply term filters. Each tuple pairs a filter's parameter name in the API
    # with its corresponding field in Elasticsearch. "None" means that the
    # names are identical.
    query_filters = {
        "filter": [
            ("extension", None),
            ("category", None),
            ("source", None),
            ("license", None),
            ("license_type", "license"),
            # Audio-specific filters
            ("length", None),
            # Image-specific filters
            ("aspect_ratio", None),
            ("size", None),
        ],
        "must_not": [
            ("excluded_source", "source"),
        ],
    }
    for behaviour, filters in query_filters.items():
        for serializer_field, es_field in filters:
            if not (arguments := search_params.data.get(serializer_field)):
                continue
            arguments = arguments.split(",")
            parameter = es_field or serializer_field
            queries[behaviour].append(Q("terms", **{parameter: arguments}))
    return queries


def create_ranking_queries(
    search_params: MediaSearchRequestSerializer,
) -> list[Q]:
    queries = [Q("rank_feature", field="standardized_popularity", boost=DEFAULT_BOOST)]
    if search_params.data["unstable__authority"]:
        boost = int(search_params.data["unstable__authority_boost"] * DEFAULT_BOOST)
        authority_query = Q("rank_feature", field="authority_boost", boost=boost)
        queries.append(authority_query)
    return queries


def build_search_query(
    search_params: MediaSearchRequestSerializer,
) -> Q:
    # Apply filters from the url query search parameters.
    url_queries = create_search_filter_queries(search_params)
    search_queries = {
        "filter": url_queries["filter"],
        "must_not": url_queries["must_not"],
        "must": [],
        "should": [],
    }

    # Exclude mature content
    if not search_params.validated_data["include_sensitive_results"]:
        search_queries["must_not"].append(Q("term", mature=True))
    # Exclude dynamically disabled sources (see Redis cache)
    if enabled_sources_query := get_enabled_sources_query():
        search_queries["filter"].append(enabled_sources_query)

    # Search either by generic multimatch or by "advanced search" with
    # individual field-level queries specified.
    if "q" in search_params.data:
        query = _quote_escape(search_params.data["q"])
        log_query_features(query, query_name="q")

        base_query_kwargs = {
            "query": query,
            "flags": DEFAULT_SQS_FLAGS,
            "fields": DEFAULT_SEARCH_FIELDS,
            "default_operator": "AND",
        }

        if '"' in query:
            base_query_kwargs["quote_field_suffix"] = ".raw"

        search_queries["must"].append(Q("simple_query_string", **base_query_kwargs))
        # Boost exact matches on the title
        quotes_stripped = query.replace('"', "")
        exact_match_boost = Q(
            "simple_query_string",
            flags=DEFAULT_SQS_FLAGS,
            fields=["title"],
            query=f"{quotes_stripped}",
            boost=10000,
        )
        search_queries["should"].append(exact_match_boost)
    else:
        for field, field_name in [
            ("creator", "creator"),
            ("title", "title"),
            ("tags", "tags.name"),
        ]:
            if field_value := search_params.data.get(field):
                log_query_features(field_value, query_name="field")
                search_queries["must"].append(
                    Q(
                        "simple_query_string",
                        flags=DEFAULT_SQS_FLAGS,
                        query=_quote_escape(field_value),
                        fields=[field_name],
                    )
                )

    if settings.USE_RANK_FEATURES:
        search_queries["should"].extend(create_ranking_queries(search_params))

    # If there are no `must` query clauses, only the results that match
    # the `should` clause are returned. To avoid this, we add an empty
    # query clause to the `must` list.
    if not search_queries["must"]:
        search_queries["must"].append(EMPTY_QUERY)

    return Q(
        "bool",
        filter=search_queries["filter"],
        must_not=search_queries["must_not"],
        must=search_queries["must"],
        should=search_queries["should"],
    )


def log_query_features(query: str, query_name) -> None:
    query_flags = []
    for flag, pattern in UNUSED_SQS_FLAGS:
        if bool(re.search(pattern, query)):
            query_flags.append(flag)
    if query_flags:
        logger.info(
            {
                "log_message": "Special features present in query",
                "query_name": query_name,
                "query": query,
                "flags": query_flags,
            }
        )


def build_collection_query(
    search_params: MediaSearchRequestSerializer,
):
    """
    Build the query to retrieve items in a collection.
    :param search_params: the validated search parameters.
    :return: the search client with the query applied.
    """
    search_query = {"filter": [], "must": [], "should": [], "must_not": []}

    # Apply the term filters. Each tuple pairs a filter's parameter name in the API
    # with its corresponding field in Elasticsearch. "None" means that the
    # names are identical.
    filters = [
        ("tag", "tags.name.keyword"),
        ("source", None),
        ("creator", "creator.keyword"),
    ]
    for serializer_field, es_field in filters:
        if argument := search_params.validated_data.get(serializer_field):
            parameter = es_field or serializer_field
            search_query["filter"].append({"term": {parameter: argument}})

    # Exclude mature content and disabled sources
    include_sensitive_by_params = search_params.validated_data.get(
        "include_sensitive_results", False
    )
    if not include_sensitive_by_params:
        search_query["must_not"].append({"term": {"mature": True}})

    if enabled_sources_query := get_enabled_sources_query():
        search_query["filter"].append(enabled_sources_query)

    return Q("bool", **search_query)


query_builders = {
    "search": build_search_query,
    "collection": build_collection_query,
}


def query_media(
    search_params: MediaSearchRequestSerializer,
    origin_index: OriginIndex,
    exact_index: bool,
    page_size: int,
    ip: int,
    filter_dead: bool,
    page: int = 1,
) -> tuple[list[Hit], int, int, dict]:
    """
    Build the search or collection query, execute it and return
    paginated result.
    For queries with `collection` parameter, returns media filtered
    by the `tag`, `source` or `source`/`creator` combination, ordered
    by the time when they were added to Openverse.
    For other queries, performs a ranked paginated search
    from the set of keywords and, optionally, filters.

    :param search_params: Search query params, see :class: `MediaSearchRequestSerializer`.
    :param origin_index: The Elasticsearch index to search (e.g. 'image')
    :param exact_index: whether to skip all modifications to the index name
    :param page_size: The number of results to return per page.
    :param ip: The user's hashed IP. Hashed IPs are used to anonymously but
    uniquely identify users exclusively for ensuring query consistency across
    Elasticsearch shards.
    :param filter_dead: Whether dead links should be removed.
    :param page: The results page number.
    :return: Tuple with a list of Hits from elasticsearch, the total count of
    pages, the number of results, and the ``SearchContext`` as a dict.
    """
    index = get_index(exact_index, origin_index, search_params)

    strategy: SearchStrategy = (
        "collection" if search_params.validated_data.get("collection") else "search"
    )

    query = query_builders[strategy](search_params)

    s = Search(index=index).query(query)

    if strategy == "search":
        # Use highlighting to determine which fields contribute to the selection of
        # top results.
        s = s.highlight(*DEFAULT_SEARCH_FIELDS)
        s = s.highlight_options(order="score")
        s.extra(track_scores=True)

    # Route users to the same Elasticsearch worker node to reduce
    # pagination inconsistencies and increase cache hits.
    # TODO: Re-add 7s request_timeout when ES stability is restored
    s = s.params(preference=str(ip))

    # Sort by `created_on` if the parameter is set or if `strategy` is `collection`.
    sort_by = search_params.validated_data.get("sort_by")
    if strategy == "collection" or sort_by == INDEXED_ON:
        sort_dir = search_params.validated_data.get("sort_dir", "desc")
        s = s.sort({"created_on": {"order": sort_dir}})

    # Execute paginated search and tally results
    page_count, result_count, results = execute_search(
        s, page, page_size, filter_dead, index, es_query=strategy
    )

    result_ids = [result.identifier for result in results]
    search_context = SearchContext.build(result_ids, origin_index)

    return results, page_count, result_count, search_context.asdict()


def tally_results(
    index: SearchIndex, results: list[Hit] | None, page: int, page_size: int
) -> None:
    """
    Tally the number of the results from each provider in the results
    for the search query.
    """
    results_to_tally = results or []
    max_result_depth = page * page_size
    if max_result_depth <= 80:
        # Applies when `page_size * page` could land "evenly" on 80
        should_tally = True
    elif max_result_depth - page_size < 80:
        # Applies when `page_size * page` could land beyond 80, but still
        # encompass some results on _this page_ that are at or below the 80th
        # position. For example: page=7 page_size=12 result depth=84.
        # While max_result_depth exceeds 80, we still want to count
        # the first eight results in `results` that are below or at the 80th
        # position for the query.
        should_tally = True
        results_to_tally = results_to_tally[: 80 - (max_result_depth - page_size)]
    else:
        should_tally = False

    if results and should_tally:
        # We ignore tallies for deep results because they're not likely to
        # be as important for search relevancy for most users at this point
        # 80 is chosen because it represents the first four pages of the
        # default page count of 20 (20 * 4) which is how our own frontend
        # makes requests and displays results. Because that is the only
        # place we can actually conceivably measure relevancy down the
        # line, it is the only sensible, controlled space we can use to
        # check things like provider density for a set of queries.
        tallies.count_provider_occurrences(results_to_tally, index)


def execute_search(
    s: Search,
    page: int,
    page_size: int,
    filter_dead: bool,
    index: SearchIndex,
    es_query: str,
) -> tuple[int, int, list[Hit]]:
    """
    Execute search for the given query slice, post-processes the results,
    and returns the results and result and page counts.
    """
    start, end = get_query_slice(s, page_size, page, filter_dead)
    s = s[start:end]

    search_response = get_es_response(s, es_query=es_query)

    results: list[Hit] = (
        _post_process_results(s, start, end, page_size, search_response, filter_dead)
        or []
    )
    result_count, page_count = _get_result_and_page_count(
        search_response, results, page_size, page
    )
    tally_results(index, results, page, page_size)
    return page_count, result_count, results


def get_sources(index):
    """
    Given an index, find all available data sources and return their counts.

    :param index: An Elasticsearch index, such as `'image'`.
    :return: A dictionary mapping sources to the count of their images.`
    """
    source_cache_name = "sources-" + index
    cache_fetch_failed = False
    try:
        sources = cache.get(key=source_cache_name)
    except ValueError:
        cache_fetch_failed = True
        sources = None
        logger.warning("Source cache fetch failed due to corruption")
    except ConnectionError:
        cache_fetch_failed = True
        sources = None
        logger.warning("Redis connect failed, cannot get cached sources.")

    if isinstance(sources, list) or cache_fetch_failed:
        sources = None
        try:
            # Invalidate old provider format.
            cache.delete(key=source_cache_name)
        except ConnectionError:
            logger.warning("Redis connect failed, cannot invalidate cached sources.")

    if not sources:
        # Don't increase `size` without reading this issue first:
        # https://github.com/elastic/elasticsearch/issues/18838
        size = 100
        body = {
            "size": 0,
            "aggs": {
                "unique_sources": {
                    "terms": {
                        "field": "source",
                        "size": size,
                        "order": {"_key": "desc"},
                    }
                }
            },
        }
        try:
            results = get_raw_es_response(
                index=index,
                body=body,
                request_cache=True,
                es_query="sources",
            )
            buckets = results["aggregations"]["unique_sources"]["buckets"]
        except NotFoundError:
            buckets = [{"key": "none_found", "doc_count": 0}]
        sources = {result["key"]: result["doc_count"] for result in buckets}

        try:
            cache.set(
                key=source_cache_name, timeout=SOURCE_CACHE_TIMEOUT, value=sources
            )
        except ConnectionError:
            logger.warning("Redis connect failed, cannot cache sources.")

    sources = {source: int(doc_count) for source, doc_count in sources.items()}
    return sources


def _get_result_and_page_count(
    response_obj: Response, results: list[Hit] | None, page_size: int, page: int
) -> tuple[int, int]:
    """
    Adjust page count because ES disallows deep pagination of ranked queries.

    :param response_obj: The original Elasticsearch response object.
    :param results: The list of filtered result Hits.
    :return: Result and page count.
    """
    if not results:
        return 0, 0

    result_count = response_obj.hits.total.value
    page_count = ceil(result_count / page_size)

    if len(results) < page_size:
        if page_count == 1:
            result_count = len(results)

        # If we have fewer results than the requested page size and are
        # not on the first page that means that we've reached the end of
        # the query and can set the page_count to the currently requested
        # page. This means that the `page_count` can change during
        # pagination for the same query, but it's the only way to
        # communicate under the current v1 API that a query has been exhausted.
        page_count = page

    return result_count, page_count

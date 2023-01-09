from __future__ import annotations

import json
import logging as log
import pprint
from itertools import accumulate
from math import ceil
from typing import Any, Literal

from django.conf import settings
from django.core.cache import cache
from rest_framework.request import Request

from elasticsearch.exceptions import NotFoundError, RequestError
from elasticsearch_dsl import Q, Search
from elasticsearch_dsl.query import EMPTY_QUERY, MoreLikeThis, Query
from elasticsearch_dsl.response import Hit, Response

import catalog.api.models as models
from catalog.api.utils.dead_link_mask import get_query_hash, get_query_mask
from catalog.api.utils.validate_images import validate_images


ELASTICSEARCH_MAX_RESULT_WINDOW = 10000
SOURCE_CACHE_TIMEOUT = 60 * 20
FILTER_CACHE_TIMEOUT = 30
DEAD_LINK_RATIO = 1 / 2
THUMBNAIL = "thumbnail"
URL = "url"
PROVIDER = "provider"
DEEP_PAGINATION_ERROR = "Deep pagination is not allowed."
QUERY_SPECIAL_CHARACTER_ERROR = "Unescaped special characters are not allowed."


class RankFeature(Query):
    name = "rank_feature"


def _unmasked_query_end(page_size, page):
    """
    Used to retrieve the upper index of results to retrieve
    from Elasticsearch under the following conditions:
    1. There is no query mask
    2. The lower index is beyond the scope of the existing query mask
    3. The lower index is within the scope of the existing query mask
    but the upper index exceeds it

    In all these cases, the query mask is not used to calculate the upper index.
    """
    return ceil(page_size * page / (1 - DEAD_LINK_RATIO))


def _paginate_with_dead_link_mask(
    s: Search, page_size: int, page: int
) -> tuple[int, int]:
    """
    Given a query, a page and page_size, return the start and end
    of the slice of results.

    In almost all cases the ``DEAD_LINK_RATIO`` will effectively double
    the page size (given the current configuration of 0.5).

    The "branch X" labels are for cross-referencing with the tests.

    :param s: The elasticsearch Search object
    :param page_size: How big the page should be.
    :param page: The page number.
    :return: Tuple of start and end.
    """
    query_hash = get_query_hash(s)
    query_mask = get_query_mask(query_hash)
    if not query_mask:  # branch 1
        start = 0
        end = _unmasked_query_end(page_size, page)
    elif page_size * (page - 1) > sum(query_mask):  # branch 2
        start = len(query_mask)
        end = _unmasked_query_end(page_size, page)
    else:  # branch 3
        # query_mask is a list of 0 and 1 where 0 indicates the result position
        # for the given query will be an invalid link. If we accumulate a query
        # mask you end up, at each index, with the number of live results you
        # will get back when you query that deeply.
        # We then query for the start and end index _of the results_ in ES based
        # on the number of results that we think will be valid based on the query mask.
        # If we're requesting `page=2 page_size=3` and the mask is [0, 1, 0, 1, 0, 1],
        # then we know that we have to _start_ with at least the sixth result of the
        # overall query to skip the first page of 3 valid results. The "end" of the
        # query will then follow the same pattern to reach the number of valid results
        # required to fill the requested page. If the mask is not deep enough to
        # account for the entire range, then we follow the typical assumption when
        # a mask is not available that the end should be `page * page_size / 0.5`
        # (i.e., double the page size)
        accu_query_mask = list(accumulate(query_mask))
        start = 0
        if page > 1:
            try:  # branch 3_start_A
                # find the index at which we can skip N valid results where N = all
                # the results that would be skipped to arrive at the start of the
                # requested page
                # This will effectively be the index at which we have the number of
                # previous valid results + 1 because we don't want to include the
                # last valid result from the previous page
                start = accu_query_mask.index(page_size * (page - 1) + 1)
            except ValueError:  # branch 3_start_B
                # Cannot fail because of the check on branch 2 which verifies that
                # the query mask already includes at least enough masked valid
                # results to fulfill the requested page size
                start = accu_query_mask.index(page_size * (page - 1)) + 1
        # else:  branch 3_start_C
        # Always start page=1 queries at 0

        if page_size * page > sum(query_mask):  # branch 3_end_A
            end = _unmasked_query_end(page_size, page)
        else:  # branch 3_end_B
            end = accu_query_mask.index(page_size * page) + 1
    return start, end


def _get_query_slice(
    s: Search, page_size: int, page: int, filter_dead: bool | None = False
) -> tuple[int, int]:
    """
    Select the start and end of the search results for this query.
    """
    if filter_dead:
        start_slice, end_slice = _paginate_with_dead_link_mask(s, page_size, page)
    else:
        # Paginate search query.
        start_slice = page_size * (page - 1)
        end_slice = page_size * page
    if start_slice + end_slice > ELASTICSEARCH_MAX_RESULT_WINDOW:
        raise ValueError(DEEP_PAGINATION_ERROR)
    return start_slice, end_slice


def _quote_escape(query_string):
    """
    If there are any unmatched quotes in the query supplied by the user, ignore
    them.
    """
    num_quotes = query_string.count('"')
    if num_quotes % 2 == 1:
        return query_string.replace('"', '\\"')
    else:
        return query_string


def _post_process_results(
    s, start, end, page_size, search_results, request, filter_dead
) -> list[Hit] | None:
    """
    After fetching the search results from the back end, iterate through the
    results, perform image validation, and route certain thumbnails through our
    proxy.

    Keeps making new query requests until it is able to fill the page size.

    :param s: The Elasticsearch Search object.
    :param start: The start of the result slice.
    :param end: The end of the result slice.
    :param search_results: The Elasticsearch response object containing search
    results.
    :param request: The Django request object, used to build a "reversed" URL
    to detail pages.
    :param filter_dead: Whether images should be validated.
    :return: List of results.
    """
    results = []
    to_validate = []
    for res in search_results:
        if hasattr(res.meta, "highlight"):
            res.fields_matched = dir(res.meta.highlight)
        to_validate.append(res.url)
        results.append(res)

    if filter_dead:
        query_hash = get_query_hash(s)
        validate_images(query_hash, start, results, to_validate)

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
            end += int(end / 2)
            if start + end > ELASTICSEARCH_MAX_RESULT_WINDOW:
                return results

            s = s[start:end]
            search_response = s.execute()

            return _post_process_results(
                s, start, end, page_size, search_response, request, filter_dead
            )

    return results[:page_size]


def _apply_filter(
    s: Search,
    # Any is used here to avoid a circular import
    search_params: Any,  # MediaSearchRequestSerializer
    serializer_field: str,
    es_field: str | None = None,
    behaviour: Literal["filter", "exclude"] = "filter",
):
    """
    Parse and apply a filter from the search parameters serializer. The
    parameter key is assumed to have the same name as the corresponding
    Elasticsearch property. Each parameter value is assumed to be a comma
    separated list encoded as a string.

    :param s: The ``Search`` instance to apply the filter to
    :param search_params: the serializer instance containing user input
    :param serializer_field: the name of the parameter field in ``search_params``
    :param es_field: the corresponding parameter name in Elasticsearch
    :param behaviour: whether to accept (``filter``) or reject (``exclude``) the hit
    :return: the input ``Search`` object with the filters applied
    """

    if serializer_field in search_params.data:
        arguments = search_params.data.get(serializer_field)
        if arguments is None:
            return s
        arguments = arguments.split(",")
        parameter = es_field or serializer_field
        query = Q("terms", **{parameter: arguments})
        method = getattr(s, behaviour)
        return method("bool", should=query)

    return s


def _exclude_filtered(s: Search):
    """
    Hide data sources from the catalog dynamically.
    """
    filter_cache_key = "filtered_providers"
    filtered_providers = cache.get(key=filter_cache_key)
    if not filtered_providers:
        filtered_providers = models.ContentProvider.objects.filter(
            filter_content=True
        ).values("provider_identifier")
        cache.set(
            key=filter_cache_key, timeout=FILTER_CACHE_TIMEOUT, value=filtered_providers
        )
    to_exclude = [f["provider_identifier"] for f in filtered_providers]
    s = s.exclude("terms", provider=to_exclude)
    return s


def _exclude_mature_by_param(s: Search, search_params):
    if not search_params.data["mature"]:
        s = s.exclude("term", mature=True)
    return s


def search(
    # Any is used here to avoid a circular import
    search_params: Any,  # MediaSearchRequestSerializer
    index: Literal["image", "audio"],
    page_size: int,
    ip: int,
    request: Request,
    filter_dead: bool,
    page: int = 1,
) -> tuple[list[Hit], int, int]:
    """
    Given a set of keywords and an optional set of filters, perform a ranked
    paginated search.

    :param search_params: Search parameters. See
     :class: `ImageSearchQueryStringSerializer`.
    :param index: The Elasticsearch index to search (e.g. 'image')
    :param page_size: The number of results to return per page.
    :param ip: The user's hashed IP. Hashed IPs are used to anonymously but
    uniquely identify users exclusively for ensuring query consistency across
    Elasticsearch shards.
    :param request: Django's request object.
    :param filter_dead: Whether dead links should be removed.
    :param page: The results page number.
    :return: Tuple with a List of Hits from elasticsearch, the total count of
    pages, and number of results.
    """
    search_client = Search(index=index)

    s = search_client
    # Apply term filters. Each tuple pairs a filter's parameter name in the API
    # with its corresponding field in Elasticsearch. "None" means that the
    # names are identical.
    filters = [
        ("extension", None),
        ("category", None),
        ("categories", "category"),
        ("length", None),
        ("aspect_ratio", None),
        ("size", None),
        ("source", None),
        ("license", "license__keyword"),
        ("license_type", "license__keyword"),
    ]
    for serializer_field, es_field in filters:
        if serializer_field in search_params.data:
            s = _apply_filter(s, search_params, serializer_field, es_field)

    exclude = [
        ("excluded_source", "source"),
    ]
    for serializer_field, es_field in exclude:
        if serializer_field in search_params.data:
            s = _apply_filter(s, search_params, serializer_field, es_field, "exclude")

    # Exclude mature content and disabled sources
    s = _exclude_mature_by_param(s, search_params)
    s = _exclude_filtered(s)

    # Search either by generic multimatch or by "advanced search" with
    # individual field-level queries specified.
    search_fields = ["tags.name", "title", "description"]
    if "q" in search_params.data:
        query = _quote_escape(search_params.data["q"])
        base_query_kwargs = {
            "query": query,
            "fields": search_fields,
            "default_operator": "AND",
        }

        if '"' in query:
            base_query_kwargs["quote_field_suffix"] = ".exact"

        s = s.query(
            "simple_query_string",
            **base_query_kwargs,
        )
        # Boost exact matches on the title
        quotes_stripped = query.replace('"', "")
        exact_match_boost = Q(
            "simple_query_string",
            fields=["title"],
            query=f"{quotes_stripped}",
            boost=10000,
        )
        s = search_client.query(Q("bool", must=s.query, should=exact_match_boost))
    else:
        if "creator" in search_params.data:
            creator = _quote_escape(search_params.data["creator"])
            s = s.query("simple_query_string", query=creator, fields=["creator"])
        if "title" in search_params.data:
            title = _quote_escape(search_params.data["title"])
            s = s.query("simple_query_string", query=title, fields=["title"])
        if "tags" in search_params.data:
            tags = _quote_escape(search_params.data["tags"])
            s = s.query("simple_query_string", fields=["tags.name"], query=tags)

    if settings.USE_RANK_FEATURES:
        feature_boost = {"standardized_popularity": 10000}
        rank_queries = []
        for field, boost in feature_boost.items():
            rank_queries.append(Q("rank_feature", field=field, boost=boost))
        s = search_client.query(
            Q("bool", must=s.query or EMPTY_QUERY, should=rank_queries)
        )

    # Use highlighting to determine which fields contribute to the selection of
    # top results.
    s = s.highlight(*search_fields)
    s = s.highlight_options(order="score")
    s.extra(track_scores=True)
    # Route users to the same Elasticsearch worker node to reduce
    # pagination inconsistencies and increase cache hits.
    s = s.params(preference=str(ip), request_timeout=7)
    # Paginate
    start, end = _get_query_slice(s, page_size, page, filter_dead)
    s = s[start:end]
    try:
        if settings.VERBOSE_ES_RESPONSE:
            log.info(pprint.pprint(s.to_dict()))
        search_response = s.execute()
        log.info(
            f"query={json.dumps(s.to_dict())}," f" es_took_ms={search_response.took}"
        )
        if settings.VERBOSE_ES_RESPONSE:
            log.info(pprint.pprint(search_response.to_dict()))
    except RequestError as e:
        raise ValueError(e)

    results = _post_process_results(
        s, start, end, page_size, search_response, request, filter_dead
    )

    result_count, page_count = _get_result_and_page_count(
        search_response, results, page_size, page
    )
    return results or [], page_count, result_count


def related_media(uuid, index, request, filter_dead):
    """
    Given a UUID, find related search results.
    """
    search_client = Search(index=index)

    # Convert UUID to sequential ID.
    item = search_client
    item = item.query("match", identifier=uuid)
    _id = item.execute().hits[0].id

    s = search_client
    s = s.query(
        MoreLikeThis(
            fields=["tags.name", "title", "creator"],
            like={"_index": index, "_id": _id},
            min_term_freq=1,
            max_query_terms=50,
        )
    )
    # Never show mature content in recommendations.
    s = s.exclude("term", mature=True)
    s = _exclude_filtered(s)
    page_size = 10
    page = 1
    start, end = _get_query_slice(s, page_size, page, filter_dead)
    s = s[start:end]
    response = s.execute()
    results = _post_process_results(
        s, start, end, page_size, response, request, filter_dead
    )

    result_count, _ = _get_result_and_page_count(response, results, page_size, page)

    return results or [], result_count


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
        log.warning("Source cache fetch failed due to corruption")
    if type(sources) == list or cache_fetch_failed:
        # Invalidate old provider format.
        cache.delete(key=source_cache_name)
    if not sources:
        # Don't increase `size` without reading this issue first:
        # https://github.com/elastic/elasticsearch/issues/18838
        size = 100
        agg_body = {
            "aggs": {
                "unique_sources": {
                    "terms": {
                        "field": "source.keyword",
                        "size": size,
                        "order": {"_key": "desc"},
                    }
                }
            }
        }
        try:
            results = settings.ES.search(index=index, body=agg_body, request_cache=True)
            buckets = results["aggregations"]["unique_sources"]["buckets"]
        except NotFoundError:
            buckets = [{"key": "none_found", "doc_count": 0}]
        sources = {result["key"]: result["doc_count"] for result in buckets}
        cache.set(key=source_cache_name, timeout=SOURCE_CACHE_TIMEOUT, value=sources)
    return sources


def _get_result_and_page_count(
    response_obj: Response, results: list[Hit] | None, page_size: int, page: int
) -> tuple[int, int]:
    """
    Elasticsearch does not allow deep pagination of ranked queries.
    Adjust returned page count to reflect this.

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

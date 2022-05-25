from __future__ import annotations

import json
import logging as log
import pprint
from typing import List, Literal, Tuple, Union

from django.conf import settings

from elasticsearch.exceptions import RequestError
from elasticsearch_dsl import Q, Search
from elasticsearch_dsl.response import Hit

from catalog.api.controllers.elasticsearch.utils import (
    exclude_filtered_providers,
    get_query_slice,
    get_result_and_page_count,
    post_process_results,
)
from catalog.api.serializers.media_serializers import MediaSearchRequestSerializer


def _quote_escape(query_string: str) -> str:
    """
    If there are any unmatched quotes in the query supplied by the user, ignore
    them by escaping.

    :param query_string: the string in which to escape unbalanced quotes
    :return: the given string, if the quotes are balanced, the escaped string otherwise
    """

    num_quotes = query_string.count('"')
    if num_quotes % 2 == 1:
        return query_string.replace('"', '\\"')
    else:
        return query_string


def _apply_filter(
    s: Search,
    query_serializer: MediaSearchRequestSerializer,
    basis: Union[str, tuple[str, str]],
    behaviour: Literal["filter", "exclude"] = "filter",
) -> Search:
    """
    Parse and apply a filter from the search parameters serializer. The
    parameter key is assumed to have the same name as the corresponding
    Elasticsearch property. Each parameter value is assumed to be a comma
    separated list encoded as a string.

    :param s: the search query to issue to Elasticsearch
    :param query_serializer: the ``MediaSearchRequestSerializer`` object with the query
    :param basis: the name of the field in the serializer and Elasticsearch
    :param behaviour: whether to accept (``filter``) or reject (``exclude``) the hit
    :return: the modified search query
    """

    search_params = query_serializer.data
    if isinstance(basis, tuple):
        serializer_field, es_field = basis
    else:
        serializer_field = es_field = basis
    if serializer_field in search_params:
        filters = []
        for arg in search_params[serializer_field].split(","):
            filters.append(Q("term", **{es_field: arg}))
        method = getattr(s, behaviour)  # can be ``s.filter`` or ``s.exclude``
        return method("bool", should=filters)
    else:
        return s


def perform_search(
    query_serializer: MediaSearchRequestSerializer,
    index: Literal["image", "audio"],
    ip: int,
) -> Tuple[List[Hit], int, int]:
    """
    Perform a ranked, paginated search based on the query and filters given in the
    search request.

    :param query_serializer: the ``MediaSearchRequestSerializer`` object with the query
    :param index: The Elasticsearch index to search (e.g. 'image')
    :param ip: the users' hashed IP to consistently route to the same ES shard
    :return: the list of search results with the page and result count
    """

    s = Search(using="default", index=index)
    search_params = query_serializer.data

    rules: dict[Literal["filter", "exclude"], list[Union[str, tuple[str, str]]]] = {
        "filter": [
            "extension",
            "category",
            ("categories", "category"),
            "aspect_ratio",
            "size",
            "length",
            "source",
            ("license", "license.keyword"),
            ("license_type", "license.keyword"),
        ],
        "exclude": [
            ("excluded_source", "source"),
        ],
    }
    for behaviour, bases in rules.items():
        for basis in bases:
            s = _apply_filter(s, query_serializer, basis, behaviour)

    # Exclude mature content
    if not search_params["mature"]:
        s = s.exclude("term", mature=True)
    # Exclude sources with ``filter_content`` enabled
    s = exclude_filtered_providers(s)

    # Search either by generic multimatch or by "advanced search" with
    # individual field-level queries specified.

    search_fields = ["tags.name", "title", "description"]
    if "q" in search_params:
        query = _quote_escape(search_params["q"])
        s = s.query(
            "simple_query_string",
            query=query,
            fields=search_fields,
            default_operator="AND",
        )
        # Boost exact matches
        quotes_stripped = query.replace('"', "")
        exact_match_boost = Q(
            "simple_query_string",
            fields=["title"],
            query=f'"{quotes_stripped}"',
            boost=10000,
        )
        s.query = Q("bool", must=s.query, should=exact_match_boost)
    else:
        query_bases = ["creator", "title", ("tags", "tags.name")]
        for query_basis in query_bases:
            if isinstance(query_basis, tuple):
                serializer_field, es_field = query_basis
            else:
                serializer_field = es_field = query_basis
            if serializer_field in search_params:
                value = _quote_escape(search_params[serializer_field])
                s = s.query("simple_query_string", fields=[es_field], query=value)

    if settings.USE_RANK_FEATURES:
        feature_boost = {"standardized_popularity": 10000}
        rank_queries = []
        for field, boost in feature_boost.items():
            rank_queries.append(Q("rank_feature", field=field, boost=boost))
        s.query = Q("bool", must=s.query, should=rank_queries)

    # Use highlighting to determine which fields contribute to the selection of
    # top results.
    s = s.highlight(*search_fields)
    s = s.highlight_options(order="score")

    # Route users to the same Elasticsearch worker node to reduce
    # pagination inconsistencies and increase cache hits.
    s = s.params(preference=str(ip), request_timeout=7)

    # Paginate
    start, end = get_query_slice(
        s,
        search_params["page_size"],
        search_params["page"],
        search_params["filter_dead"],
    )
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

    results = post_process_results(
        s,
        start,
        end,
        search_params["page_size"],
        search_response,
        search_params["filter_dead"],
    )

    result_count, page_count = get_result_and_page_count(
        search_response, results, search_params["page_size"]
    )
    return results, page_count, result_count

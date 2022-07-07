from __future__ import annotations

import json
import logging
from typing import List, Literal, Optional, Tuple

from django.conf import settings

from elasticsearch.exceptions import RequestError
from elasticsearch_dsl import Q, Search
from elasticsearch_dsl.query import EMPTY_QUERY
from elasticsearch_dsl.response import Hit

from catalog.api.controllers.elasticsearch.utils import (
    exclude_filtered_providers,
    get_query_slice,
    get_result_and_page_count,
    post_process_results,
)
from catalog.api.serializers.media_serializers import MediaSearchRequestSerializer


parent_logger = logging.getLogger(__name__)


class FieldMapping:
    """
    Establishes a mapping between a field in ``MediaSearchRequestSerializer`` and the
    Elasticsearch index for a media.
    """

    def __init__(self, serializer_field: str, es_field: Optional[str] = None):
        self.serializer_field: str = serializer_field
        """the name of the field in ``MediaSearchRequestSerializer``"""

        self.es_field: str = es_field or serializer_field
        """the name of the field in the Elasticsearch index"""

    def __str__(self):
        return (
            "FieldMapping("
            f"serializer_field={self.serializer_field}, "
            f"es_field={self.es_field})"
        )

    def __repr__(self):
        return str(self)


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
    mapping: FieldMapping,
    behaviour: Literal["filter", "exclude"] = "filter",
) -> Search:
    """
    Parse and apply a filter from the search parameters serializer. The
    parameter key is assumed to have the same name as the corresponding
    Elasticsearch property. Each parameter value is assumed to be a comma
    separated list encoded as a string.

    :param s: the search query to issue to Elasticsearch
    :param query_serializer: the ``MediaSearchRequestSerializer`` object with the query
    :param mapping: the name of the field in the serializer and Elasticsearch
    :param behaviour: whether to accept (``filter``) or reject (``exclude``) the hit
    :return: the modified search query
    """
    logger = parent_logger.getChild("_apply_filter")
    search_params = query_serializer.data
    if mapping.serializer_field in search_params:
        filters = []
        for arg in search_params[mapping.serializer_field].split(","):
            filters.append(Q("term", **{mapping.es_field: arg}))
        method = getattr(s, behaviour)  # can be ``s.filter`` or ``s.exclude``
        logger.debug(
            "applying filter "
            f"behaviour={behaviour} "
            f"mapping={mapping} "
            f"filters={json.dumps(list(map(lambda f: f.to_dict(), filters)))} "
        )
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

    logger = parent_logger.getChild("perform_search")
    logger.info(
        "searching with "
        f"query_serializer.data={json.dumps(query_serializer.data)} "
        f"index={index} "
        f"(hashed) ip={ip} "
    )
    s = Search(using="default", index=index)
    search_params = query_serializer.data

    rules: dict[Literal["filter", "exclude"], list[FieldMapping]] = {
        "filter": [
            FieldMapping("extension"),
            FieldMapping("category"),
            FieldMapping("categories", "category"),
            FieldMapping("aspect_ratio"),
            FieldMapping("size"),
            FieldMapping("length"),
            FieldMapping("source"),
            FieldMapping("license", "license.keyword"),
            FieldMapping("license_type", "license.keyword"),
        ],
        "exclude": [
            FieldMapping("excluded_source", "source"),
        ],
    }
    for behaviour, mappings in rules.items():
        for mapping in mappings:
            s = _apply_filter(s, query_serializer, mapping, behaviour)

    # Exclude mature content
    if not search_params["mature"]:
        logger.debug("excluding mature")
        s = s.exclude("term", mature=True)
    # Exclude sources with ``filter_content`` enabled
    s = exclude_filtered_providers(s)

    # Search either by generic multimatch or by "advanced search" with
    # individual field-level queries specified.

    search_fields = ["tags.name", "title", "description"]
    if "q" in search_params:
        escaped_query = _quote_escape(search_params["q"])
        logger.info(f"searching with query term escaped_query={escaped_query}")
        s = s.query(
            "simple_query_string",
            query=escaped_query,
            fields=search_fields,
            default_operator="AND",
        )
        # Boost exact matches
        quotes_stripped = escaped_query.replace('"', "")
        exact_match_boost = Q(
            "simple_query_string",
            fields=["title"],
            query=f'"{quotes_stripped}"',
            boost=10000,
        )
        s.query = Q("bool", must=s.query, should=exact_match_boost)
    else:
        logger.info("searching without query term")
        query_bases = ["creator", "title", ("tags", "tags.name")]
        for query_basis in query_bases:
            if isinstance(query_basis, tuple):
                serializer_field, es_field = query_basis
            else:
                serializer_field = es_field = query_basis
            if serializer_field in search_params:
                value = _quote_escape(search_params[serializer_field])
                logger.debug(
                    "adding query for "
                    f"value={value} "
                    f"es_field={es_field}"
                    f"serializer_field={serializer_field}"
                )
                s = s.query("simple_query_string", fields=[es_field], query=value)

    if settings.USE_RANK_FEATURES:
        feature_boost = {"standardized_popularity": 10000}
        rank_queries = []
        for field, boost in feature_boost.items():
            logger.debug(
                "applying ranked features " f"field={field} " f"boost={boost} "
            )
            rank_queries.append(Q("rank_feature", field=field, boost=boost))
        s.query = Q("bool", must=s.query or EMPTY_QUERY, should=rank_queries)

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
        logger.info("executing query")
        search_response = s.execute()
        logger.debug(
            "executed query "
            f"es_took_ms={search_response.took} "
            f"query={json.dumps(s.to_dict())} "
            f"response={json.dumps(search_response.to_dict())} "
        )
    except RequestError as e:
        logger.error("encountered error executing query", exc_info=True)
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

    dumpable_results = (
        results.to_dict()
        if isinstance(results, Hit)
        else list(map(lambda r: r.to_dict(), results))
    )

    logger.debug(
        "finished post processing and returning "
        f"result_count={result_count} "
        f"page_count={page_count} "
        f"results={json.dumps(dumpable_results)}"
    )
    return results, page_count, result_count

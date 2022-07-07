import json
import logging

from elasticsearch_dsl import Search

from catalog.api.controllers.elasticsearch.utils import (
    exclude_filtered_providers,
    get_query_slice,
    get_result_and_page_count,
    post_process_results,
)


parent_logger = logging.getLogger(__name__)


def related_media(uuid, index, filter_dead):
    """
    Given a UUID, find related search results.
    """
    logger = parent_logger.getChild("related_media")
    search_client = Search(using="default", index=index)

    # Convert UUID to sequential ID.
    item = search_client.query("match", identifier=uuid)
    _id = item.execute().hits[0].id

    s = search_client.query(
        "more_like_this",
        fields=["tags.name", "title", "creator"],
        like={"_index": index, "_id": _id},
        min_term_freq=1,
        max_query_terms=50,
    )
    # Never show mature content in recommendations.
    s = s.exclude("term", mature=True)
    s = exclude_filtered_providers(s)
    page_size = 10
    page = 1
    start, end = get_query_slice(s, page_size, page, filter_dead)
    s = s[start:end]
    response = s.execute()
    logger.debug(
        "executed related query "
        f"es_took_ms={response.took} "
        f"query={json.dumps(s.to_dict())} "
        f"response={json.dumps(response.to_dict())} "
    )

    results = post_process_results(s, start, end, page_size, response, filter_dead)

    result_count, _ = get_result_and_page_count(response, results, page_size)

    logger.debug(
        "finished post processing and returning related "
        f"result_count={result_count} "
        f"results={json.dumps(results)}"
    )
    return results, result_count

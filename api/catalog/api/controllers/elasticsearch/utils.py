from itertools import accumulate
from math import ceil
from typing import List, Optional, Tuple

from django.core.cache import cache

from elasticsearch_dsl import Search
from elasticsearch_dsl.response import Hit, Response

from catalog.api.models import ContentProvider
from catalog.api.utils.dead_link_mask import get_query_hash, get_query_mask
from catalog.api.utils.validate_images import validate_images


FILTER_CACHE_TIMEOUT = 30
DEAD_LINK_RATIO = 1 / 2
ELASTICSEARCH_MAX_RESULT_WINDOW = 10000


def exclude_filtered_providers(s: Search) -> Search:
    """
    Hide data sources from the catalog dynamically. This excludes providers with
    ``filter_content`` enabled from the search results.

    :param s: the search query to issue to Elasticsearch
    :return: the modified search query
    """

    filter_cache_key = "filtered_providers"
    filtered_providers = cache.get(key=filter_cache_key)
    if filtered_providers is None:
        filtered_providers = ContentProvider.objects.filter(filter_content=True).values(
            "provider_identifier"
        )
        cache.set(
            key=filter_cache_key,
            timeout=FILTER_CACHE_TIMEOUT,
            value=filtered_providers,
        )
    if len(filtered_providers) != 0:
        to_exclude = [f["provider_identifier"] for f in filtered_providers]
        s = s.exclude("terms", provider=to_exclude)
    return s


def paginate_with_dead_link_mask(
    s: Search, page_size: int, page: int
) -> Tuple[int, int]:
    """
    Given a query, a page and page_size, return the start and end
    of the slice of results.

    :param s: The elasticsearch Search object
    :param page_size: How big the page should be.
    :param page: The page number.
    :return: Tuple of start and end.
    """
    query_hash = get_query_hash(s)
    query_mask = get_query_mask(query_hash)
    if not query_mask:
        start = 0
        end = ceil(page_size * page / (1 - DEAD_LINK_RATIO))
    elif page_size * (page - 1) > sum(query_mask):
        start = len(query_mask)
        end = ceil(page_size * page / (1 - DEAD_LINK_RATIO))
    else:
        accu_query_mask = list(accumulate(query_mask))
        start = 0
        if page > 1:
            try:
                start = accu_query_mask.index(page_size * (page - 1) + 1)
            except ValueError:
                start = accu_query_mask.index(page_size * (page - 1)) + 1
        if page_size * page > sum(query_mask):
            end = ceil(page_size * page / (1 - DEAD_LINK_RATIO))
        else:
            end = accu_query_mask.index(page_size * page) + 1
    return start, end


def get_query_slice(
    s: Search, page_size: int, page: int, filter_dead: Optional[bool] = False
) -> Tuple[int, int]:
    """
    Select the start and end of the search results for this query.
    """
    if filter_dead:
        start_slice, end_slice = paginate_with_dead_link_mask(s, page_size, page)
    else:
        # Paginate search query.
        start_slice = page_size * (page - 1)
        end_slice = page_size * page
    if start_slice + end_slice > ELASTICSEARCH_MAX_RESULT_WINDOW:
        raise ValueError("Deep pagination is not allowed.")
    return start_slice, end_slice


def post_process_results(
    s, start, end, page_size, search_results, filter_dead
) -> List[Hit]:
    """
    After fetching the search results from the back end, iterate through the
    results, perform image validation, and route certain thumbnails through our
    proxy.

    :param s: The Elasticsearch Search object.
    :param start: The start of the result slice.
    :param end: The end of the result slice.
    :param search_results: The Elasticsearch response object containing search
    results.
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

        if len(results) < page_size:
            end += int(end / 2)
            if start + end > ELASTICSEARCH_MAX_RESULT_WINDOW:
                return results

            s = s[start:end]
            search_response = s.execute()

            return post_process_results(
                s, start, end, page_size, search_response, filter_dead
            )
    return results[:page_size]


def get_result_and_page_count(
    response_obj: Response, results: List[Hit], page_size: int
) -> Tuple[int, int]:
    """
    Elasticsearch does not allow deep pagination of ranked queries.
    Adjust returned page count to reflect this.

    :param response_obj: The original Elasticsearch response object.
    :param results: The list of filtered result Hits.
    :return: Result and page count.
    """
    result_count = response_obj.hits.total.value
    natural_page_count = int(result_count / page_size)
    if natural_page_count % page_size != 0:
        natural_page_count += 1
    last_allowed_page = int((5000 + page_size / 2) / page_size)
    page_count = min(natural_page_count, last_allowed_page)
    if len(results) < page_size and page_count == 0:
        result_count = len(results)

    return result_count, page_count

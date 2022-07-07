import json
import logging
from itertools import accumulate
from math import ceil
from typing import List, Optional, Tuple

from django.core.cache import cache

from elasticsearch_dsl import Search
from elasticsearch_dsl.response import Hit, Response

from catalog.api.models import ContentProvider
from catalog.api.utils.dead_link_mask import get_query_hash, get_query_mask
from catalog.api.utils.validate_images import validate_images


parent_logger = logging.getLogger(__name__)


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
    logger = parent_logger.getChild("exclude_filtered_providers")
    filter_cache_key = "filtered_providers"
    filtered_providers = cache.get(key=filter_cache_key)
    if filtered_providers is None:
        filtered_providers = ContentProvider.objects.filter(filter_content=True).values(
            "provider_identifier"
        )
        logger.debug("adding filtered providers to cache")
        cache.set(
            key=filter_cache_key,
            timeout=FILTER_CACHE_TIMEOUT,
            value=filtered_providers,
        )

    logger.info(f'filtered_providers={",".join(filtered_providers)}')
    if len(filtered_providers) != 0:
        to_exclude = [f["provider_identifier"] for f in filtered_providers]
        logger.info("auto-excluding filtered providers")
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
    logger = parent_logger.getChild("paginate_with_dead_link_mask")
    query_hash = get_query_hash(s)
    query_mask = get_query_mask(query_hash)
    logger.debug(
        f"page_size={page_size} "
        f"page={page} "
        f"query_hash={query_hash} "
        f'query_mask={",".join(map(str, query_mask))} '
    )
    if not query_mask:
        start = 0
        end = ceil(page_size * page / (1 - DEAD_LINK_RATIO))
        logger.debug(
            "empty query_mask "
            f"page_size={page_size} "
            f"page={page} "
            f"start={start} "
            f"end={end} "
        )
        return start, end

    # TODO: What does this request_size mean vs the one below
    # that doesn't subtract 1 from the page? Why do we subtract
    # 1 here and the other time we do not?
    request_size = page_size * (page - 1)
    query_mask_sum = sum(query_mask)
    if request_size > query_mask_sum:
        start = len(query_mask)
        end = ceil(page_size * page / (1 - DEAD_LINK_RATIO))
        logger.debug(
            "request size exceeds query mask sum (branch 1)"
            f"request_size={request_size} "
            f"sum(query_mask)={query_mask_sum} "
            f"start={start} "
            f"end={end} "
        )
        return start, end

    accu_query_mask = list(accumulate(query_mask))
    logger.debug(f"accu_query_mask={accu_query_mask} ")
    start = 0
    if page > 1:
        caught = False
        try:
            idx = page_size * (page - 1) + 1
            start = accu_query_mask.index(idx)
        except ValueError:
            caught = True
            idx = page_size * (page - 1)
            start = accu_query_mask.index(idx) + 1

        logger.debug("shifted page using " f"idx={idx} " f"caught?={caught} ")

    request_size = page_size * page
    if request_size > query_mask_sum:
        logger.debug(
            "request size exceeds query mask sum (branch 2) "
            f"request_size={request_size} "
            f"query_mask_sum={query_mask_sum} "
        )
        end = ceil(page_size * page / (1 - DEAD_LINK_RATIO))
    else:
        end = accu_query_mask.index(page_size * page) + 1

    logger.debug("third branch returnining " f"start={start} " f"end={end} ")
    return start, end


def get_query_slice(
    s: Search, page_size: int, page: int, filter_dead: Optional[bool] = False
) -> Tuple[int, int]:
    """
    Select the start and end of the search results for this query.
    """
    logger = parent_logger.getChild("get_query_slice")
    if filter_dead:
        start_slice, end_slice = paginate_with_dead_link_mask(s, page_size, page)
    else:
        # Paginate search query.
        start_slice = page_size * (page - 1)
        end_slice = page_size * page
        logger.debug(
            "paginating without filtering for dead links "
            f"page_size={page_size} "
            f"page={page} "
            f"start_slice={start_slice} "
            f"end_slice={end_slice} "
        )
    if start_slice + end_slice > ELASTICSEARCH_MAX_RESULT_WINDOW:
        raise ValueError(
            "Deep pagination is not allowed. "
            f"Window totalled {start_slice + end_slice}."
        )

    logger.info(f"start_slice={start_slice} end_slice={end_slice}")
    return start_slice, end_slice


def post_process_results(
    s, start, end, page_size, search_results, filter_dead, depth: int = 0
) -> List[Hit]:
    """
    After fetching the search results from the back end, iterate through the
    results filtering dead links. After filtering links, continue accruing additional
    results until the requested page_size of validated results is reached.

    :param s: The Elasticsearch Search object.
    :param start: The start of the result slice.
    :param end: The end of the result slice.
    :param search_results: The Elasticsearch response object containing search
    results.
    :param filter_dead: Whether images should be validated.
    :return: List of results.
    """
    logger = parent_logger.getChild("post_process_results")
    logger.info(f"post processing results depth={depth}")
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
            logger.info(f"executing additional backfill query depth={depth}")
            search_response = s.execute()
            # don't log the query off of ``s`` because it's identical to the already
            # logged query elsewhere in the logs, just with different start/end.
            logger.debug(
                "exectued additional backfill query"
                f"start={start} "
                f"end={end} "
                f"es_took_ms={search_response.took} "
                f"response={json.dumps(search_response.to_dict())} "
            )

            return post_process_results(
                s, start, end, page_size, search_response, filter_dead, depth=depth + 1
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
    logger = parent_logger.getChild("get_result_and_page_count")
    result_count = response_obj.hits.total.value
    natural_page_count = int(result_count / page_size)
    if natural_page_count % page_size != 0:
        logger.debug("incrementing natural_page_count")
        natural_page_count += 1
    last_allowed_page = int((5000 + page_size / 2) / page_size)
    page_count = min(natural_page_count, last_allowed_page)
    if len(results) < page_size and page_count == 0:
        logger.debug(f"setting result_count to len(results)={len(results)}")
        result_count = len(results)

    logger.debug(
        f"result_count={result_count} "
        f"page_count={page_count} "
        f"natural_page_count={natural_page_count} "
        f"last_allowed_page={last_allowed_page}"
    )
    return result_count, page_count

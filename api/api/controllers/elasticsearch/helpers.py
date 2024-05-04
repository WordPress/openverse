from __future__ import annotations

import functools
import pprint
import time
from itertools import accumulate
from math import ceil

from django.conf import settings

import structlog
from elasticsearch import BadRequestError, NotFoundError
from elasticsearch_dsl import Search

from api.utils.dead_link_mask import get_query_hash, get_query_mask


logger = structlog.get_logger(__name__)


def log_timing_info(func):
    @functools.wraps(func)
    def wrapper(*args, es_query, **kwargs):
        start_time = time.time()

        # Call the original function
        result = func(*args, **kwargs)

        response_time_in_ms = int((time.time() - start_time) * 1000)
        if hasattr(result, "took"):
            es_time_in_ms = result.took
        else:
            es_time_in_ms = result.get("took")
        logger.info(
            {
                "response_time": response_time_in_ms,
                "es_time": es_time_in_ms,
                "es_query": es_query,
            }
        )

        return result

    return wrapper


@log_timing_info
def get_es_response(s, *args, **kwargs):
    if settings.VERBOSE_ES_RESPONSE:
        logger.info(pprint.pprint(s.to_dict()))

    try:
        search_response = s.execute()

        if settings.VERBOSE_ES_RESPONSE:
            logger.info(pprint.pprint(search_response.to_dict()))
    except (BadRequestError, NotFoundError) as e:
        raise ValueError(e)

    return search_response


@log_timing_info
def get_raw_es_response(index, body, *args, **kwargs):
    return settings.ES.search(index=index, body=body, *args, **kwargs)


ELASTICSEARCH_MAX_RESULT_WINDOW = 10000
DEAD_LINK_RATIO = 1 / 2
DEEP_PAGINATION_ERROR = "Deep pagination is not allowed."


def _unmasked_query_end(page_size, page):
    """
    Calculate the upper index of results to retrieve from Elasticsearch.

    Used to retrieve the upper index of results to retrieve from Elasticsearch under the
    following conditions:
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
    Return the start and end of the results slice, given the query, page and page size.

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


def get_query_slice(
    s: Search, page_size: int, page: int, filter_dead: bool | None = False
) -> tuple[int, int]:
    """Select the start and end of the search results for this query."""

    if filter_dead:
        start_slice, end_slice = _paginate_with_dead_link_mask(s, page_size, page)
    else:
        # Paginate search query.
        start_slice = page_size * (page - 1)
        end_slice = page_size * page
    if start_slice + end_slice > ELASTICSEARCH_MAX_RESULT_WINDOW:
        raise ValueError(DEEP_PAGINATION_ERROR)
    return start_slice, end_slice

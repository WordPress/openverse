from unittest import mock

import pytest

from catalog.api.controllers import search_controller
from catalog.api.utils.pagination import MAX_TOTAL_PAGE_COUNT


@pytest.mark.parametrize(
    "total_hits, real_result_count, page_size, expected",
    [
        # No results
        (0, 0, 10, (0, 0)),
        # Setting page size to 0 raises an exception
        pytest.param(
            0, 0, 0, (0, 0), marks=pytest.mark.raises(exception=ZeroDivisionError)
        ),
        # Fewer results than page size leads to max of result total
        (5, 5, 10, (5, 0)),
        # Even if no real results exist, total result count and page count are returned
        # (seems like an impossible case IRL)
        (100, 0, 10, (100, 10)),
        # If there are real results and ES reports no hits, nothing is expected
        # (seems like an impossible case IRL)
        (0, 100, 10, (0, 0)),
        # Evenly divisible number of pages
        (25, 5, 5, (25, 5)),
        # Unevenly divisible number of pages
        (21, 5, 5, (21, 5)),
        # My assumption would be that this yields (20, 4), but the code is such that
        # when the "natural" page count can't be cleanly divisible by the page size,
        # We increment it plus one. Why would that be the case? 20 results, with 5
        # results per-page, would seem to result in 4 pages total not 5 🤷‍♀️
        (20, 5, 5, (20, 5)),
        # Fewer hits than page size, but result list somehow differs, use that for count
        (48, 20, 50, (20, 0)),
        # Page count gets truncated always
        (5000, 10, 10, (5000, MAX_TOTAL_PAGE_COUNT)),
    ],
)
def test_get_result_and_page_count(total_hits, real_result_count, page_size, expected):
    response_obj = mock.MagicMock()
    response_obj.hits.total.value = total_hits
    results = [mock.MagicMock() for _ in range(real_result_count)]

    actual = search_controller._get_result_and_page_count(
        response_obj,
        results,
        page_size,
    )
    assert actual == expected

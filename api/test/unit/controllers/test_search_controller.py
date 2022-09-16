import random
from enum import Enum, auto
from typing import Callable
from unittest import mock
from uuid import uuid4

import pytest
from django_redis import get_redis_connection
from elasticsearch_dsl import Search

from catalog.api.controllers import search_controller
from catalog.api.utils.dead_link_mask import get_query_hash, save_query_mask


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


@pytest.fixture
def unique_search() -> Search:
    s = Search()
    s = s.query(
        "simple_query_string",
        query=str(uuid4()),
        fields=["title"],
    )
    return s


@pytest.mark.parametrize(
    ("page_size", "page", "expected_end"),
    (
        (20, 1, 40),
        (40, 1, 80),
        (20, 2, 80),
        (40, 2, 160),
        (10, 4, 80),
        (20, 10, 400),
    ),
)
def test_paginate_with_dead_link_mask_new_search(
    unique_search, page_size, page, expected_end
):
    """
    Testing "branch 1" in the function code.

    This test case is aimed at when a search does not yet have a query mask
    because the search has never before been executed.

    ``start`` is pinned to 0 because when a query mask does not exist, the query
    must start at 0 due to the fact that the validity of the query results is not
    known. We can't reliably skip any number of results due to potentially dead
    links. If we didn't start maskless queries at 0, then query pagination would
    not line up in a deterministic way.

    Take for example, the following list of result liveness:
    [True, False, False, False, False, True, True]
     0     1      2      3      4      5     6

    If we do not have a query mask to represent this, but we request page 2 of size 2,
    where should we start the query? We would want to start at index 2 (skipping the
    first page of 2 results), but in actuality we need to start at index 6 because
    the first page of 2 confirmed live results actually encompases the range from
    1 to 5, as that is the smallest window in which we can fulfill the requested
    _first_ page of results that we're skipping.

    Given this, if we don't know the link liveness (via a query mask) then we must
    start at 0.

    ``expected_end`` is always double the page size due to the current
    setting of ``DEAD_LINK_RATIO``. For pages beyond the first page,
    we are forced to compensate for two facts that cause the query size
    to grow at a dramatic rate:
    1. ``start`` being pinned to 0 (see explanation below)
    2. The presumed possibility that the first n results (where n = page_size * page),
    which represent the results we would _skip_ to reach the start of the page we
    actually want will be precisely live/dead at the ratio described by
    ``DEAD_LINK_RATIO``. Therefore, we're sort of "betting" on the fact that if we
    skip enough results to satisfy the dead link ratio's assumption and then grab enough
    results on the tail end to assume that the first pages are precisely dead/live at
    that ratio, then the page we actually want will definitely be inside of that range.
    Despite the large query size growth, it does seem that this is more or less reasonable
    though if the API receives a bunch of last page + max page size queries for original
    query terms it would cause a ton of very large query sizes to be sent to ES.
    """
    start = 0

    assert search_controller._paginate_with_dead_link_mask(
        s=unique_search, page_size=page_size, page=page
    ) == (start, expected_end)


class CreateMaskConfig(Enum):
    FORCE_DEAD_BITS_AT_START = auto()
    PREVENT_DEAD_BITS_AT_START = auto()
    FORCE_DEAD_BITS_AT_END = auto()
    PREVENT_DEAD_BITS_AT_END = auto()


@pytest.fixture(name="create_mask")
def create_mask_fixture() -> Callable[(Search, int, int), None]:
    created_masks = []

    def create_mask(
        s: Search,
        liveness_count: int | None,
        mask: list[int] | None = None,
        mask_size: int | None = None,
        config: tuple[CreateMaskConfig] = (),
    ):
        query_hash = get_query_hash(s)
        created_masks.append(query_hash)
        if mask:
            save_query_mask(query_hash, mask)
            return

        assert (
            mask_size >= liveness_count
        ), "Cannot create more live bits than the mask can contain."
        dead_bits = [0] * (mask_size - liveness_count)
        live_bits = [1] * liveness_count
        mask = dead_bits + live_bits
        random.shuffle(mask)

        if CreateMaskConfig.FORCE_DEAD_BITS_AT_START in config:
            if mask[0] == 1:
                first_dead_bit = mask.index(0)
                del mask[first_dead_bit]
                mask = [0] + mask

        if CreateMaskConfig.PREVENT_DEAD_BITS_AT_START in config:
            if mask[0] == 0:
                first_live_bit = mask.index(1)
                del mask[first_live_bit]
                mask = [1] + mask

        if CreateMaskConfig.FORCE_DEAD_BITS_AT_END in config:
            if mask[-1] == 1:
                first_dead_bit = mask.index(0)
                del mask[first_dead_bit]
                mask = mask + [0]

        if CreateMaskConfig.PREVENT_DEAD_BITS_AT_END in config:
            if mask[-1] == 0:
                first_live_bit = mask.index(1)
                del mask[first_live_bit]
                mask = mask + [1]

        save_query_mask(query_hash, mask)

    yield create_mask

    with get_redis_connection("default") as redis:
        redis.delete(*[f"{h}:dead_link_mask" for h in created_masks])


@pytest.mark.parametrize(
    ("page_size", "page", "mask_size", "liveness_count", "expected_end"),
    (
        (20, 2, 19, 10, 80),
        (20, 2, 19, 0, 80),
        (20, 2, 1, 0, 80),
        (20, 2, 10, 9, 80),
        (20, 2, 10, 0, 80),
        (40, 2, 19, 10, 160),
        (40, 2, 19, 18, 160),
        (40, 2, 19, 0, 160),
        (40, 2, 39, 10, 160),
        (40, 2, 9, 5, 160),
        (10, 2, 5, 2, 40),
        (10, 2, 1, 0, 40),
        (10, 2, 9, 4, 40),
    ),
)
def test_paginate_with_dead_link_mask_query_mask_is_not_large_enough(
    unique_search,
    create_mask,
    page_size,
    page,
    mask_size,
    liveness_count,
    expected_end,
):
    """
    Testing "branch 2" in the function code.

    We could pin ``liveness_count`` to 0 and none of these tests would have
    different results _however_ it would assume the particular implementation
    detail about how ``start`` is calculated in the actual function.

    ``page_size`` must be at least 2 for these tests because the first page
    always has an implicit start at 0 _unless_ a query mask exists that indicates
    that it can skip forward. In this case a mask will exist, therefore the first
    page will skip forward to avoid any dead links at the start of the results list.
    """
    start = mask_size
    create_mask(s=unique_search, mask_size=mask_size, liveness_count=liveness_count)
    assert search_controller._paginate_with_dead_link_mask(
        s=unique_search, page_size=page_size, page=page
    ) == (start, expected_end)


@pytest.mark.parametrize(
    (
        "page_size",
        "page",
        "mask_or_mask_size",
        "liveness_count",
        "expected_range",
        "create_mask_config",
    ),
    (
        # query starts at the end of the mask
        pytest.param(20, 2, 20, 20, (20, 80), (), id="start_A; end_A"),
        # second page query window is fully within the mask
        pytest.param(
            2,
            2,
            [0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1],
            None,
            (4, 8),
            (),
            id="start_A; end_B",
        ),
        pytest.param(
            2,
            2,
            [0, 1, 1, 0, 0, 0],
            None,
            (3, 8),
            (),
            id="start_B; end_A",
        ),
        # start_B; end_B is impossible. See note in doc string below
        # query is fully covered by the mask
        pytest.param(
            20,
            1,
            20,
            20,
            (0, 20),
            (),
            id="start_C; end_B",
        ),
        # query is not fulfilled by mask
        pytest.param(
            20,
            1,
            20,
            19,
            (0, 40),
            CreateMaskConfig.PREVENT_DEAD_BITS_AT_START,
            id="start_C; end_A",
        ),
        pytest.param(
            20,
            1,
            20,
            19,
            (0, 40),
            CreateMaskConfig.FORCE_DEAD_BITS_AT_START,
            id="start_C; end_A",
        ),
        # mask scope extends beyond the query window
        pytest.param(
            3, 1, [0, 0, 0, 1, 1, 1, 0, 1], None, (0, 6), (), id="start_C; end_B"
        ),
    ),
)
def test_paginate_with_dead_link_mask_query_mask_overlaps_query_window(
    unique_search,
    create_mask,
    page_size,
    page,
    mask_or_mask_size,
    liveness_count,
    expected_range,
    create_mask_config,
):
    """
    Testing "branch 3" in the function code. Individual parameterized cases
    annotated on this test case are labelled with the start and end branch names.

    Branch combinations:

    start_A; end_A
    start_A; end_B
    start_B; end_A
    start_B; end_B  # impossible, see explanation below
    start_C; end_A
    start_C; end_B

    There are additional tests around the boundaries of each branch, hence the
    number of defined cases is greater than the number of listed branch combinations.

    Additionally, start_B + end_B is impossible. end_B can only happen when the query
    mask contains _at least_ sufficient live bits to skip the previous pages and cover
    the entirety of the presently requested page. This is checked by evaluating the sum
    of the bits and only using the bits to find the end of the query if the mask covers
    the full size of the query. If not, then the unmasked end is used. If start_B happens,
    this means that the mask was not even sufficient to cover the previous pages + 1, just
    the previous pages _exactly_. If you combine this information, it is clear that end_B
    cannot happen when start_B happens because the conditions for start_B preclude the
    possibility of end_B.
    """
    create_mask_kwargs = {
        "s": unique_search,
        "liveness_count": liveness_count,
        "config": (
            (create_mask_config,)
            if not isinstance(create_mask_config, tuple)
            else create_mask_config
        ),
    }
    if isinstance(mask_or_mask_size, int):
        create_mask_kwargs.update(mask_size=mask_or_mask_size)
    else:
        create_mask_kwargs.update(mask=mask_or_mask_size)

    create_mask(**create_mask_kwargs)
    actual_range = search_controller._paginate_with_dead_link_mask(
        s=unique_search, page_size=page_size, page=page
    )
    assert (
        actual_range == expected_range
    ), f"expected {expected_range} but got {actual_range}"

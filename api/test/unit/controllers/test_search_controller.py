import datetime
import random
import re
from collections.abc import Callable
from enum import Enum, auto
from unittest import mock
from unittest.mock import patch
from uuid import uuid4

import pook
import pytest
from django_redis import get_redis_connection
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Terms
from structlog.testing import capture_logs

from api.controllers import search_controller
from api.controllers.elasticsearch import helpers as es_helpers
from api.controllers.search_controller import (
    FILTERED_SOURCES_CACHE_KEY,
    FILTERED_SOURCES_CACHE_VERSION,
)
from api.utils import tallies
from api.utils.dead_link_mask import get_query_hash, save_query_mask
from api.utils.search_context import SearchContext
from test.factory.es_http import (
    MOCK_DEAD_RESULT_URL_PREFIX,
    MOCK_LIVE_RESULT_URL_PREFIX,
    create_mock_es_http_image_search_response,
)
from test.factory.models.content_source import ContentSourceFactory


pytestmark = pytest.mark.django_db


cache_availability_params = pytest.mark.parametrize(
    "is_cache_reachable, cache_name",
    [(True, "search_con_cache"), (False, "unreachable_search_con_cache")],
)
# This parametrize decorator runs the test function with two scenarios:
# - one where the API can connect to Redis
# - one where it cannot and raises ``ConnectionError``
# The fixtures referenced here are defined below.


@pytest.fixture(autouse=True)
def search_con_cache(django_cache, monkeypatch):
    cache = django_cache
    monkeypatch.setattr("api.controllers.search_controller.cache", cache)
    yield cache


@pytest.fixture
def unreachable_search_con_cache(unreachable_django_cache, monkeypatch):
    cache = unreachable_django_cache
    monkeypatch.setattr("api.controllers.search_controller.cache", cache)
    yield cache


@pytest.mark.parametrize(
    "total_hits, real_result_count, page_size, page, expected",
    [
        # No results
        (0, 0, 10, 1, (0, 0)),
        # Setting page size to 0 raises an exception
        # Not possible in the actual API
        pytest.param(
            5, 5, 0, 1, (0, 0), marks=pytest.mark.raises(exception=ZeroDivisionError)
        ),
        # Fewer results than page size leads to max of result total
        (5, 5, 10, 1, (5, 1)),
        # If no real results exist, even if there are hits, fall back to 0, 0
        # (This case represents where all the links for a result are dead, for example)
        (100, 0, 10, 1, (0, 0)),
        # If there are real results and ES reports no hits, nothing is expected
        # (seems like an impossible case IRL)
        (0, 100, 10, 1, (0, 0)),
        # Evenly divisible number of pages
        (25, 5, 5, 1, (25, 5)),
        # An edge case that previously did not behave as expected with evenly divisible numbers of pages
        (20, 5, 5, 1, (20, 4)),
        # Unevenly divisible number of pages
        (21, 5, 5, 1, (21, 5)),
        # Fewer hits than page size, but result list somehow differs, use that for count
        (48, 20, 50, 1, (20, 1)),
        # Despite us applying a pagination limit, that is applied further up in the API, not at this low a level
        (2000, 20, 20, 2, (2000, 100)),
        # Page count is reduced to the current page number even though 2000 / 20 is much larger than 5
        # because despite that we have result count < page size which indicates we've exhausted the query
        (2000, 5, 20, 5, (2000, 5)),
        # First page, we got all the results and there are no further possible pages with the current page count
        (10, 10, 20, 1, (10, 1)),
        # This is here to test a case that used to erroneously produce (10, 2) by adding 1
        # to the page count when it wasn't necessary to do so.
        (10, 10, 10, 1, (10, 1)),
        # This is technically impossible because we truncate results to the page size before entering this method
        # I think the handling of this case is a likely source for the bug in the previous case
        (10, 10, 9, 1, (10, 2)),
    ],
)
def test_get_result_and_page_count(
    total_hits, real_result_count, page_size, page, expected
):
    response_obj = mock.MagicMock()
    response_obj.hits.total.value = total_hits
    results = [mock.MagicMock() for _ in range(real_result_count)]

    actual = search_controller._get_result_and_page_count(
        response_obj,
        results,
        page_size,
        page,
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
    the first page of 2 confirmed live results actually encompasses the range from
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

    assert es_helpers._paginate_with_dead_link_mask(
        s=unique_search, page_size=page_size, page=page
    ) == (start, expected_end)


class CreateMaskConfig(Enum):
    FORCE_DEAD_BITS_AT_START = auto()
    PREVENT_DEAD_BITS_AT_START = auto()
    FORCE_DEAD_BITS_AT_END = auto()
    PREVENT_DEAD_BITS_AT_END = auto()


@pytest.fixture(name="create_mask")
def create_mask_fixture() -> Callable[[Search, int, int], None]:
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
    assert es_helpers._paginate_with_dead_link_mask(
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
    actual_range = es_helpers._paginate_with_dead_link_mask(
        s=unique_search, page_size=page_size, page=page
    )
    assert (
        actual_range == expected_range
    ), f"expected {expected_range} but got {actual_range}"


@pytest.mark.parametrize(
    ("page", "page_size", "does_tally", "number_of_results_passed"),
    (
        (1, 20, True, 20),
        (2, 20, True, 20),
        (3, 20, True, 20),
        (4, 20, True, 20),
        (5, 20, False, 0),
        (1, 40, True, 40),
        (2, 40, True, 40),
        (3, 40, False, 0),
        (4, 40, False, 0),
        (5, 40, False, 0),
        (1, 10, True, 10),
        (2, 10, True, 10),
        (3, 10, True, 10),
        (4, 10, True, 10),
        (5, 10, True, 10),
        (6, 10, True, 10),
        (7, 10, True, 10),
        (8, 10, True, 10),
        (9, 10, False, 0),
        (1, 12, True, 12),
        (2, 12, True, 12),
        (3, 12, True, 12),
        (4, 12, True, 12),
        (5, 12, True, 12),
        (6, 12, True, 12),
        (7, 12, True, 8),
        (8, 12, False, 0),
    ),
)
@pytest.mark.parametrize("include_sensitive_results", (True, False))
@mock.patch.object(
    tallies, "count_provider_occurrences", wraps=tallies.count_provider_occurrences
)
@mock.patch(
    "api.controllers.search_controller._post_process_results",
)
def test_search_tallies_pages_less_than_5(
    mock_post_process_results,
    count_provider_occurrences_mock: mock.MagicMock,
    page,
    page_size,
    does_tally,
    number_of_results_passed,
    media_type_config,
    include_sensitive_results,
    settings,
):
    media_with_hits = media_type_config.model_factory.create_batch(
        size=page_size, with_hit=True
    )
    mock_post_process_results.return_value = [hit for _, hit in media_with_hits]

    serializer = media_type_config.search_request_serializer(
        data={
            "q": "dogs",
            "unstable__include_sensitive_results": include_sensitive_results,
        },
        context={
            "media_type": media_type_config.media_type,
        },
    )
    serializer.is_valid()

    search_controller.query_media(
        search_params=serializer,
        ip=0,
        origin_index=media_type_config.origin_index,
        exact_index=False,
        page=page,
        page_size=page_size,
        filter_dead=False,
    )

    if does_tally:
        count_provider_occurrences_mock.assert_called_once_with(
            mock.ANY,
            media_type_config.origin_index
            if include_sensitive_results
            else media_type_config.filtered_index,
        )
        passed_results = count_provider_occurrences_mock.call_args_list[0][0][0]
        assert len(passed_results) == number_of_results_passed
    else:
        count_provider_occurrences_mock.assert_not_called()


@mock.patch.object(
    tallies, "count_provider_occurrences", wraps=tallies.count_provider_occurrences
)
@mock.patch(
    "api.controllers.search_controller._post_process_results",
)
def test_search_tallies_handles_empty_page(
    mock_post_process_results,
    count_provider_occurrences_mock: mock.MagicMock,
    media_type_config,
):
    mock_post_process_results.return_value = None

    serializer = media_type_config.search_request_serializer(
        data={"q": "dogs"}, context={"media_type": media_type_config.media_type}
    )
    serializer.is_valid()

    search_controller.query_media(
        search_params=serializer,
        ip=0,
        origin_index=media_type_config.origin_index,
        exact_index=False,
        # Force calculated result depth length to include results within 80th position and above
        # to force edge case where retrieved results are only partially tallied.
        page=1,
        page_size=100,
        filter_dead=True,
    )

    count_provider_occurrences_mock.assert_not_called()


@pytest.mark.parametrize(
    ("feature_enabled", "include_sensitive_results", "index_suffix"),
    (
        (True, True, ""),
        (True, False, "-filtered"),
        (False, True, ""),
        (False, False, ""),
    ),
)
@mock.patch("api.controllers.search_controller.Search", wraps=Search)
def test_resolves_index(
    search_class,
    media_type_config,
    feature_enabled,
    include_sensitive_results,
    index_suffix,
    settings,
):
    origin_index = media_type_config.origin_index
    searched_index = f"{origin_index}{index_suffix}"

    settings.ENABLE_FILTERED_INDEX_QUERIES = feature_enabled

    serializer = media_type_config.search_request_serializer(
        data={"unstable__include_sensitive_results": include_sensitive_results},
        context={"media_type": media_type_config.media_type},
    )
    serializer.is_valid()

    search_controller.query_media(
        search_params=serializer,
        ip=0,
        origin_index=origin_index,
        exact_index=False,
        page=1,
        page_size=20,
        filter_dead=False,
    )

    search_class.assert_called_once_with(index=searched_index)


@mock.patch(
    "api.controllers.search_controller._post_process_results",
    wraps=search_controller._post_process_results,
)
@mock.patch("api.controllers.search_controller.SearchContext")
@pook.on
def test_no_post_process_results_recursion(
    mock_search_context,
    wrapped_post_process_results,
    image_media_type_config,
    settings,
    # request the redis mock to auto-clean Redis between each test run
    # otherwise the dead link query mask causes test details to leak
    # between each run
    redis,
):
    # Search context does not matter for this test, so we can mock it
    # to avoid needing to account for additional ES requests
    mock_search_context.build.return_value = SearchContext(set(), set())

    hit_count = 5
    mock_es_response = create_mock_es_http_image_search_response(
        index=image_media_type_config.origin_index,
        total_hits=45,
        hit_count=hit_count,
    )

    # `origin_index` enforced by passing `exact_index=True` below.
    es_endpoint = (
        f"{settings.ES_ENDPOINT}/{image_media_type_config.origin_index}/_search"
    )

    mock_search = (
        pook.post(es_endpoint)
        .times(1)
        .reply(200)
        .header("x-elastic-product", "Elasticsearch")
        .json(mock_es_response)
        .mock
    )

    # Ensure dead link filtering does not remove any results
    pook.head(
        pook.regex(rf"{MOCK_LIVE_RESULT_URL_PREFIX}/\d"),
    ).times(hit_count).reply(200)

    serializer = image_media_type_config.search_request_serializer(
        # This query string does not matter, ultimately, as pook is mocking
        # the ES response regardless of the input
        data={"q": "bird perched"},
        context={"media_type": image_media_type_config.media_type},
    )
    serializer.is_valid()
    results, _, _, _ = search_controller.query_media(
        search_params=serializer,
        ip=0,
        origin_index=image_media_type_config.origin_index,
        exact_index=True,
        page=3,
        page_size=20,
        filter_dead=True,
    )

    assert {r["_source"]["identifier"] for r in mock_es_response["hits"]["hits"]} == {
        r.identifier for r in results
    }

    assert wrapped_post_process_results.call_count == 1
    assert mock_search.total_matches == 1


@pytest.mark.parametrize(
    # both scenarios force `post_process_results`
    # to recurse to fill the page due to the dead link
    # configuration present in the test body
    "page, page_size, mock_total_hits",
    # Note the following
    # - DEAD_LINK_RATIO causes all query sizes to start at double the page size
    # - The test function is configured so that each request only returns 2 live
    #   results
    # - We clear the redis cache between each test, meaning there is no query-based
    #   dead link mask. This forces `from` to 0 for each case.
    # - Recursion should only continue while results still exist that could fulfill
    #   the requested page size. Once the available hits are exhausted, the function
    #   should stop recursing. This is why exceeding  or matching the available
    #   hits is significant.
    (
        # First request: from: 0, size: 10
        # Second request: from: 0, size: 15, exceeds max results
        pytest.param(1, 5, 12, id="first_page"),
        # First request: from: 0, size: 22
        # Second request: from 0, size: 33, exceeds max results
        pytest.param(3, 4, 32, id="last_page"),
        # First request: from: 0, size: 22
        # Second request: from 0, size: 33, matches max results
        pytest.param(3, 4, 33, id="last_page_with_exact_max_results"),
    ),
)
@mock.patch(
    "api.controllers.search_controller._post_process_results",
    wraps=search_controller._post_process_results,
)
@mock.patch("api.controllers.search_controller.SearchContext")
@pook.on
def test_post_process_results_recurses_as_needed(
    mock_search_context,
    wrapped_post_process_results,
    image_media_type_config,
    settings,
    page,
    page_size,
    mock_total_hits,
    # request the redis mock to auto-clean Redis between each test run
    # otherwise the dead link query mask causes test details to leak
    # between each run
    redis,
):
    # Search context does not matter for this test, so we can mock it
    # to avoid needing to account for additional ES requests
    mock_search_context.build.return_value = SearchContext(set(), set())

    mock_es_response_1 = create_mock_es_http_image_search_response(
        index=image_media_type_config.origin_index,
        total_hits=mock_total_hits,
        hit_count=10,
        live_hit_count=2,
    )

    mock_es_response_2 = create_mock_es_http_image_search_response(
        index=image_media_type_config.origin_index,
        total_hits=mock_total_hits,
        hit_count=4,
        live_hit_count=2,
        base_hits=mock_es_response_1["hits"]["hits"],
    )

    # `origin_index` enforced by passing `exact_index=True` below.
    es_endpoint = (
        f"{settings.ES_ENDPOINT}/{image_media_type_config.origin_index}/_search"
    )

    # `from` is always 0 if there is no query mask
    # see `_paginate_with_dead_link_mask` branch 1
    # Testing this with a query mask would introduce far more complexity
    # with no significant benefit
    re.compile('from":0')

    mock_first_es_request = (
        pook.post(es_endpoint)
        # The dead link ratio causes the initial query size to double
        .body(re.compile(f'size":{(page_size * page) * 2}'))
        .body(re.compile('from":0'))
        .times(1)
        .reply(200)
        .header("x-elastic-product", "Elasticsearch")
        .json(mock_es_response_1)
        .mock
    )

    mock_second_es_request = (
        pook.post(es_endpoint)
        # Size is clamped to the total number of available hits
        .body(re.compile(f'size":{mock_total_hits}'))
        .body(re.compile('from":0'))
        .times(1)
        .reply(200)
        .header("x-elastic-product", "Elasticsearch")
        .json(mock_es_response_2)
        .mock
    )

    live_results = [
        r
        for r in mock_es_response_2["hits"]["hits"]
        if r["_source"]["url"].startswith(MOCK_LIVE_RESULT_URL_PREFIX)
    ]

    pook.head(pook.regex(rf"{MOCK_LIVE_RESULT_URL_PREFIX}/\d")).times(
        len(live_results)
    ).reply(200)

    pook.head(pook.regex(rf"{MOCK_DEAD_RESULT_URL_PREFIX}/\d")).times(
        len(mock_es_response_2["hits"]["hits"]) - len(live_results)
    ).reply(400)

    serializer = image_media_type_config.search_request_serializer(
        # This query string does not matter, ultimately, as pook is mocking
        # the ES response regardless of the input
        data={"q": "bird perched"},
        context={"media_type": image_media_type_config.media_type},
    )
    serializer.is_valid()
    results, _, _, _ = search_controller.query_media(
        search_params=serializer,
        ip=0,
        origin_index=image_media_type_config.origin_index,
        exact_index=True,
        page=page,
        page_size=page_size,
        filter_dead=True,
    )

    assert mock_first_es_request.total_matches == 1
    assert mock_second_es_request.total_matches == 1

    assert {r["_source"]["identifier"] for r in live_results} == {
        r.identifier for r in results
    }

    assert wrapped_post_process_results.call_count == 2


@mock.patch(
    "api.controllers.search_controller.check_dead_links",
)
def test_excessive_recursion_in_post_process(
    mock_check_dead_links,
    image_media_type_config,
    redis,
    caplog,
):
    def _delete_all_results_but_first(_, __, results, ___):
        results[1:] = []

    mock_check_dead_links.side_effect = _delete_all_results_but_first

    serializer = image_media_type_config.search_request_serializer(
        # This query string does not matter, ultimately, as pook is mocking
        # the ES response regardless of the input
        data={"q": "bird perched"},
        context={"media_type": image_media_type_config.media_type},
    )
    serializer.is_valid()

    with capture_logs() as cap_logs:
        results, _, _, _ = search_controller.query_media(
            search_params=serializer,
            ip=0,
            origin_index=image_media_type_config.origin_index,
            exact_index=True,
            page=1,
            page_size=2,
            filter_dead=True,
        )
    messages = [record["event"] for record in cap_logs]
    assert "Nesting threshold breached" in messages


@pytest.mark.django_db
@cache_availability_params
@pytest.mark.parametrize(
    "excluded_count, result",
    [(2, Terms(source=["source1", "source2"])), (0, None)],
)
def test_get_excluded_sources_query_returns_excluded(
    excluded_count, result, is_cache_reachable, cache_name, request
):
    cache = request.getfixturevalue(cache_name)

    if is_cache_reachable:
        cache.set(
            key=FILTERED_SOURCES_CACHE_KEY,
            version=FILTERED_SOURCES_CACHE_VERSION,
            timeout=30,
            value=[f"source{i + 1}" for i in range(excluded_count)],
        )
    else:
        for i in range(excluded_count):
            ContentSourceFactory.create(
                created_on=datetime.datetime.now(),
                source_identifier=f"source{i + 1}",
                source_name=f"Source {i + 1}",
                filter_content=True,
            )

    with capture_logs() as cap_logs:
        assert search_controller.get_excluded_sources_query() == result

    if not is_cache_reachable:
        messages = [record["event"] for record in cap_logs]
        assert all(
            message in messages
            for message in [
                "Redis connect failed, cannot get cached filtered sources.",
                "Redis connect failed, cannot cache filtered sources.",
            ]
        )


@cache_availability_params
def test_get_sources_returns_stats(is_cache_reachable, cache_name, request, caplog):
    cache = request.getfixturevalue(cache_name)

    if is_cache_reachable:
        cache.set("sources-multimedia", value={"source_1": "1000", "source_2": "1000"})

    with capture_logs() as cap_logs, patch(
        "api.controllers.search_controller.get_raw_es_response",
        return_value={
            "aggregations": {
                "unique_sources": {
                    "buckets": [
                        {"key": "source_1", "doc_count": 1000},
                        {"key": "source_2", "doc_count": 1000},
                    ]
                }
            }
        },
    ):
        assert search_controller.get_sources("multimedia") == {
            "source_1": 1000,
            "source_2": 1000,
        }

    if not is_cache_reachable:
        messages = [record["event"] for record in cap_logs]
        assert all(
            message in messages
            for message in [
                "Redis connect failed, cannot get cached sources.",
                "Redis connect failed, cannot cache sources.",
            ]
        )

from unittest.mock import patch
from uuid import uuid4

import pytest

from api.constants import privilege
from api.controllers.elasticsearch.helpers import DEAD_LINK_RATIO


@pytest.fixture
def unique_query_hash(redis, monkeypatch):
    def get_unique_hash(*args, **kwargs):
        return str(uuid4())

    monkeypatch.setattr(
        "api.controllers.search_controller.get_query_hash", get_unique_hash
    )


@pytest.fixture
def empty_validation_cache(monkeypatch):
    def get_empty_cached_statuses(_, image_urls):
        return [None] * len(image_urls)

    monkeypatch.setattr(
        "api.utils.check_dead_links._get_cached_statuses",
        get_empty_cached_statuses,
    )


_MAKE_HEAD_REQUESTS_MODULE_PATH = "api.utils.check_dead_links._make_head_requests"


def _patch_make_head_requests():
    def _make_head_requests(urls):
        responses = []
        for idx, url in enumerate(urls):
            status_code = 200 if idx % 10 != 0 else 404
            responses.append((url, status_code))
        return responses

    return patch(_MAKE_HEAD_REQUESTS_MODULE_PATH, side_effect=_make_head_requests)


def patch_link_validation_dead_for_count(count):
    total_res_count = 0

    def _make_head_requests(urls):
        nonlocal total_res_count
        responses = []
        for idx, url in enumerate(urls):
            total_res_count += 1
            status_code = 404 if total_res_count <= count else 200
            responses.append((url, status_code))
        return responses

    return patch(_MAKE_HEAD_REQUESTS_MODULE_PATH, side_effect=_make_head_requests)


@pytest.mark.django_db
@_patch_make_head_requests()
def test_dead_link_filtering(mocked_map, api_client):
    path = "/v1/images/"
    query_params = {"q": "*", "page_size": 20}

    # Make a request that does not filter dead links...
    with patch(
        "api.views.image_views.ImageViewSet.get_db_results"
    ) as mock_get_db_result:
        mock_get_db_result.side_effect = lambda value: value
        res_with_dead_links = api_client.get(
            path,
            query_params | {"filter_dead": False},
        )
        # ...and ensure that our patched function was not called
        mocked_map.assert_not_called()

        # Make a request that filters dead links...
        res_without_dead_links = api_client.get(
            path,
            query_params | {"filter_dead": True},
        )
        # ...and ensure that our patched function was called
        mocked_map.assert_called()

    assert res_with_dead_links.status_code == 200
    assert res_without_dead_links.status_code == 200

    data_with_dead_links = res_with_dead_links.json()
    data_without_dead_links = res_without_dead_links.json()

    res_1_ids = {result["id"] for result in data_with_dead_links["results"]}
    res_2_ids = {result["id"] for result in data_without_dead_links["results"]}
    # In this case, both have 20 results as the dead link filter has "back filled" the
    # pages of dead links. See the subsequent test for the case when this does not
    # occur (i.e., when the entire first page of links is dead).
    assert len(res_1_ids) == 20
    assert len(res_2_ids) == 20
    assert bool(res_1_ids - res_2_ids)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("filter_dead", "page_size", "expected_result_count"),
    (
        (True, 20, 0),
        (False, 20, 20),
    ),
)
def test_dead_link_filtering_all_dead_links(
    api_client,
    filter_dead,
    page_size,
    expected_result_count,
    unique_query_hash,
    empty_validation_cache,
):
    path = "/v1/images/"
    query_params = {"q": "*", "page_size": page_size}

    with patch(
        "api.views.image_views.ImageViewSet.get_db_results"
    ) as mock_get_db_result:
        mock_get_db_result.side_effect = lambda value: value
        with patch_link_validation_dead_for_count(page_size / DEAD_LINK_RATIO):
            response = api_client.get(
                path,
                query_params | {"filter_dead": filter_dead},
            )

    assert response.status_code == 200

    res_json = response.json()

    assert len(res_json["results"]) == expected_result_count
    if expected_result_count == 0:
        assert res_json["result_count"] == 0


@pytest.fixture
def search_factory(api_client):
    """Allow passing url parameters along with a search request."""

    def _parameterized_search(**kwargs):
        response = api_client.get("/v1/images/", kwargs)
        assert response.status_code == 200
        parsed = response.json()
        return parsed

    return _parameterized_search


@pytest.fixture
def search_without_dead_links(search_factory):
    """Test with ``filter_dead`` parameter set to true."""

    def _search_without_dead_links(**kwargs):
        return search_factory(filter_dead=True, **kwargs)

    return _search_without_dead_links


@pytest.mark.django_db
def test_page_size_removing_dead_links(search_without_dead_links):
    """
    Test whether the number of results returned is equal to the requested page size.

    We have about 500 dead links in the sample data and should have around
    8 dead links in the first 100 results on a query composed of a single
    wildcard operator.
    """

    data = search_without_dead_links(q="*", page_size=20)
    assert len(data["results"]) == 20


@pytest.mark.django_db
def test_page_consistency_removing_dead_links(search_without_dead_links):
    """Test that results in consecutive pages don't repeat when filtering dead links."""

    page_size = 5
    total_pages = int(privilege.PAGINATION_DEPTH.anonymous / page_size)

    page_results = []
    for page in range(1, total_pages + 1):
        page_data = search_without_dead_links(q="*", page_size=page_size, page=page)
        page_results += page_data["results"]

    def no_duplicates(xs):
        s = set()
        for x in xs:
            if x in s:
                return False
            s.add(x)
        return True

    ids = list(map(lambda x: x["id"], page_results))
    # No results should be repeated so we should have no duplicate ids
    assert no_duplicates(ids)

from test.constants import API_URL
from unittest.mock import MagicMock, patch

import pytest
import requests

from catalog.api.utils.pagination import MAX_TOTAL_PAGE_COUNT


def _patch_redis():
    def redis_mget(keys, *_, **__):
        """
        Patch for ``redis.mget`` used by ``validate_images`` to use validity
        information from the cache
        """
        return [None] * len(keys)

    mock_conn = MagicMock()
    mock_conn.mget = MagicMock(side_effect=redis_mget)
    return patch("django_redis.get_redis_connection", return_value=mock_conn)


def _patch_grequests():
    def grequests_map(reqs, *_, **__):
        """
        Patch for ``grequests.map`` used by ``validate_images`` to filter
        and remove dead links
        """
        responses = []
        for idx in range(len(list(reqs))):
            mocked_res = MagicMock()
            mocked_res.status_code = 200 if idx % 10 != 0 else 404
            responses.append(mocked_res)
        return responses

    return patch("grequests.map", side_effect=grequests_map)


@pytest.mark.django_db
@_patch_redis()
@_patch_grequests()
def test_dead_link_filtering(mocked_map, _, client):
    path = "/v1/images/"
    query_params = {"q": "*", "page_size": 20}

    # Make a request that does not filter dead links...
    res_with_dead_links = client.get(
        path,
        query_params | {"filter_dead": False},
    )
    # ...and ensure that our patched function was not called
    mocked_map.assert_not_called()

    # Make a request that filters dead links...
    res_without_dead_links = client.get(
        path,
        query_params | {"filter_dead": True},
    )
    # ...and ensure that our patched function was called
    mocked_map.assert_called()

    assert res_with_dead_links.status_code == 200
    assert res_without_dead_links.status_code == 200

    data_with_dead_links = res_with_dead_links.json()
    data_without_dead_links = res_without_dead_links.json()

    res_1_ids = set(result["id"] for result in data_with_dead_links["results"])
    res_2_ids = set(result["id"] for result in data_without_dead_links["results"])
    assert bool(res_1_ids - res_2_ids)


@pytest.fixture
def search_factory(client):
    """
    Allows passing url parameters along with a search request.
    """

    def _parameterized_search(**kwargs):
        response = requests.get(f"{API_URL}/v1/images", params=kwargs, verify=False)
        assert response.status_code == 200
        parsed = response.json()
        return parsed

    return _parameterized_search


@pytest.fixture
def search_without_dead_links(search_factory):
    """
    Here we pass filter_dead = True.
    """

    def _search_without_dead_links(**kwargs):
        return search_factory(filter_dead=True, **kwargs)

    return _search_without_dead_links


@pytest.mark.django_db
def test_page_size_removing_dead_links(search_without_dead_links):
    """
    We have about 500 dead links in the sample data and should have around
    8 dead links in the first 100 results on a query composed of a single
    wildcard operator.

    Test whether the number of results returned is equal to the requested
    page_size of 20.
    """
    data = search_without_dead_links(q="*", page_size=20)
    assert len(data["results"]) == 20


@pytest.mark.django_db
def test_page_consistency_removing_dead_links(search_without_dead_links):
    """
    Test the results returned in consecutive pages are never repeated when
    filtering out dead links.
    """
    total_pages = MAX_TOTAL_PAGE_COUNT
    page_size = 5

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


@pytest.mark.django_db
def test_max_page_count():
    response = requests.get(
        f"{API_URL}/v1/images", params={"page": MAX_TOTAL_PAGE_COUNT + 1}, verify=False
    )
    assert response.status_code == 400

from unittest.mock import patch
from urllib.parse import urlparse
from uuid import uuid4

from django.conf import settings

import pook
import pytest

from api.constants import restricted_features
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


def _mock_get_db_results(results, include_addons=False):
    return (results, [])


def _patch_make_head_requests():
    def _make_head_requests(urls, *args, **kwargs):
        responses = []
        for idx, url in enumerate(urls):
            status_code = 200 if idx % 10 != 0 else 404
            responses.append((url, status_code))
        return responses

    return patch(_MAKE_HEAD_REQUESTS_MODULE_PATH, side_effect=_make_head_requests)


def patch_link_validation_dead_for_count(count):
    total_res_count = 0

    def _make_head_requests(urls, *args, **kwargs):
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
        mock_get_db_result.side_effect = _mock_get_db_results
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
        mock_get_db_result.side_effect = _mock_get_db_results
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


def answer_link_checks(dead_urls):
    """
    Answer the dead link checks with ``pook`` instead of the providers.

    ``dead_urls`` respond with 404 and every other URL with 200. Requests to
    Elasticsearch still go through.

    :return: the mock that answers the live URLs
    """

    for url in dead_urls:
        pook.head(url).persist().reply(404)
    live = pook.head(pook.regex(r"^https?://")).persist()
    live.reply(200)

    pook.enable_network(urlparse(settings.ES_ENDPOINT).hostname)
    pook.on()
    return live


@pytest.mark.django_db
@pytest.mark.pook(start_active=False)
def test_page_size_removing_dead_links(search_factory):
    """Dead links are removed, and the page is backfilled to the requested size."""

    results = search_factory(q="*", page_size=20, filter_dead=False)["results"]
    dead_urls = {result["url"] for result in results[::4]}
    live_ids = [result["id"] for result in results if result["url"] not in dead_urls]

    answer_link_checks(dead_urls)
    data = search_factory(q="*", page_size=20, filter_dead=True)

    ids = [result["id"] for result in data["results"]]
    assert len(ids) == 20
    assert ids[: len(live_ids)] == live_ids
    assert not dead_urls & {result["url"] for result in data["results"]}


@pytest.mark.django_db
@pytest.mark.pook(start_active=False)
def test_page_consistency_removing_dead_links(search_factory):
    """Consecutive pages don't repeat or drop results when filtering dead links."""

    page_size = 5
    total_pages = int(restricted_features.MAX_RESULT_COUNT.anonymous / page_size)

    dead_urls = set()
    for page in range(1, total_pages * page_size // 20 + 1):
        results = search_factory(q="*", page_size=20, page=page, filter_dead=False)[
            "results"
        ]
        dead_urls |= {result["url"] for result in results[::4]}

    answer_link_checks(dead_urls)
    page_results = []
    for page in range(1, total_pages + 1):
        page_data = search_factory(
            q="*", page_size=page_size, page=page, filter_dead=True
        )
        page_results += page_data["results"]

    ids = [result["id"] for result in page_results]
    assert len(ids) == total_pages * page_size
    assert len(set(ids)) == len(ids)
    assert not dead_urls & {result["url"] for result in page_results}


@pytest.mark.django_db
@pytest.mark.pook(start_active=False)
def test_related_filters_dead_links_by_default_setting(api_client, settings):
    """
    The related view checks links only when ``FILTER_DEAD_LINKS_BY_DEFAULT``
    is enabled, as search does when ``filter_dead`` isn't passed.
    """

    item = api_client.get("/v1/images/", {"q": "dog"}).json()["results"][0]
    path = f"/v1/images/{item['id']}/related/"

    settings.FILTER_DEAD_LINKS_BY_DEFAULT = False
    results = api_client.get(path).json()["results"]
    assert len(results) == 10
    dead_urls = {result["url"] for result in results[:3]}
    live_ids = [result["id"] for result in results if result["url"] not in dead_urls]

    live = answer_link_checks(dead_urls)
    assert api_client.get(path).json()["results"] == results
    assert live.calls == 0

    settings.FILTER_DEAD_LINKS_BY_DEFAULT = True
    filtered = api_client.get(path).json()["results"]

    ids = [result["id"] for result in filtered]
    assert len(ids) == 10
    assert ids[: len(live_ids)] == live_ids
    assert not dead_urls & {result["url"] for result in filtered}

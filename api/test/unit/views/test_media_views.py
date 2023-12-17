from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, patch
from uuid import uuid4

from rest_framework.response import Response

import pytest
import pytest_django.asserts

from api.models.models import ContentProvider


def test_hits_to_db_handles_missing_entries(api_client, media_type_config):
    """
    The ``get_db_results`` function should handle the case where a media entry
    is missing from the database.
    """

    viewset = media_type_config.viewset_class()

    hits = []
    for _ in range(10):
        hit = SimpleNamespace()
        hit.identifier = str(uuid4())
        hit.meta = SimpleNamespace()
        hits.append(hit)

    # When the DB has no entries for any of the identifiers...
    with patch.object(
        viewset, "get_queryset", return_value=Mock(filter=Mock(return_value=[]))
    ):
        results = viewset.get_db_results(hits)

    # ...the function returns the hits.
    assert results == hits


@pytest.mark.django_db
def test_list_query_count(api_client, media_type_config):
    num_results = 20

    # Since controller returns a list of ``Hit``s, not model instances, we must
    # set the ``meta`` param on each of them to match the shape of ``Hit``.
    results = media_type_config.model_factory.create_batch(size=num_results)
    for result in results:
        result.meta = None

    controller_ret = (
        results,
        1,  # num_pages
        num_results,
        {},  # search_context
    )
    with patch(
        "api.views.media_views.search_controller",
        query_media=MagicMock(return_value=controller_ret),
    ), patch(
        "api.serializers.media_serializers.search_controller",
        get_sources=MagicMock(return_value={}),
    ), pytest_django.asserts.assertNumQueries(
        1
    ):
        res = api_client.get(f"/v1/{media_type_config.url_prefix}/")

    assert res.status_code == 200


@pytest.mark.django_db
def test_retrieve_query_count(api_client, media_type_config):
    media = media_type_config.model_factory.create()

    # This number goes up without `select_related` in the viewset queryset.
    with pytest_django.asserts.assertNumQueries(1):
        res = api_client.get(f"/v1/{media_type_config.url_prefix}/{media.identifier}/")

    assert res.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize(
    "path, expected_params",
    [
        pytest.param("tag/cat/", {"tag": "cat"}, id="tag"),
        pytest.param("source/flickr/", {"source": "flickr"}, id="source"),
        pytest.param(
            "source/flickr/creator/cat/",
            {"source": "flickr", "creator": "cat"},
            id="source_creator",
        ),
    ],
)
def test_collection_parameters(path, expected_params, api_client):
    mock_get_media_results = MagicMock(return_value=Response())

    with patch(
        "api.views.media_views.MediaViewSet.get_media_results",
        new_callable=lambda: mock_get_media_results,
    ) as mock_get_media_results:
        api_client.get(f"/v1/images/{path}")

    actual_params = mock_get_media_results.call_args[0][3]
    request_kind = mock_get_media_results.call_args[0][1]

    assert mock_get_media_results.called
    assert actual_params == expected_params
    assert request_kind == "collection"


@pytest.mark.parametrize(
    "filter_content", (True, False), ids=lambda x: "filtered" if x else "not_filtered"
)
@pytest.mark.django_db
def test_get_queryset_provider_filtering(api_client, media_type_config, filter_content):
    test_provider = "test_provider_filtering_provider"
    media = media_type_config.model_factory.create(provider=test_provider)

    ContentProvider.objects.create(
        created_on=datetime.now(tz=timezone.utc),
        provider_identifier=test_provider,
        provider_name="Test Provider",
        domain_name="https://example.com",
        filter_content=filter_content,
    )

    res = api_client.get(f"/v1/{media_type_config.url_prefix}/{media.identifier}/")

    assert res.status_code == (404 if filter_content else 200)


@pytest.mark.django_db
def test_get_queryset_does_not_exclude_works_without_contentprovider_entry(
    api_client, media_type_config
):
    """
    Search only excludes works when a content provider entry exists AND that
    entry has `filter_content=True`. Critically this means it will include works
    from providers that do not have a content provider entry. To ensure the individual
    media views follow the same behaviour, this test retrieves a single media result
    assigned to a provider that has no content provider entry.
    """
    test_provider = f"test_provider_{uuid4()}"
    media = media_type_config.model_factory.create(provider=test_provider)

    assert (
        ContentProvider.objects.filter(provider_identifier=test_provider).exists()
        is False
    )

    res = api_client.get(f"/v1/{media_type_config.url_prefix}/{media.identifier}/")

    assert res.status_code == 200

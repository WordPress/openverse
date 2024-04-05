from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
import pytest_django.asserts

from api.models.models import ContentProvider


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
    ), pytest_django.asserts.assertNumQueries(1):
        res = api_client.get(f"/v1/{media_type_config.url_prefix}/")

    assert res.status_code == 200


@pytest.mark.django_db
def test_retrieve_query_count(api_client, media_type_config):
    media = media_type_config.model_factory.create()

    # This number goes up without `select_related` in the viewset queryset.
    with pytest_django.asserts.assertNumQueries(1):
        res = api_client.get(f"/v1/{media_type_config.url_prefix}/{media.identifier}/")

    assert res.status_code == 200


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

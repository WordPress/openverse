from unittest.mock import MagicMock, patch

import pytest
import pytest_django.asserts


@pytest.mark.django_db
def test_list_query_count(api_client, media_type_config):
    num_results = 20
    controller_ret = (
        media_type_config.model_factory.create_batch(size=num_results),  # results
        1,  # num_pages
        num_results,
        {},  # search_context
    )
    with patch(
        "api.views.media_views.search_controller",
        search=MagicMock(return_value=controller_ret),
    ), patch(
        "api.serializers.media_serializers.search_controller",
        get_sources=MagicMock(return_value={}),
    ), pytest_django.asserts.assertNumQueries(
        1
    ):
        res = api_client.get(f"/v1/{media_type_config.media_type}/")

    assert res.status_code == 200


@pytest.mark.django_db
def test_retrieve_query_count(api_client, media_type_config):
    media = media_type_config.model_factory.create()

    # This number goes up without `select_related` in the viewset queryset.
    with pytest_django.asserts.assertNumQueries(1):
        res = api_client.get(f"/v1/{media_type_config.media_type}/{media.identifier}/")

    assert res.status_code == 200

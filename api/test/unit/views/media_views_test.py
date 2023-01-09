from test.factory.models.audio import AudioFactory
from test.factory.models.image import ImageFactory
from unittest.mock import MagicMock, patch

import pytest
import pytest_django.asserts


@pytest.mark.django_db
@pytest.mark.parametrize(
    "media_type, media_factory",
    [
        ("images", ImageFactory),
        ("audio", AudioFactory),
    ],
)
def test_list_query_count(api_client, media_type, media_factory):
    num_results = 20
    controller_ret = (
        [
            MagicMock(identifier=str(media_factory.create().identifier))
            for _ in range(num_results)
        ],  # results
        1,  # num_pages
        num_results,
    )
    with patch(
        "catalog.api.views.media_views.search_controller",
        search=MagicMock(return_value=controller_ret),
    ), patch(
        "catalog.api.serializers.media_serializers.search_controller",
        get_sources=MagicMock(return_value={}),
    ), pytest_django.asserts.assertNumQueries(
        1
    ):
        res = api_client.get(f"/v1/{media_type}/")

    assert res.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("media_type", "media_factory"),
    (
        ("images", ImageFactory),
        ("audio", AudioFactory),
    ),
)
def test_retrieve_query_count(api_client, media_type, media_factory):
    media = media_factory.create()

    # This number goes up without `select_related` in the viewset queryset.
    with pytest_django.asserts.assertNumQueries(1):
        res = api_client.get(f"/v1/{media_type}/{media.identifier}/")

    assert res.status_code == 200

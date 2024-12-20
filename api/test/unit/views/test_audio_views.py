from unittest.mock import MagicMock, patch

import pytest
import pytest_django.asserts

from test.factory.models import AudioFactory


@pytest.mark.parametrize("peaks, query_count", [(True, 2), (False, 1)])
@pytest.mark.django_db
def test_peaks_param_determines_addons(api_client, peaks, query_count):
    num_results = 20

    # Since controller returns a list of ``Hit``s, not model instances, we must
    # set the ``meta`` param on each of them to match the shape of ``Hit``.
    results = AudioFactory.create_batch(size=num_results)
    for result in results:
        result.meta = None

    controller_ret = (
        results,
        1,  # num_pages
        num_results,
        {},  # search_context
    )
    with (
        patch(
            "api.views.media_views.search_controller",
            query_media=MagicMock(return_value=controller_ret),
        ),
        patch(
            "api.serializers.media_serializers.search_controller",
            get_sources=MagicMock(return_value={}),
        ),
        pytest_django.asserts.assertNumQueries(query_count),
    ):
        res = api_client.get(f"/v1/audio/?peaks={peaks}")

    assert res.status_code == 200

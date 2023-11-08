from test.factory.es_http import (
    MOCK_LIVE_RESULT_URL_PREFIX,
    create_mock_es_http_image_response_with_identifier,
    create_mock_es_http_image_search_response,
)
from test.factory.models import ImageFactory
from unittest import mock

import pook
import pytest

from api.controllers import search_controller


pytestmark = pytest.mark.django_db


@mock.patch(
    "api.controllers.search_controller.related_media",
    wraps=search_controller.related_media,
)
@pook.on
def test_related_media(
    wrapped_related_results,
    image_media_type_config,
    settings,
    # request the redis mock to auto-clean Redis between each test run
    # otherwise the dead link query mask causes test details to leak
    # between each run
    redis,
):
    image = ImageFactory.create()

    # Mock the ES response for the item itself
    es_original_index_endpoint = (
        f"{settings.ES_ENDPOINT}/{image_media_type_config.origin_index}/_search"
    )
    mock_es_hit_response = create_mock_es_http_image_response_with_identifier(
        index=image_media_type_config.origin_index,
        identifier=image.identifier,
    )
    pook.post(es_original_index_endpoint).times(1).reply(200).header(
        "x-elastic-product", "Elasticsearch"
    ).json(mock_es_hit_response)

    # Mock the post process ES requests
    pook.head(pook.regex(rf"{MOCK_LIVE_RESULT_URL_PREFIX}/\d")).times(20).reply(200)

    # Related only queries the filtered index, so we mock that.
    es_filtered_index_endpoint = (
        f"{settings.ES_ENDPOINT}/{image_media_type_config.filtered_index}/_search"
    )
    mock_es_response = create_mock_es_http_image_search_response(
        index=image_media_type_config.origin_index,
        total_hits=20,
        live_hit_count=20,
        hit_count=10,
    )

    # Testing the ES query
    es_related_query = {
        "from": 0,
        "query": {
            "bool": {
                "minimum_should_match": 1,
                "must_not": [
                    {"term": {"identifier": image.identifier}},
                    {"term": {"mature": True}},
                ],
                "should": [
                    {"match": {"title": "Bird Nature Photo"}},
                    {"simple_query_string": {"fields": ["tags.name"], "query": "bird"}},
                ],
            }
        },
        "size": 20,
    }
    mock_related = (
        pook.post(es_filtered_index_endpoint)
        .json(es_related_query)  # Testing that ES query is correct
        .times(1)
        .reply(200)
        .header("x-elastic-product", "Elasticsearch")
        .json(mock_es_response)
        .mock
    )

    results = search_controller.related_media(
        uuid=image.identifier,
        index=image_media_type_config.origin_index,
        filter_dead=True,
    )
    assert len(results) == 10
    assert wrapped_related_results.call_count == 1
    assert mock_related.total_matches == 1

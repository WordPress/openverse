from unittest import mock

import pook
import pytest

from api.controllers.elasticsearch import related
from api.controllers.search_controller import (
    ENABLED_SOURCES_CACHE_KEY,
    ENABLED_SOURCES_CACHE_VERSION,
)
from test.factory.es_http import (
    MOCK_LIVE_RESULT_URL_PREFIX,
    create_mock_es_http_image_response_with_identifier,
    create_mock_es_http_image_search_response,
)
from test.factory.models import ImageFactory


pytestmark = pytest.mark.django_db


@pytest.fixture
def enabled_sources_cache(django_cache, monkeypatch):
    cache = django_cache
    monkeypatch.setattr("api.controllers.search_controller.cache", cache)

    enabled_source = "enabled_source"
    cache_value = [enabled_source]
    cache.set(
        key=ENABLED_SOURCES_CACHE_KEY,
        version=ENABLED_SOURCES_CACHE_VERSION,
        value=cache_value,
        timeout=1,
    )

    yield enabled_source

    cache.delete(ENABLED_SOURCES_CACHE_KEY, version=ENABLED_SOURCES_CACHE_VERSION)


@mock.patch(
    "api.controllers.elasticsearch.related.related_media",
    wraps=related.related_media,
)
@pook.on
def test_related_media(
    wrapped_related_results,
    image_media_type_config,
    settings,
    enabled_sources_cache,
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
                "filter": [
                    {"terms": {"source": [enabled_sources_cache]}},
                ],
                "must_not": [
                    {"term": {"mature": True}},
                    {"term": {"identifier": image.identifier}},
                ],
                "should": [
                    {"match": {"title": "Bird Nature Photo"}},
                    {"terms": {"tags.name.keyword": ["bird"]}},
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

    results = related.related_media(
        uuid=image.identifier,
        index=image_media_type_config.origin_index,
        filter_dead=True,
    )
    assert len(results) == 10
    assert wrapped_related_results.call_count == 1
    assert mock_related.total_matches == 1

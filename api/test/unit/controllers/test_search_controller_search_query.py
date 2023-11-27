from django.core.cache import cache

import pytest
from elasticsearch_dsl import Q

from api.controllers import search_controller
from api.controllers.search_controller import (
    DEFAULT_SQS_FLAGS,
    FILTERED_PROVIDERS_CACHE_KEY,
)


pytestmark = pytest.mark.django_db


@pytest.fixture
def excluded_providers_cache():
    excluded_provider = "excluded_provider"
    cache_value = [excluded_provider]
    cache.set(FILTERED_PROVIDERS_CACHE_KEY, cache_value, timeout=1)

    yield excluded_provider

    cache.delete(FILTERED_PROVIDERS_CACHE_KEY)


def test_create_search_query_empty(media_type_config):
    serializer = media_type_config.search_request_serializer(data={})
    serializer.is_valid(raise_exception=True)
    search_query = search_controller.build_search_query(serializer)
    actual_query_clauses = search_query.to_dict()["bool"]

    assert actual_query_clauses == {
        "must_not": [{"term": {"mature": True}}],
        "must": [{"match_all": {}}],
        "should": [
            {"rank_feature": {"boost": 10000, "field": "standardized_popularity"}}
        ],
    }


def test_create_search_query_empty_no_ranking(media_type_config, settings):
    settings.USE_RANK_FEATURES = False
    serializer = media_type_config.search_request_serializer(data={})
    serializer.is_valid(raise_exception=True)
    search_query = search_controller.build_search_query(serializer)
    actual_query_clauses = search_query.to_dict()["bool"]

    assert actual_query_clauses == {
        "must_not": [{"term": {"mature": True}}],
        "must": [{"match_all": {}}],
    }


def test_create_search_query_q_search_no_filters(media_type_config):
    serializer = media_type_config.search_request_serializer(data={"q": "cat"})
    serializer.is_valid(raise_exception=True)
    search_query = search_controller.build_search_query(serializer)
    actual_query_clauses = search_query.to_dict()["bool"]

    assert actual_query_clauses == {
        "must_not": [{"term": {"mature": True}}],
        "must": [
            {
                "simple_query_string": {
                    "default_operator": "AND",
                    "fields": ["title", "description", "tags.name"],
                    "query": "cat",
                    "flags": DEFAULT_SQS_FLAGS,
                }
            }
        ],
        "should": [
            {
                "simple_query_string": {
                    "boost": 10000,
                    "fields": ["title"],
                    "query": "cat",
                    "flags": DEFAULT_SQS_FLAGS,
                }
            },
            {"rank_feature": {"boost": 10000, "field": "standardized_popularity"}},
        ],
    }


def test_create_search_query_q_search_with_quotes_adds_exact_suffix(media_type_config):
    serializer = media_type_config.search_request_serializer(
        data={"q": '"The cutest cat"'}
    )
    serializer.is_valid(raise_exception=True)
    search_query = search_controller.build_search_query(serializer)
    actual_query_clauses = search_query.to_dict()["bool"]

    assert actual_query_clauses == {
        "must_not": [{"term": {"mature": True}}],
        "must": [
            {
                "simple_query_string": {
                    "default_operator": "AND",
                    "fields": ["title", "description", "tags.name"],
                    "query": '"The cutest cat"',
                    "quote_field_suffix": ".raw",
                    "flags": DEFAULT_SQS_FLAGS,
                }
            }
        ],
        "should": [
            {
                "simple_query_string": {
                    "boost": 10000,
                    "fields": ["title"],
                    "query": "The cutest cat",
                    "flags": DEFAULT_SQS_FLAGS,
                }
            },
            {"rank_feature": {"boost": 10000, "field": "standardized_popularity"}},
        ],
    }


def test_create_search_query_q_search_with_filters(image_media_type_config):
    serializer = image_media_type_config.search_request_serializer(
        data={
            "q": "cat",
            "license": "by-nc",
            "aspect_ratio": "wide",
            # this is a deprecated param, and it doesn't work because it doesn't exist in the serializer
            "categories": "digitized_artwork",
            "category": "illustration",
            "excluded_source": "flickr",
            "unstable__authority": True,
            "unstable__authority_boost": "2.5",
            "unstable__include_sensitive_results": True,
        }
    )
    serializer.is_valid(raise_exception=True)
    search_query = search_controller.build_search_query(serializer)
    actual_query_clauses = search_query.to_dict()["bool"]

    assert actual_query_clauses == {
        "filter": [
            {"terms": {"category": ["illustration"]}},
            {"terms": {"license": ["by-nc"]}},
            {"terms": {"aspect_ratio": ["wide"]}},
        ],
        "must_not": [{"terms": {"source": ["flickr"]}}],
        "must": [
            {
                "simple_query_string": {
                    "default_operator": "AND",
                    "fields": ["title", "description", "tags.name"],
                    "query": "cat",
                    "flags": DEFAULT_SQS_FLAGS,
                }
            }
        ],
        "should": [
            {
                "simple_query_string": {
                    "boost": 10000,
                    "fields": ["title"],
                    "query": "cat",
                    "flags": DEFAULT_SQS_FLAGS,
                }
            },
            {"rank_feature": {"boost": 10000, "field": "standardized_popularity"}},
            {"rank_feature": {"boost": 25000, "field": "authority_boost"}},
        ],
    }


def test_create_search_query_non_q_query(image_media_type_config):
    serializer = image_media_type_config.search_request_serializer(
        data={
            "creator": "Artist From Openverse",
            "title": "kitten🐱",
            "tags": "cute",
        }
    )
    serializer.is_valid(raise_exception=True)
    search_query = search_controller.build_search_query(serializer)
    actual_query_clauses = search_query.to_dict()["bool"]

    assert actual_query_clauses == {
        "must_not": [{"term": {"mature": True}}],
        "must": [
            {
                "simple_query_string": {
                    "fields": ["creator"],
                    "query": "Artist From Openverse",
                    "flags": DEFAULT_SQS_FLAGS,
                }
            },
            {
                "simple_query_string": {
                    "fields": ["title"],
                    "query": "kitten🐱",
                    "flags": DEFAULT_SQS_FLAGS,
                }
            },
            {
                "simple_query_string": {
                    "fields": ["tags.name"],
                    "query": "cute",
                    "flags": DEFAULT_SQS_FLAGS,
                }
            },
        ],
        "should": [
            {"rank_feature": {"boost": 10000, "field": "standardized_popularity"}},
        ],
    }


def test_create_search_query_q_search_license_license_type_creates_2_terms_filters(
    image_media_type_config,
):
    serializer = image_media_type_config.search_request_serializer(
        data={
            "license": "by-nc",
            "license_type": "commercial",
        }
    )
    serializer.is_valid(raise_exception=True)
    search_query = search_controller.build_search_query(serializer)
    actual_query_clauses = search_query.to_dict()["bool"]

    first_license_terms_filter = actual_query_clauses["filter"][0]
    second_license_terms_filter_licenses = sorted(
        actual_query_clauses["filter"][1]["terms"]["license"]
    )
    # Extracting these to make comparisons not dependent on list order.
    assert first_license_terms_filter == {"terms": {"license": ["by-nc"]}}
    assert second_license_terms_filter_licenses == [
        "by",
        "by-nd",
        "by-sa",
        "cc0",
        "pdm",
        "sampling+",
    ]
    actual_query_clauses.pop("filter", None)

    assert actual_query_clauses == {
        "must_not": [{"term": {"mature": True}}],
        "must": [{"match_all": {}}],
        "should": [
            {"rank_feature": {"boost": 10000, "field": "standardized_popularity"}},
        ],
    }


def test_create_search_query_empty_with_dynamically_excluded_providers(
    image_media_type_config,
    excluded_providers_cache,
):
    serializer = image_media_type_config.search_request_serializer(data={})
    serializer.is_valid(raise_exception=True)

    search_query = search_controller.build_search_query(serializer)

    actual_query_clauses = search_query.to_dict()["bool"]
    assert actual_query_clauses == {
        "must_not": [
            {"term": {"mature": True}},
            {"terms": {"provider": [excluded_providers_cache]}},
        ],
        "must": [{"match_all": {}}],
        "should": [
            {"rank_feature": {"boost": 10000, "field": "standardized_popularity"}}
        ],
    }


@pytest.mark.parametrize(
    ("data", "expected_query_filter"),
    [
        pytest.param(
            {"tag": "art"},
            [{"term": {"tags.name.keyword": "art"}}],
            id="filter_by_tag",
        ),
        pytest.param(
            {"tag": "art, photography"},
            [{"term": {"tags.name.keyword": "art, photography"}}],
            id="filter_by_tag_treats_punctuation_as_part_of_tag",
        ),
        pytest.param(
            {"source": "flickr"},
            [{"term": {"source": "flickr"}}],
            id="filter_by_source",
        ),
        pytest.param(
            {"source": "flickr", "creator": "nasa"},
            [
                {"term": {"source": "flickr"}},
                {"term": {"creator.keyword": "nasa"}},
            ],
            id="filter_by_creator",
        ),
    ],
)
def test_build_collection_query(image_media_type_config, data, expected_query_filter):
    serializer = image_media_type_config.search_request_serializer(data={})
    serializer.is_valid(raise_exception=True)
    actual_query = search_controller.build_collection_query(serializer, data)
    expected_query = Q(
        "bool",
        filter=expected_query_filter,
        must_not=[{"term": {"mature": True}}],
    )

    assert actual_query == expected_query

from django.core.cache import cache

import pytest

from api.controllers import search_controller


pytestmark = pytest.mark.django_db


@pytest.fixture
def excluded_providers_cache():
    cache_key = "filtered_providers"
    excluded_provider = "excluded_provider"
    cache_value = [{"provider_identifier": excluded_provider}]
    cache.set(cache_key, cache_value, timeout=1)

    yield excluded_provider

    cache.delete(cache_key)


def test_create_search_query_empty(media_type_config):
    serializer = media_type_config.search_request_serializer(data={})
    serializer.is_valid(raise_exception=True)
    search_query = search_controller.create_search_query(serializer)
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
    search_query = search_controller.create_search_query(serializer)
    actual_query_clauses = search_query.to_dict()["bool"]

    assert actual_query_clauses == {
        "must_not": [{"term": {"mature": True}}],
        "must": [{"match_all": {}}],
    }


def test_create_search_query_q_search_no_filters(media_type_config):
    serializer = media_type_config.search_request_serializer(data={"q": "cat"})
    serializer.is_valid(raise_exception=True)
    search_query = search_controller.create_search_query(serializer)
    actual_query_clauses = search_query.to_dict()["bool"]

    assert actual_query_clauses == {
        "must_not": [{"term": {"mature": True}}],
        "must": [
            {
                "simple_query_string": {
                    "default_operator": "AND",
                    "fields": ["title", "description", "tags.name"],
                    "query": "cat",
                }
            }
        ],
        "should": [
            {
                "simple_query_string": {
                    "boost": 10000,
                    "fields": ["title"],
                    "query": "cat",
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
    search_query = search_controller.create_search_query(serializer)
    actual_query_clauses = search_query.to_dict()["bool"]

    assert actual_query_clauses == {
        "must_not": [{"term": {"mature": True}}],
        "must": [
            {
                "simple_query_string": {
                    "default_operator": "AND",
                    "fields": ["title", "description", "tags.name"],
                    "query": '"The cutest cat"',
                    "quote_field_suffix": ".exact",
                }
            }
        ],
        "should": [
            {
                "simple_query_string": {
                    "boost": 10000,
                    "fields": ["title"],
                    "query": "The cutest cat",
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
    search_query = search_controller.create_search_query(serializer)
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
                }
            }
        ],
        "should": [
            {
                "simple_query_string": {
                    "boost": 10000,
                    "fields": ["title"],
                    "query": "cat",
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
    search_query = search_controller.create_search_query(serializer)
    actual_query_clauses = search_query.to_dict()["bool"]

    assert actual_query_clauses == {
        "must_not": [{"term": {"mature": True}}],
        "must": [
            {
                "simple_query_string": {
                    "fields": ["creator"],
                    "query": "Artist From Openverse",
                }
            },
            {"simple_query_string": {"fields": ["title"], "query": "kitten🐱"}},
            {"simple_query_string": {"fields": ["tags.name"], "query": "cute"}},
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
    search_query = search_controller.create_search_query(serializer)
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

    search_query = search_controller.create_search_query(serializer)

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

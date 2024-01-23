from elasticsearch_cluster.create_new_es_index.create_new_es_index import (
    merge_index_configurations,
)


def test_merge_index_configurations():
    """Test merge_index_configurations with realistic data."""
    current_index_config = {
        "aliases": {"audio": {}},
        "mappings": {
            "dynamic": "false",
            "properties": {"authority_boost": {"type": "rank_feature"}},
        },
        "settings": {
            "index": {
                "routing": {
                    "allocation": {"include": {"_tier_preference": "data_content"}}
                },
                "refresh_interval": "-1",
                "number_of_shards": "1",
                "provided_name": "audio-init",
                "creation_date": "1704314839358",
                "analysis": {
                    "filter": {
                        "stem_overrides": {
                            "type": "stemmer_override",
                            "rules": ["animals => animal", "animal => animal"],
                        },
                    },
                    "analyzer": {"tokenizer": "standard"},
                },
                "number_of_replicas": "1",
                "uuid": "fHs6A-7oSpOmutQLgWA0sw",
                "version": {"created": "8080299"},
            }
        },
    }

    # New index config contains changes to some keys, including nested keys.
    new_index_config = {
        "settings": {
            "index": {
                "routing": {"allocation": {"include": {"_tier_preference": "foo"}}},
                "refresh_interval": "9999",
                "number_of_shards": "9999",
                "analysis": {
                    "filter": {
                        "stem_overrides": {
                            "type": "stemmer_override",
                            "rules": [
                                "foo => bar",
                            ],
                        },
                    }
                },
            }
        }
    }

    # Aliases and excluded settings dropped, changes merged.
    expected_merged_config = {
        "mappings": {
            "dynamic": "false",
            "properties": {"authority_boost": {"type": "rank_feature"}},
        },
        "settings": {
            "index": {
                "routing": {"allocation": {"include": {"_tier_preference": "foo"}}},
                "refresh_interval": "9999",
                "number_of_shards": "9999",
                "analysis": {
                    "filter": {
                        "stem_overrides": {
                            "type": "stemmer_override",
                            "rules": [
                                "foo => bar",
                            ],
                        },
                    },
                    "analyzer": {"tokenizer": "standard"},
                },
                "number_of_replicas": "1",
            }
        },
    }
    actual_merged_config = merge_index_configurations.function(
        new_index_config, current_index_config
    )
    assert actual_merged_config == expected_merged_config

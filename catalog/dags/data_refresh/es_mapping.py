from common.constants import AUDIO, IMAGE, MediaType


def index_settings(media_type: MediaType):
    """
    Return the Elasticsearch mapping for a given table in the database.

    :param media_type: The name of the table in the upstream database.
    :return: the settings for the ES mapping
    """

    number_of_shards: dict[MediaType, int] = {
        IMAGE: 18,
        AUDIO: 1,
    }

    settings = {
        "index": {
            "number_of_shards": number_of_shards[media_type],
            "number_of_replicas": 0,
            "refresh_interval": "-1",
        },
        "analysis": {
            "filter": {
                "stem_overrides": {
                    "type": "stemmer_override",
                    "rules": [
                        # Override unwanted 'anim' stems
                        "animals => animal",
                        "animal => animal",
                        "anime => anime",
                        "animate => animate",
                        "animated => animate",
                        # Override "universe" to prevent matching to
                        # "university" or "universal".
                        "universe => universe",
                    ],
                },
                "english_stop": {"type": "stop", "stopwords": "_english_"},
                "english_stemmer": {"type": "stemmer", "language": "english"},
                "english_possessive_stemmer": {
                    "type": "stemmer",
                    "language": "possessive_english",
                },
            },
            "analyzer": {
                "custom_english": {
                    "tokenizer": "standard",
                    "filter": [
                        # Stem overrides must appear before the primary
                        # language stemmer.
                        "stem_overrides",
                        "english_possessive_stemmer",
                        "lowercase",
                        "english_stop",
                        "english_stemmer",
                    ],
                }
            },
        },
    }
    common_mappings = {
        "dynamic": False,  # extra fields are stored in ``_source`` but not indexed
        "properties": {
            "id": {"type": "long"},
            "created_on": {"type": "date"},
            "mature": {"type": "boolean"},
            # Keyword fields
            "identifier": {"type": "keyword"},
            "extension": {"type": "keyword"},
            "license": {"type": "keyword"},
            "provider": {"type": "keyword"},
            "source": {"type": "keyword"},
            "filetype": {"type": "keyword"},
            "category": {"type": "keyword"},
            # Text-based fields
            "title": {
                "type": "text",
                "analyzer": "custom_english",
                "similarity": "boolean",
                "fields": {
                    "keyword": {"type": "keyword", "ignore_above": 256},
                    "raw": {"type": "text", "index": True},
                },
            },
            "description": {
                "type": "text",
                "analyzer": "custom_english",
                "similarity": "boolean",
                "fields": {"raw": {"type": "text", "index": True}},
            },
            "creator": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            # Rank feature fields
            "standardized_popularity": {"type": "rank_feature"},
            "authority_boost": {"type": "rank_feature"},
            "authority_penalty": {
                "type": "rank_feature",
                "positive_score_impact": False,
            },
            "max_boost": {"type": "rank_feature"},
            "min_boost": {"type": "rank_feature"},
            # Nested fields
            "tags": {
                "properties": {
                    "accuracy": {"type": "float"},
                    # Text-based fields
                    "name": {
                        "type": "text",
                        "analyzer": "custom_english",
                        "fields": {
                            "keyword": {"type": "keyword", "ignore_above": 256},
                            "raw": {"type": "text", "index": True},
                        },
                    },
                }
            },
        },
    }
    media_properties = {
        "image": {
            # Keyword fields
            "aspect_ratio": {"type": "keyword"},
            "size": {"type": "keyword"},
        },
        "audio": {
            # Keyword fields
            "length": {"type": "keyword"},
        },
    }
    media_mappings = common_mappings.copy()
    media_mappings["properties"].update(media_properties[media_type])
    result = {"settings": settings.copy(), "mappings": media_mappings}
    return result

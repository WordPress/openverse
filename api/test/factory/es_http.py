from uuid import uuid4


MOCK_LIVE_RESULT_URL_PREFIX = "https://example.com/openverse-live-image-result-url"
MOCK_DEAD_RESULT_URL_PREFIX = "https://example.com/openverse-dead-image-result-url"


def create_mock_es_http_image_hit(
    _id: str, index: str, live: bool = True, identifier: str | None = None
):
    return {
        "_index": index,
        "_type": "_doc",
        "_id": _id,
        "_score": 7.607353,
        "_source": {
            "thumbnail": None,
            "aspect_ratio": "wide",
            "extension": "jpg",
            "size": "large",
            "authority_boost": 85,
            "max_boost": 85,
            "min_boost": 1,
            "id": _id,
            "identifier": identifier or str(uuid4()),
            "title": "Bird Nature Photo",
            "foreign_landing_url": "https://example.com/photo/LYTN21EBYO",
            "creator": "Nature's Beauty",
            "creator_url": "https://example.com/author/121424",
            "url": f"{MOCK_LIVE_RESULT_URL_PREFIX}/{_id}"
            if live
            else f"{MOCK_DEAD_RESULT_URL_PREFIX}/{_id}",
            "license": "cc0",
            "license_version": "1.0",
            "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
            "provider": "example",
            "source": "example",
            "category": "photograph",
            "created_on": "2022-02-26T08:48:33+00:00",
            "tags": [{"name": "bird"}],
            "mature": False,
        },
    }


def create_mock_es_http_image_search_response(
    index: str,
    total_hits: int,
    hit_count: int,
    live_hit_count: int | None = None,
    base_hits=None,
):
    live_hit_count = live_hit_count if live_hit_count is not None else hit_count
    base_hits = base_hits or []

    live_hits = [
        create_mock_es_http_image_hit(
            _id=len(base_hits) + i,
            index=index,
            live=True,
        )
        for i in range(live_hit_count)
    ]

    dead_hits = [
        create_mock_es_http_image_hit(
            _id=len(live_hits) + len(base_hits) + i,
            index=index,
            live=False,
        )
        for i in range(hit_count - live_hit_count)
    ]

    return {
        "took": 3,
        "timed_out": False,
        "_shards": {"total": 18, "successful": 18, "skipped": 0, "failed": 0},
        "hits": {
            "total": {"value": total_hits, "relation": "eq"},
            "max_score": 11.0007305,
            "hits": base_hits + live_hits + dead_hits,
        },
    }


def create_mock_es_http_image_response_with_identifier(
    index: str,
    identifier: str,
):
    return {
        "took": 3,
        "timed_out": False,
        "_shards": {"total": 18, "successful": 18, "skipped": 0, "failed": 0},
        "hits": {
            "total": {"value": 1, "relation": "eq"},
            "max_score": 11.0007305,
            "hits": [
                create_mock_es_http_image_hit(
                    _id="1",
                    index=index,
                    live=True,
                    identifier=identifier,
                )
            ],
        },
    }

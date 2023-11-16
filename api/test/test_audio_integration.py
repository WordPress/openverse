"""
End-to-end API tests for audio.

Can be used to verify a live deployment is functioning as designed.
Run with the `pytest -s` command from this directory.
"""

import json
from test.constants import API_URL
from test.media_integration import (
    creator_collection,
    detail,
    license_filter_case_insensitivity,
    related,
    report,
    search,
    search_all_excluded,
    search_by_category,
    search_consistency,
    search_quotes,
    search_quotes_exact,
    search_source_and_excluded,
    search_special_chars,
    sensitive_search_and_detail,
    source_collection,
    stats,
    tag_collection,
    uuid_validation,
)

import pytest
import requests
from django_redis import get_redis_connection

from api.utils.check_dead_links import CACHE_PREFIX


@pytest.fixture
def force_result_validity():
    statuses = {}

    def force_validity(query_response):
        nonlocal statuses
        new_statuses = {
            f"{CACHE_PREFIX}{item['url']}": 200 for item in query_response["results"]
        }
        statuses |= new_statuses
        with get_redis_connection() as redis:
            redis.mset(new_statuses)

    yield force_validity

    with get_redis_connection() as redis:
        redis.delete(*list(statuses.keys()))


@pytest.fixture
def audio_fixture(force_result_validity):
    res = requests.get(f"{API_URL}/v1/audio/", verify=False)
    parsed = res.json()
    force_result_validity(parsed)
    assert res.status_code == 200
    return parsed


@pytest.fixture
def jamendo_audio_fixture(force_result_validity):
    """
    Get an audio object specifically from the Jamendo provider.

    Thumbnail tests must use Jamendo results because the Wikimedia
    sample audio results do not have thumbnails.
    """
    res = requests.get(
        f"{API_URL}/v1/audio/",
        data={"source": "jamendo"},
        verify=False,
    )
    parsed = res.json()
    force_result_validity(parsed)
    assert res.status_code == 200
    return parsed


def test_search(audio_fixture):
    search(audio_fixture)


def test_search_category_filtering(audio_fixture):
    search_by_category("audio", "music", audio_fixture)
    search_by_category("audio", "pronunciation", audio_fixture)


def test_search_category_filtering_fails(audio_fixture):
    with pytest.raises(AssertionError):
        search_by_category("audio", "not_valid", audio_fixture)


def test_search_all_excluded():
    search_all_excluded("audio", ["freesound", "jamendo", "wikimedia_audio"])


def test_search_source_and_excluded():
    search_source_and_excluded("audio")


def test_search_quotes():
    search_quotes("audio", "love")


def test_search_quotes_exact():
    # ``field recording`` returns different results when quoted vs unquoted
    search_quotes_exact("audio", "field recording")


def test_search_with_special_characters():
    search_special_chars("audio", "love")


def test_search_consistency():
    n_pages = 5
    search_consistency("audio", n_pages)


def test_audio_detail(audio_fixture):
    detail("audio", audio_fixture)


def test_audio_stats():
    stats("audio")


def test_audio_detail_without_thumb():
    resp = requests.get(f"{API_URL}/v1/audio/44540200-91eb-483d-9e99-38ce86a52fb6")
    assert resp.status_code == 200
    parsed = json.loads(resp.text)
    assert parsed["thumbnail"] is None


def test_audio_search_without_thumb():
    """The first audio of this search should not have a thumbnail."""
    resp = requests.get(f"{API_URL}/v1/audio/?q=zaus")
    assert resp.status_code == 200
    parsed = json.loads(resp.text)
    assert parsed["results"][0]["thumbnail"] is None


def test_audio_report(audio_fixture):
    report("audio", audio_fixture)


def test_audio_license_filter_case_insensitivity():
    license_filter_case_insensitivity("audio")


def test_audio_uuid_validation():
    uuid_validation("audio", "123456789123456789123456789123456789")
    uuid_validation("audio", "12345678-1234-5678-1234-1234567891234")
    uuid_validation("audio", "abcd")


def test_audio_related(audio_fixture):
    related(audio_fixture)


def test_audio_tag_collection():
    tag_collection("audio")


def test_audio_source_collection():
    source_collection("audio")


def test_audio_creator_collection():
    creator_collection("audio")


def test_audio_sensitive_search_and_detail():
    sensitive_search_and_detail("audio")

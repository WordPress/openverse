"""
End-to-end API tests for audio. Can be used to verify a live deployment is
functioning as designed. Run with the `pytest -s` command from this directory.
"""

import json
from test.constants import API_URL
from test.media_integration import (
    detail,
    license_filter_case_insensitivity,
    report,
    search,
    search_all_excluded,
    search_by_category,
    search_consistency,
    search_quotes,
    search_source_and_excluded,
    search_special_chars,
    stats,
    thumb,
    thumb_compression,
    thumb_full_size,
    thumb_webp,
)

import pytest
import requests


@pytest.fixture
def audio_fixture():
    res = requests.get(f"{API_URL}/v1/audio?q=", verify=False)
    assert res.status_code == 200
    parsed = json.loads(res.text)
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


def test_search_with_special_characters():
    search_special_chars("audio", "love")


def test_search_consistency():
    n_pages = 5
    search_consistency("audio", n_pages)


def test_audio_detail(audio_fixture):
    detail("audio", audio_fixture)


def test_audio_stats():
    stats("audio")


def test_audio_thumb(audio_fixture):
    thumb(audio_fixture)


def test_audio_detail_without_thumb():
    resp = requests.get(f"{API_URL}/v1/audio/44540200-91eb-483d-9e99-38ce86a52fb6")
    assert resp.status_code == 200
    parsed = json.loads(resp.text)
    assert parsed["thumbnail"] is None


def test_audio_search_without_thumb():
    """The first audio of this search should not have a thumbnail."""
    resp = requests.get(f"{API_URL}/v1/audio/?q=zaus&filter_dead=false")
    assert resp.status_code == 200
    parsed = json.loads(resp.text)
    assert parsed["results"][0]["thumbnail"] is None


def test_audio_thumb_compression(audio_fixture):
    thumb_compression(audio_fixture)


def test_audio_thumb_webp(audio_fixture):
    thumb_webp(audio_fixture)


def test_audio_thumb_full_size(audio_fixture):
    thumb_full_size(audio_fixture)


def test_audio_report(audio_fixture):
    report("audio", audio_fixture)


def test_audio_license_filter_case_insensitivity():
    license_filter_case_insensitivity("audio")

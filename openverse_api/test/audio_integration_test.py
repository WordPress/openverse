"""
End-to-end API tests for audio. Can be used to verify a live deployment is
functioning as designed. Run with the `pytest -s` command from this directory.
"""

import json
from test.constants import API_URL
from test.media_integration import (
    detail,
    report,
    search,
    search_consistency,
    search_quotes,
    search_special_chars,
    stats,
    thumb,
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


def test_audio_report(audio_fixture):
    report("audio", audio_fixture)

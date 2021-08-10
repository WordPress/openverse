"""
End-to-end API tests for audio. Can be used to verify a live deployment is
functioning as designed. Run with the `pytest -s` command from this directory.
"""

import json

import pytest
import requests

from test.constants import API_URL
from test.media_integration import (
    search,
    search_quotes,
    search_special_chars,
    search_consistency,
    detail,
)


@pytest.fixture
def audio_fixture():
    res = requests.get(f'{API_URL}/v1/audio?q=', verify=False)
    assert res.status_code == 200
    parsed = json.loads(res.text)
    return parsed


def test_search(audio_fixture):
    search(audio_fixture)


def test_search_quotes():
    search_quotes('audio', 'love')


def test_search_with_special_characters():
    search_special_chars('audio', 'love')


def test_search_consistency():
    n_pages = 5
    search_consistency('audio', n_pages)


def test_audio_detail(audio_fixture):
    detail('audio', audio_fixture)


def test_audio_stats():
    pass
    response = requests.get(f'{API_URL}/v1/audio/stats', verify=False)
    parsed_response = json.loads(response.text)
    assert response.status_code == 200
    num_audio = 0
    provider_count = 0
    for pair in parsed_response:
        audio_count = pair['audio_count']
        num_audio += int(audio_count)
        provider_count += 1
    assert num_audio > 0
    assert provider_count > 0

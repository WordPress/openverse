"""
End-to-end API tests for audio. Can be used to verify a live deployment is
functioning as designed. Run with the `pytest -s` command from this directory.
"""

import json

import pytest
import requests

from test.constants import API_URL

@pytest.fixture
def audio_fixture():
    res = requests.get(f'{API_URL}/v1/audio?q=', verify=False)
    assert res.status_code == 200
    parsed = json.loads(res.text)
    return parsed


def test_search(audio_fixture):
    assert audio_fixture['result_count'] > 0


def test_audio_detail(audio_fixture):
    test_id = audio_fixture['results'][0]['id']
    response = requests.get(f'{API_URL}/v1/audio/{test_id}', verify=False)
    assert response.status_code == 200

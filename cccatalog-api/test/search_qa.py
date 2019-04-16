import requests
import json
from .api_live_integration_test import API_URL

"""
Perform some basic tests to ensure that search rankings work as anticipated.
"""


def test_phrase_relevance():
    res = requests.get(API_URL + "/search?q=home office")
    parsed = json.loads(res.text)
    assert parsed[0]['id'] == 1
import requests
from .api_live_integration_test import API_URL


def test_phrase_relevance():
    res = requests.get(API_URL + "/search?q=home office")
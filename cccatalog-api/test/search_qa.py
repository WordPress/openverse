import requests
import json
from enum import Enum
from .api_live_integration_test import API_URL

"""
Perform some basic tests to ensure that search rankings work as anticipated.
"""

class TaskTypes(Enum):
    TARGET = 1
    LESS_RELEVANT = 2
    NOT_RELEVANT = 3


def test_phrase_relevance():
    res = requests.get(API_URL + "/search?q=home office&filter_dead=False")
    parsed = json.loads(res.text)
    assert parsed[0]['id'] == TaskTypes.Target.value
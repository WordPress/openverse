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
    res = requests.get(
        "{}/image/search?q=home%20office&filter_dead=false&qa=true"
        .format(API_URL)
    )
    parsed = json.loads(res.text)
    assert parsed[0]['id'] == TaskTypes.Target.value
    assert parsed[1]['id'] < TaskTypes.NOT_RELEVANT.value
    assert parsed[-1]['id'] != TaskTypes.NOT_RELEVANT.value

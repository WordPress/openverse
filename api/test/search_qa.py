"""
Perform some basic tests to ensure that search rankings work as anticipated.
"""

import json
import pprint
from enum import Enum

import pytest
import requests

from .api_live_integration import API_URL


class QAScores(Enum):
    TARGET = 1
    LESS_RELEVANT = 2
    NOT_RELEVANT = 3


@pytest.mark.skip(reason="This test is nondeterministic")
def test_phrase_relevance():
    res = requests.get(f"{API_URL}/image/search?q=home office&qa=true")
    parsed = json.loads(res.text)
    pprint.pprint(parsed)
    assert int(parsed["results"][0]["id"]) == QAScores.TARGET.value
    assert int(parsed["results"][1]["id"]) < QAScores.NOT_RELEVANT.value
    assert int(parsed["results"][-1]["id"]) != QAScores.NOT_RELEVANT.value

import json
import requests

"""
Tests to run against a live instance of Openverse with a significant (10M+)
number of records. Quality of search rankings can be affected by the number of
documents in the search index, so toy examples with five or six documents
do not accurately model relevance at scale.
"""

API_URL = 'https://dev.api.openverse.engineering'


def _phrase_in_tags(tags, term):
    for tag in tags:
        if 'name' in tag:
            if tag['name'] == term:
                return True
    return False


def _phrase_in_title(title, term):
    return term in title


def test_phrase_relevance():
    """
    If I search for "home office", the top results ought to have the phrase
    'home office' in the tags or title.
    """
    search_term = 'home office'
    response = requests.get(
        API_URL + '/image/search?q={}'.format(search_term),
        verify=False
    )
    assert response.status_code == 200
    parsed = json.loads(response.text)
    first_result = parsed['results'][0]
    assert (
            _phrase_in_tags(first_result['tags'], search_term) or
            _phrase_in_title(first_result['title'], search_term)
    )

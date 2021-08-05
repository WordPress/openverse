"""
End-to-end API tests for audio. Can be used to verify a live deployment is
functioning as designed. Run with the `pytest -s` command from this directory.
"""

import json

import requests

from test.constants import API_URL


def search(fixture):
    """Returns results for test query."""
    assert fixture['result_count'] > 0


def search_quotes(media_path, q='test'):
    """Returns a response when quote matching is messed up."""
    response = requests.get(f'{API_URL}/v1/{media_path}?q="{q}', verify=False)
    assert response.status_code == 200


def search_special_chars(media_path, q='test'):
    """Returns a response when query includes special characters."""
    response = requests.get(f'{API_URL}/v1/{media_path}?q={q}!', verify=False)
    assert response.status_code == 200


def search_consistency(media_path, n_pages, ):
    """
    Returns consistent, non-duplicate results in the first n pages.

    Elasticsearch sometimes reaches an inconsistent state, which causes search
    results to appear differently upon page refresh. This can also introduce
    image duplicates in subsequent pages. This test ensures that no duplicates
    appear in the first few pages of a search query.
    """

    searches = set(
        requests.get(
            f'{API_URL}/v1/{media_path}?page={page}',
            verify=False
        )
        for page in range(1, n_pages)
    )

    results = set()
    for response in searches:
        parsed = json.loads(response.text)
        for result in parsed['results']:
            media_id = result['id']
            assert media_id not in results
            results.add(media_id)


def detail(media_type, fixture):
    test_id = fixture['results'][0]['id']
    response = requests.get(f'{API_URL}/v1/{media_type}/{test_id}', verify=False)
    assert response.status_code == 200

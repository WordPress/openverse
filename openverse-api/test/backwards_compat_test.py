"""
This file ensures that deprecated URLs are redirected to their updated paths and
not left to rot.

Can be used to verify a live deployment is functioning as designed.
Run with the `pytest -s` command from this directory.
"""

import requests

from test.constants import API_URL


def test_old_stats_endpoint():
    response = requests.get(
        f'{API_URL}/v1/sources?type=images',
        allow_redirects=False,
        verify=False
    )
    assert response.status_code == 301
    assert response.is_permanent_redirect
    assert response.headers.get('Location') == '/v1/images/stats'


def test_old_related_images_endpoint():
    response = requests.get(
        f'{API_URL}/v1/recommendations/images/xyz',
        allow_redirects=False,
        verify=False
    )
    assert response.status_code == 301
    assert response.is_permanent_redirect
    assert response.headers.get('Location') == '/v1/images/xyz/recommendations'


def test_old_oembed_endpoint():
    response = requests.get(
        f'{API_URL}/v1/oembed?key=value',
        allow_redirects=False,
        verify=False
    )
    assert response.status_code == 301
    assert response.is_permanent_redirect
    assert response.headers.get('Location') == '/v1/images/oembed?key=value'


def test_old_thumbs_endpoint():
    response = requests.get(
        f'{API_URL}/v1/thumbs/xyz',
        allow_redirects=False,
        verify=False
    )
    assert response.status_code == 301
    assert response.is_permanent_redirect
    assert response.headers.get('Location') == '/v1/images/xyz/thumb'
import requests
import json
import pytest

API_URL = 'http://localhost:8000'


@pytest.fixture
def search_fixture():
    response = requests.get(API_URL + '/image/search?q=a')
    assert response.status_code == 200
    return json.loads(response.text)


def test_search(search_fixture):
    assert search_fixture['result_count'] > 10


def test_image_detail(search_fixture):
    test_id = search_fixture['results'][0]['id']
    response = requests.get(API_URL + '/image/{}'.format(test_id))
    assert response.status_code == 200


@pytest.fixture
def link_shortener_fixture(search_fixture):
    link_to_shorten = search_fixture['results'][0]['detail']
    payload = {"full_url": link_to_shorten}
    response = requests.post(API_URL + '/link', json=payload)
    assert response.status_code == 200
    return json.loads(response.text)


def test_link_shortener_create(link_shortener_fixture):
    assert 'shortened_url' in link_shortener_fixture


def test_link_shortener_resolve(link_shortener_fixture):
    path = link_shortener_fixture['shortened_url'].split('/')[-1]
    response = requests.get(API_URL + '/link/' + path, allow_redirects=False)
    assert response.status_code == 301

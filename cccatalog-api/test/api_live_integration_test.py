import requests
import json
import pytest
import os
from cccatalog.api.licenses import LICENSE_GROUPS

"""
End-to-end API tests. Can be used to verify a live deployment is functioning as
designed. Run with the `pytest -s` command from this directory.
"""


API_URL = os.getenv('INTEGRATION_TEST_URL', 'https://localhost:8000')
known_apis = {
    'http://localhost:8000': 'LOCAL',
    'https://api.creativecommons.engineering': 'PRODUCTION',
    'https://api-dev.creativecommons.engineering': 'TESTING'
}


def setup_module():
    if API_URL in known_apis:
        print(
            '\n\033[1;31;40mTesting {} environment'.format(known_apis[API_URL])
        )


@pytest.fixture
def search_fixture():
    response = requests.get(API_URL + '/image/search?q=a',
                            verify=False)
    assert response.status_code == 200
    parsed = json.loads(response.text)
    return parsed


def test_search(search_fixture):
    assert search_fixture['result_count'] > 0


def test_search_consistency():
    """
    Elasticsearch sometimes reaches an inconsistent state, which causes search
    results to appear differently upon page refresh. This can also introduce
    image duplicates in subsequent pages. This test ensures that no duplicates
    appear in the first few pages of a search query.
    """
    n_pages = 5
    searches = set(
        requests.get(API_URL + '/image/search?q=a;page={}'.format(page),
                     verify=False)
        for page in range(1, n_pages)
    )

    images = set()
    for response in searches:
        parsed = json.loads(response.text)
        for result in parsed['results']:
            image_id = result['id']
            assert image_id not in images
            images.add(image_id)


def test_image_detail(search_fixture):
    test_id = search_fixture['results'][0]['id']
    response = requests.get(API_URL + '/image/{}'.format(test_id), verify=False)
    assert response.status_code == 200


@pytest.fixture
def link_shortener_fixture(search_fixture):
    link_to_shorten = search_fixture['results'][0]['detail']
    payload = {"full_url": link_to_shorten}
    response = requests.post(API_URL + '/link', json=payload, verify=False)
    assert response.status_code == 200
    return json.loads(response.text)


def test_link_shortener_create(link_shortener_fixture):
    assert 'shortened_url' in link_shortener_fixture


def test_link_shortener_resolve(link_shortener_fixture):
    path = link_shortener_fixture['shortened_url'].split('/')[-1]
    response = requests.get(API_URL + '/link/' + path, allow_redirects=False,
                            verify=False)
    assert response.status_code == 301


def test_stats():
    response = requests.get(API_URL + '/statistics/image', verify=False)
    parsed_response = json.loads(response.text)
    assert response.status_code == 200
    num_images = 0
    provider_count = 0
    for pair in parsed_response:
        image_count = pair['image_count']
        num_images += int(image_count)
        provider_count += 1
    assert num_images > 0
    assert provider_count > 0


@pytest.fixture
def test_list_create(search_fixture):
    payload = {
        'title': 'INTEGRATION TEST',
        'images': [search_fixture['results'][0]['id']]
    }
    response = requests.post(API_URL + '/list', json=payload, verify=False)
    parsed_response = json.loads(response.text)
    assert response.status_code == 201
    return parsed_response


def test_list_detail(test_list_create):
    list_slug = test_list_create['url'].split('/')[-1]
    response = requests.get(
        API_URL + '/list/{}'.format(list_slug), verify=False
    )
    assert response.status_code == 200


def test_list_delete(test_list_create):
    list_slug = test_list_create['url'].split('/')[-1]
    token = test_list_create['auth']
    headers = {"Authorization": "Token {}".format(token)}
    response = requests.delete(
        API_URL + '/list/{}'.format(list_slug),
        headers=headers,
        verify=False
    )
    assert response.status_code == 204


def test_license_type_filtering():
    """
    Ensure that multiple license type filters interact together correctly.
    """
    commercial = LICENSE_GROUPS['commercial']
    modification = LICENSE_GROUPS['modification']
    commercial_and_modification = set.intersection(modification, commercial)
    response = requests.get(
        API_URL + '/image/search?q=a&lt=commercial,modification', verify=False
    )
    parsed = json.loads(response.text)
    for result in parsed['results']:
        assert result['license'].upper() in commercial_and_modification


def test_single_license_type_filtering():
    commercial = LICENSE_GROUPS['commercial']
    response = requests.get(
        API_URL + '/image/search?q=a&lt=commercial', verify=False
    )
    parsed = json.loads(response.text)
    for result in parsed['results']:
        assert result['license'].upper() in commercial


def test_specific_license_filter():
    response = requests.get(API_URL + '/image/search?q=a&li=by', verify=False)
    parsed = json.loads(response.text)
    for result in parsed['results']:
        assert result['license'] == 'by'


def test_creator_quotation_grouping():
    """
    Users should be able to group terms together with quotation marks to narrow
    down their searches more effectively.
    :return:
    """
    no_quotes = json.loads(
        requests.get(
            API_URL + '/image/search?creator=claude%20monet',
            verify=False
        ).text
    )
    quotes = json.loads(
        requests.get(
            API_URL + '/image/search?creator="claude%20monet"',
            verify=False
        ).text
    )
    # Did quotation marks actually narrow down the search?
    assert len(no_quotes['results']) > len(quotes['results'])
    # Did we find only Claude Monet works, or did his lesser known brother Jim
    # Monet sneak into the results?
    for result in quotes['results']:
        assert result['creator'] == 'Claude Monet'

"""
These are the LEGACY API integration tests.

**Do not add further tests here. New tests should be added in v1_integration_test.**

End-to-end API tests. Can be used to verify a live deployment is functioning as
designed. Run with the `pytest -s` command from this directory.
"""

import json
import os
import uuid

import pytest
import requests

from catalog.api.constants.licenses import LICENSE_GROUPS
from catalog.api.models import Image
from catalog.api.utils.watermark import watermark


API_URL = os.getenv("INTEGRATION_TEST_URL", "http://localhost:8000")
known_apis = {
    "http://localhost:8000": "LOCAL",
    "https://api.openverse.engineering": "PRODUCTION",
    "https://api-dev.openverse.engineering": "TESTING",
}


def setup_module():
    if API_URL in known_apis:
        print(f"\n\033[1;31;40mTesting {known_apis[API_URL]} environment")


@pytest.fixture
def search_fixture():
    response = requests.get(f"{API_URL}/image/search?q=honey", verify=False)
    assert response.status_code == 200
    parsed = json.loads(response.text)
    return parsed


def test_search_quotes():
    """Test that a response is given even if the user messes up quote matching."""

    response = requests.get(f'{API_URL}/image/search?q="test"', verify=False)
    assert response.status_code == 200


def test_search(search_fixture):
    assert search_fixture["result_count"] > 0


def test_search_consistency():
    """
    Ensure that no duplicates appear in the first few pages of a search query.

    Elasticsearch sometimes reaches an inconsistent state, which causes search
    results to appear differently upon page refresh. This can also introduce
    image duplicates in subsequent pages.
    """

    n_pages = 5
    searches = {
        requests.get(f"{API_URL}/image/search?q=honey;page={page}", verify=False)
        for page in range(1, n_pages)
    }

    images = set()
    for response in searches:
        parsed = json.loads(response.text)
        for result in parsed["results"]:
            image_id = result["id"]
            assert image_id not in images
            images.add(image_id)


def test_image_detail(search_fixture):
    test_id = search_fixture["results"][0]["id"]
    response = requests.get(f"{API_URL}/image/{test_id}", verify=False)
    assert response.status_code == 200


def test_image_delete_invalid_creds(search_fixture):
    test_id = search_fixture["results"][0]["id"]
    should_fail = requests.delete(
        f"{API_URL}/image/{test_id}", auth=("invalid", "credentials"), verify=False
    )
    assert should_fail.status_code == 401


def test_image_delete(search_fixture):
    test_id = search_fixture["results"][0]["id"]
    response = requests.delete(
        f"{API_URL}/image/{test_id}",
        auth=("continuous_integration", "deploy"),
        verify=False,
    )
    assert response.status_code == 204
    deleted_response = requests.get(f"{API_URL}/image/{test_id}")
    assert deleted_response.status_code == 404


@pytest.fixture
def link_shortener_fixture(search_fixture):
    link_to_shorten = search_fixture["results"][0]["detail"]
    payload = {"full_url": link_to_shorten}
    response = requests.post(f"{API_URL}/link", json=payload, verify=False)
    assert response.status_code == 200
    return json.loads(response.text)


def test_link_shortener_create(link_shortener_fixture):
    assert "shortened_url" in link_shortener_fixture


def test_link_shortener_resolve(link_shortener_fixture):
    path = link_shortener_fixture["shortened_url"].split("/")[-1]
    response = requests.get(
        f"{API_URL}/link/{path}", allow_redirects=False, verify=False
    )
    assert response.status_code == 301


def test_stats():
    response = requests.get(f"{API_URL}/statistics/image", verify=False)
    parsed_response = json.loads(response.text)
    assert response.status_code == 200
    num_images = 0
    provider_count = 0
    for pair in parsed_response:
        image_count = pair["image_count"]
        num_images += int(image_count)
        provider_count += 1
    assert num_images > 0
    assert provider_count > 0


@pytest.mark.skip(reason="Disabled feature")
@pytest.fixture
def test_list_create(search_fixture):
    payload = {
        "title": "INTEGRATION TEST",
        "images": [search_fixture["results"][0]["id"]],
    }
    response = requests.post(API_URL + "/list", json=payload, verify=False)
    parsed_response = json.loads(response.text)
    assert response.status_code == 201
    return parsed_response


@pytest.mark.skip(reason="Disabled feature")
def test_list_detail(test_list_create):
    list_slug = test_list_create["url"].split("/")[-1]
    response = requests.get(f"{API_URL}/list/{list_slug}", verify=False)
    assert response.status_code == 200


@pytest.mark.skip(reason="Disabled feature")
def test_list_delete(test_list_create):
    list_slug = test_list_create["url"].split("/")[-1]
    token = test_list_create["auth"]
    headers = {"Authorization": f"Token {token}"}
    response = requests.delete(
        f"{API_URL}/list/{list_slug}", headers=headers, verify=False
    )
    assert response.status_code == 204


def test_license_type_filtering():
    """Ensure that multiple license type filters interact together correctly."""

    commercial = LICENSE_GROUPS["commercial"]
    modification = LICENSE_GROUPS["modification"]
    commercial_and_modification = set.intersection(modification, commercial)
    response = requests.get(
        f"{API_URL}/image/search?q=honey&lt=commercial,modification", verify=False
    )
    parsed = json.loads(response.text)
    for result in parsed["results"]:
        assert result["license"].upper() in commercial_and_modification


def test_single_license_type_filtering():
    commercial = LICENSE_GROUPS["commercial"]
    response = requests.get(
        f"{API_URL}/image/search?q=honey&lt=commercial", verify=False
    )
    parsed = json.loads(response.text)
    for result in parsed["results"]:
        assert result["license"].upper() in commercial


def test_specific_license_filter():
    response = requests.get(f"{API_URL}/image/search?q=honey&li=by", verify=False)
    parsed = json.loads(response.text)
    for result in parsed["results"]:
        assert result["license"] == "by"


def test_creator_quotation_grouping():
    """Test that quotation marks can be used to narrow down search results."""

    no_quotes = json.loads(
        requests.get(
            f"{API_URL}/image/search?creator=claude%20monet", verify=False
        ).text
    )
    quotes = json.loads(
        requests.get(
            f'{API_URL}/image/search?creator="claude%20monet"', verify=False
        ).text
    )
    # Did quotation marks actually narrow down the search?
    assert len(no_quotes["results"]) > len(quotes["results"])
    # Did we find only Claude Monet works, or did his lesser known brother Jim
    # Monet sneak into the results?
    for result in quotes["results"]:
        assert "Claude Monet" in result["creator"]


@pytest.fixture
def test_oauth2_registration():
    payload = {
        "name": f"INTEGRATION TEST APPLICATION {uuid.uuid4()}",
        "description": "A key for testing the OAuth2 registration process.",
        "email": "example@example.org",
    }
    response = requests.post(f"{API_URL}/oauth2/register/", json=payload, verify=False)
    parsed_response = json.loads(response.text)
    assert response.status_code == 201
    return parsed_response


def test_oauth2_token_exchange(test_oauth2_registration):
    client_id = test_oauth2_registration["client_id"]
    client_secret = test_oauth2_registration["client_secret"]
    token_exchange_request = (
        f"client_id={client_id}"
        f"&client_secret={client_secret}"
        f"&grant_type=client_credentials"
    )
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "cache-control": "no-cache",
    }
    response = json.loads(
        requests.post(
            f"{API_URL}/oauth2/token/",
            data=token_exchange_request,
            headers=headers,
            verify=False,
        ).text
    )
    assert "access_token" in response


def test_watermark_preserves_exif():
    img_with_exif = (
        "https://raw.githubusercontent.com/ianare/exif-samples/"
        "master/jpg/Canon_PowerShot_S40.jpg"
    )
    info = {
        "title": "test",
        "creator": "test",
        "license": "test",
        "license_version": "test",
    }
    _, exif = watermark(image_url=img_with_exif, info=info)
    assert exif is not None

    img_no_exif = (
        "https://creativecommons.org/wp-content/uploads/"
        "2019/03/9467312978_64cd5d2f3b_z.jpg"
    )
    _, no_exif = watermark(image_url=img_no_exif, info=info)
    assert no_exif is None


def test_attribution():
    """
    Check that the API includes an attribution string.

    Since there are some works where the title or creator is not known, the format of
    the attribution string can need to be tweaked slightly.
    """

    title_and_creator_missing = Image(
        identifier="ab80dbe1-414c-4ee8-9543-f9599312aeb8",
        title=None,
        creator=None,
        license="by",
        license_version="3.0",
    )
    print("\nAttribution examples:\n")
    print(title_and_creator_missing.attribution)
    assert "This work" in title_and_creator_missing.attribution

    title = "A foo walks into a bar"
    creator_missing = Image(
        identifier="ab80dbe1-414c-4ee8-9543-f9599312aeb8",
        title=title,
        creator=None,
        license="by",
        license_version="3.0",
    )
    print(creator_missing.attribution)
    assert title in creator_missing.attribution
    assert "by " not in creator_missing.attribution

    creator = "John Doe"
    title_missing = Image(
        identifier="ab80dbe1-414c-4ee8-9543-f9599312aeb8",
        title=None,
        creator=creator,
        license="by",
        license_version="3.0",
    )
    print(title_missing.attribution)
    assert creator in title_missing.attribution
    assert "This work" in title_missing.attribution

    all_data_present = Image(
        identifier="ab80dbe1-414c-4ee8-9543-f9599312aeb8",
        title=title,
        creator=creator,
        license="by",
        license_version="3.0",
    )
    print(all_data_present.attribution)
    assert title in all_data_present.attribution
    assert creator in all_data_present.attribution


def test_browse_by_provider():
    response = requests.get(f"{API_URL}/image/browse/behance", verify=False)
    assert response.status_code == 200
    parsed = json.loads(response.text)
    assert parsed["result_count"] > 0


def test_extension_filter():
    response = requests.get(f"{API_URL}/image/search?q=honey&extension=jpg")
    parsed = json.loads(response.text)
    for result in parsed["results"]:
        assert ".jpg" in result["url"]


@pytest.fixture
def search_factory():
    """Allow passing url parameters along with a search request."""

    def _parameterized_search(**kwargs):
        response = requests.get(f"{API_URL}/image/search", params=kwargs, verify=False)
        assert response.status_code == 200
        parsed = response.json()
        return parsed

    return _parameterized_search


@pytest.fixture
def search_with_dead_links(search_factory):
    """Test with ``filter_dead`` parameter set to ``False``."""

    def _search_with_dead_links(**kwargs):
        return search_factory(filter_dead=False, **kwargs)

    return _search_with_dead_links


@pytest.fixture
def search_without_dead_links(search_factory):
    """Test with ``filter_dead`` parameter set to ``True``."""

    def _search_without_dead_links(**kwargs):
        return search_factory(filter_dead=True, **kwargs)

    return _search_without_dead_links


def test_page_size_removing_dead_links(search_without_dead_links):
    """
    Test whether the number of results returned is equal to the requested page size.

    We have about 500 dead links in the sample data and should have around
    8 dead links in the first 100 results on a query composed of a single
    wildcard operator.

    """
    data = search_without_dead_links(q="*", pagesize=100)
    assert len(data["results"]) == 100


def test_dead_links_are_correctly_filtered(
    search_with_dead_links, search_without_dead_links
):
    """
    Test the results for the same query with and without dead links are different.

    We use the results' id to compare them.
    """
    data_with_dead_links = search_with_dead_links(q="*", pagesize=100)
    data_without_dead_links = search_without_dead_links(q="*", pagesize=100)

    comparisons = []
    for result_1 in data_with_dead_links["results"]:
        for result_2 in data_without_dead_links["results"]:
            comparisons.append(result_1["id"] == result_2["id"])

    # Some results should be different
    # so we should have less than 100 True comparisons
    assert comparisons.count(True) < 100


def test_page_consistency_removing_dead_links(search_without_dead_links):
    """Test that results in consecutive pages don't repeat when filtering dead links."""

    total_pages = 100
    pagesize = 5

    page_results = []
    for page in range(1, total_pages + 1):
        page_data = search_without_dead_links(q="*", pagesize=pagesize, page=page)
        page_results += page_data["results"]

    def no_duplicates(xs):
        s = set()
        for x in xs:
            if x in s:
                return False
            s.add(x)
        return True

    ids = list(map(lambda x: x["id"], page_results))
    # No results should be repeated so we should have no duplicate ids
    assert no_duplicates(ids)


def test_related_does_not_break():
    response = requests.get(
        f"{API_URL}/image/related/000000000000000000000000000000000000", verify=False
    )
    assert response.status_code == 404


@pytest.fixture
def related_factory():
    """Allow passing url parameters along with a related images request."""

    def _parameterized_search(identifier, **kwargs):
        response = requests.get(
            f"{API_URL}/image/related/{identifier}", params=kwargs, verify=False
        )
        assert response.status_code == 200
        parsed = response.json()
        return parsed

    return _parameterized_search


@pytest.mark.skip(
    reason="Generally, we don't paginate related images, so "
    "consistency is less of an issue."
)
def test_related_image_search_page_consistency(
    related_factory, search_without_dead_links
):
    initial_images = search_without_dead_links(q="*", pagesize=10)
    for image in initial_images["results"]:
        related = related_factory(image["id"])
        assert related["result_count"] > 0
        assert len(related["results"]) == 10

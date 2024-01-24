"""
End-to-end API tests.

Can be used to verify a live deployment is functioning as designed.
Run with the `pytest -s` command from this directory.
"""

import json

import pytest
import requests

from api.constants.licenses import LICENSE_GROUPS
from api.models import Image
from api.utils.watermark import watermark
from test.constants import API_URL


@pytest.fixture
def image_fixture():
    response = requests.get(f"{API_URL}/v1/images?q=dog", verify=False)
    assert response.status_code == 200
    parsed = json.loads(response.text)
    return parsed


def test_link_shortener_create():
    payload = {"full_url": "abcd"}
    response = requests.post(f"{API_URL}/v1/link/", json=payload, verify=False)
    assert response.status_code == 410


def test_link_shortener_resolve():
    response = requests.get(f"{API_URL}/v1/link/abc", verify=False)
    assert response.status_code == 410


@pytest.mark.skip(reason="Disabled feature")
@pytest.fixture
def test_list_create(image_fixture):
    payload = {
        "title": "INTEGRATION TEST",
        "images": [image_fixture["results"][0]["id"]],
    }
    response = requests.post(f"{API_URL}/list", json=payload, verify=False)
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
        f"{API_URL}/v1/images?q=dog&license_type=commercial,modification", verify=False
    )
    parsed = json.loads(response.text)
    for result in parsed["results"]:
        assert result["license"] in commercial_and_modification


def test_single_license_type_filtering():
    commercial = LICENSE_GROUPS["commercial"]
    response = requests.get(
        f"{API_URL}/v1/images?q=dog&license_type=commercial", verify=False
    )
    parsed = json.loads(response.text)
    for result in parsed["results"]:
        assert result["license"] in commercial


def test_specific_license_filter():
    response = requests.get(f"{API_URL}/v1/images?q=dog&license=by", verify=False)
    parsed = json.loads(response.text)
    for result in parsed["results"]:
        assert result["license"] == "by"


def test_creator_quotation_grouping():
    """Test that quotation marks can be used to narrow down search results."""

    no_quotes = json.loads(
        requests.get(f"{API_URL}/v1/images?creator=Steve%20Wedgwood", verify=False).text
    )
    quotes = json.loads(
        requests.get(
            f'{API_URL}/v1/images?creator="Steve%20Wedgwood"', verify=False
        ).text
    )
    # Did quotation marks actually narrow down the search?
    assert len(no_quotes["results"]) > len(quotes["results"])
    # Did we find only William Ford Stanley works, or also by others?
    for result in quotes["results"]:
        assert "Steve Wedgwood" in result["creator"]


@pytest.mark.skip(reason="Unmaintained feature/grequests ssl recursion bug")
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
    assert "This work" in title_and_creator_missing.attribution

    title = "A foo walks into a bar"
    creator_missing = Image(
        identifier="ab80dbe1-414c-4ee8-9543-f9599312aeb8",
        title=title,
        creator=None,
        license="by",
        license_version="3.0",
    )
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
    assert creator in title_missing.attribution
    assert "This work" in title_missing.attribution

    all_data_present = Image(
        identifier="ab80dbe1-414c-4ee8-9543-f9599312aeb8",
        title=title,
        creator=creator,
        license="by",
        license_version="3.0",
    )
    assert title in all_data_present.attribution
    assert creator in all_data_present.attribution


def test_license_override():
    null_license_url = Image(
        identifier="ab80dbe1-414c-4ee8-9543-f9599312aeb8",
        title="test",
        creator="test",
        license="by",
        license_version="3.0",
        meta_data={"license_url": "null"},
    )
    assert null_license_url.license_url is not None


def test_source_search():
    response = requests.get(f"{API_URL}/v1/images?source=flickr", verify=False)
    if response.status_code != 200:
        print(f"Request failed. Message: {response.body}")
    assert response.status_code == 200
    parsed = json.loads(response.text)
    assert parsed["result_count"] > 0


def test_extension_filter():
    response = requests.get(f"{API_URL}/v1/images?q=dog&extension=jpg")
    parsed = json.loads(response.text)
    for result in parsed["results"]:
        assert ".jpg" in result["url"]


@pytest.fixture
def recommendation_factory():
    """Allow passing url parameters along with a related images request."""

    def _parameterized_search(identifier, **kwargs):
        response = requests.get(
            f"{API_URL}/v1/recommendations?type=images&id={identifier}",
            params=kwargs,
            verify=False,
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
    recommendation, search_without_dead_links
):
    initial_images = search_without_dead_links(q="*", page_size=10)
    for image in initial_images["results"]:
        related = recommendation_factory(image["id"])
        assert related["result_count"] > 0
        assert len(related["results"]) == 10

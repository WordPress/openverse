"""
End-to-end API tests for images.

Can be used to verify a live deployment is functioning as designed.
Run with the `pytest -s` command from this directory.
"""

import pytest


pytestmark = pytest.mark.django_db


@pytest.fixture
def image_fixture(client):
    response = client.get("/v1/images/", {"q": "dog"})
    assert response.status_code == 200
    parsed = response.json()
    return parsed


@pytest.mark.parametrize(
    "url, expected_status_code",
    [
        ("https://any.domain/any/path/{identifier}", 200),  # no trailing slash
        ("https://any.domain/any/path/{identifier}/", 200),  # trailing slash
        ("https://any.domain/any/path/00000000-0000-0000-0000-000000000000", 400),
        ("https://any.domain/any/path/not-a-valid-uuid", 400),
    ],
)
def test_oembed_endpoint(image_fixture, url, expected_status_code, client):
    if "{identifier}" in url:
        url = url.format(identifier=image_fixture["results"][0]["id"])
    params = {"url": url}
    response = client.get("/v1/images/oembed/", params)
    assert response.status_code == expected_status_code


def test_oembed_endpoint_for_json(image_fixture, client):
    identifier = image_fixture["results"][0]["id"]
    params = {
        "url": f"https://any.domain/any/path/{identifier}",
        # 'format': 'json' is the default
    }
    response = client.get("/v1/images/oembed/", params)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"

    parsed = response.json()
    assert parsed["width"] == image_fixture["results"][0]["width"]
    assert parsed["height"] == image_fixture["results"][0]["height"]
    assert parsed["license_url"] == image_fixture["results"][0]["license_url"]

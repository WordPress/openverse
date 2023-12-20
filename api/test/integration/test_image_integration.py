"""
End-to-end API tests for images.

Can be used to verify a live deployment is functioning as designed.
Run with the `pytest -s` command from this directory.
"""

import pytest


pytestmark = pytest.mark.django_db


@pytest.fixture
def image_fixture(api_client):
    response = api_client.get("/v1/images/", {"q": "dog"})
    assert response.status_code == 200
    parsed = response.json()
    return parsed


@pytest.mark.parametrize(
    "url, expected_status_code",
    [
        pytest.param(
            "https://any.domain/any/path/{identifier}",
            200,
            id="OK; no trailing slash",
        ),
        pytest.param(
            "https://any.domain/any/path/{identifier}/",
            200,
            id="OK; trailing slash",
        ),  # trailing slash
        pytest.param(
            "https://any.domain/any/path/00000000-0000-0000-0000-000000000000",
            404,
            id="not OK; valid UUID but no matching identifier",
        ),
        pytest.param(
            "https://any.domain/any/path/not-a-valid-uuid",
            400,
            id="not OK; invalid UUID",
        ),
    ],
)
def test_oembed_endpoint(
    image_fixture, url: str, expected_status_code: int, api_client
):
    if "{identifier}" in url:
        url = url.format(identifier=image_fixture["results"][0]["id"])
    params = {"url": url}
    response = api_client.get("/v1/images/oembed/", params)
    assert response.status_code == expected_status_code


def test_oembed_endpoint_for_json(image_fixture, api_client):
    identifier = image_fixture["results"][0]["id"]
    params = {
        "url": f"https://any.domain/any/path/{identifier}",
        # 'format': 'json' is the default
    }
    response = api_client.get("/v1/images/oembed/", params)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"

    parsed = response.json()
    assert parsed["width"] == image_fixture["results"][0]["width"]
    assert parsed["height"] == image_fixture["results"][0]["height"]
    assert parsed["license_url"] == image_fixture["results"][0]["license_url"]

from django.urls import reverse

import pytest


@pytest.mark.parametrize(
    "path",
    [
        "/v1/auth_tokens/.well-known/oauth-authorization-server",
        "/v1/auth_tokens/.well-known/oauth-protected-resource",
        "/v1/auth_tokens/register/some-client-id/",
    ],
)
def test_toolkit_metadata_and_dcr_routes_are_not_mounted(api_client, path):
    res = api_client.get(path)

    assert res.status_code == 404


@pytest.mark.parametrize(
    ("name", "expected_path"),
    [
        ("oauth2_provider:authorize", "/v1/auth_tokens/authorize/"),
        ("oauth2_provider:revoke-token", "/v1/auth_tokens/revoke_token/"),
        ("oauth2_provider:introspect", "/v1/auth_tokens/introspect/"),
    ],
)
def test_toolkit_base_routes_are_still_mounted(name, expected_path):
    assert reverse(name) == expected_path

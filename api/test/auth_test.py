import time
import uuid
from test.constants import API_URL

from django.urls import reverse
from django.utils.http import urlencode

import pytest

from catalog.api.models import OAuth2Verification


@pytest.mark.django_db
@pytest.fixture
def test_auth_tokens_registration(client):
    data = {
        "name": f"INTEGRATION TEST APPLICATION {uuid.uuid4()}",
        "description": "A key for testing the OAuth2 registration process.",
        "email": "example@example.org",
    }
    res = client.post(
        "/v1/auth_tokens/register",
        data,
        verify=False,
    )
    assert res.status_code == 201
    res_data = res.json()
    return res_data


@pytest.mark.django_db
@pytest.fixture
def test_auth_token_exchange(client, test_auth_tokens_registration):
    client_id = test_auth_tokens_registration["client_id"]
    client_secret = test_auth_tokens_registration["client_secret"]
    data = urlencode(
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        }
    )
    res = client.post(
        "/v1/auth_tokens/token/",
        data,
        "application/x-www-form-urlencoded",
        verify=False,
    )
    res_data = res.json()
    assert "access_token" in res_data
    return res_data


@pytest.mark.django_db
def test_auth_email_verification(client, test_auth_token_exchange):
    # This test needs to cheat by looking in the database, so it will be
    # skipped in non-local environments.
    if API_URL == "http://localhost:8000":
        verify = OAuth2Verification.objects.last()
        code = verify.code
        path = reverse("verify-email", args=[code])
        res = client.get(path)
        assert res.status_code == 200
        test_auth_rate_limit_reporting(client, test_auth_token_exchange, verified=True)


@pytest.mark.django_db
def test_auth_rate_limit_reporting(client, test_auth_token_exchange, verified=False):
    # We're anonymous still, so we need to wait a second before exchanging
    # the token.
    time.sleep(1)
    token = test_auth_token_exchange["access_token"]
    res = client.get("/v1/rate_limit", HTTP_AUTHORIZATION=f"Bearer {token}")
    res_data = res.json()
    if verified:
        assert res_data["rate_limit_model"] == "standard"
        assert res_data["verified"] is True
    else:
        assert res_data["rate_limit_model"] == "standard"
        assert res_data["verified"] is False


@pytest.mark.django_db
def test_pase_size_limit_unauthed(client):
    query_params = {"filter_dead": False, "page_size": 20}
    res = client.get("/v1/images/", query_params)
    assert res.status_code == 200
    query_params["page_size"] = 21
    res = client.get("/v1/images/", query_params)
    assert res.status_code == 401


@pytest.mark.django_db
def test_page_size_limit_authed(client, test_auth_token_exchange):
    time.sleep(1)
    token = test_auth_token_exchange["access_token"]
    query_params = {"filter_dead": False, "page_size": 21}
    res = client.get("/v1/images/", query_params, HTTP_AUTHORIZATION=f"Bearer {token}")
    assert res.status_code == 200

    query_params = {"filter_dead": False, "page_size": 500}
    res = client.get("/v1/images/", query_params, HTTP_AUTHORIZATION=f"Bearer {token}")
    assert res.status_code == 200

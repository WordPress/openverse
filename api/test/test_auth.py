import time
import uuid
from test.constants import API_URL

from django.urls import reverse
from django.utils.http import urlencode

import pytest
from oauth2_provider.models import AccessToken

from api.models import OAuth2Verification, ThrottledApplication


cache_availability_params = pytest.mark.parametrize(
    "is_cache_reachable, cache_name",
    [(True, "oauth_cache"), (False, "unreachable_oauth_cache")],
)
# This parametrize decorator runs the test function with two scenarios:
# - one where the API can connect to Redis
# - one where it cannot and raises ``ConnectionError``
# The fixtures referenced here are defined below.


@pytest.fixture(autouse=True)
def oauth_cache(django_cache, monkeypatch):
    cache = django_cache
    monkeypatch.setattr("rest_framework.throttling.SimpleRateThrottle.cache", cache)
    yield cache


@pytest.fixture
def unreachable_oauth_cache(unreachable_django_cache, monkeypatch):
    cache = unreachable_django_cache
    monkeypatch.setattr("api.views.oauth2_views.cache", cache)
    yield cache


@pytest.mark.django_db
@pytest.fixture
def test_auth_tokens_registration(client):
    data = {
        "name": f"INTEGRATION TEST APPLICATION {uuid.uuid4()}",
        "description": "A key for testing the OAuth2 registration process.",
        "email": "example@example.org",
    }
    res = client.post(
        "/v1/auth_tokens/register/",
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
def test_auth_token_exchange_unsupported_method(client):
    res = client.get(
        "/v1/auth_tokens/token/",
        verify=False,
    )
    assert res.status_code == 405
    assert res.json()["detail"] == 'Method "GET" not allowed.'


def _integration_verify_most_recent_token(client):
    verify = OAuth2Verification.objects.last()
    code = verify.code
    path = reverse("verify-email", args=[code])
    return client.get(path)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "rate_limit_model",
    [x[0] for x in ThrottledApplication.RATE_LIMIT_MODELS],
)
@cache_availability_params
@pytest.mark.skipif(
    API_URL != "http://localhost:8000",
    reason=(
        "This test needs to cheat by looking in the database,"
        " so it needs to skip in non-local environments where"
        " that isn't possible."
    ),
)
def test_auth_email_verification(
    request,
    client,
    is_cache_reachable,
    cache_name,
    rate_limit_model,
    test_auth_token_exchange,
):
    res = _integration_verify_most_recent_token(client)
    assert res.status_code == 200
    test_auth_rate_limit_reporting(
        request,
        client,
        is_cache_reachable,
        cache_name,
        rate_limit_model,
        test_auth_token_exchange,
        verified=True,
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "rate_limit_model",
    [x[0] for x in ThrottledApplication.RATE_LIMIT_MODELS],
)
@cache_availability_params
def test_auth_rate_limit_reporting(
    request,
    client,
    is_cache_reachable,
    cache_name,
    rate_limit_model,
    test_auth_token_exchange,
    verified=False,
):
    request.getfixturevalue(cache_name)

    # We're anonymous still, so we need to wait a second before exchanging
    # the token.
    time.sleep(1)
    token = test_auth_token_exchange["access_token"]
    application = AccessToken.objects.get(token=token).application
    application.rate_limit_model = rate_limit_model
    application.save()
    res = client.get("/v1/rate_limit/", HTTP_AUTHORIZATION=f"Bearer {token}")
    res_data = res.json()
    if is_cache_reachable:
        assert res.status_code == 200
    else:
        assert res.status_code == 424
        assert res_data["requests_this_minute"] is None
        assert res_data["requests_today"] is None

    if verified:
        assert res_data["rate_limit_model"] == rate_limit_model
        assert res_data["verified"] is True
    else:
        assert res_data["rate_limit_model"] == rate_limit_model
        assert res_data["verified"] is False


@pytest.mark.django_db
@pytest.mark.parametrize(
    "verified",
    (True, False),
)
def test_auth_response_headers(
    client, verified, test_auth_tokens_registration, test_auth_token_exchange
):
    if verified:
        _integration_verify_most_recent_token(client)

    token = test_auth_token_exchange["access_token"]

    res = client.get("/v1/images/", HTTP_AUTHORIZATION=f"Bearer {token}")

    assert (
        res.headers["x-ov-client-application-name"]
        == test_auth_tokens_registration["name"]
    )
    assert res.headers["x-ov-client-application-verified"] == str(verified)


def test_unauthed_response_headers(client):
    res = client.get("/v1/images")

    assert "x-ov-client-application-name" not in res.headers
    assert "x-ov-client-application-verified" not in res.headers


@pytest.mark.django_db
@pytest.mark.parametrize(
    "sort_dir, exp_indexed_on",
    [
        ("desc", "2022-12-31"),
        ("asc", "2022-01-01"),
    ],
)
def test_sorting_authed(
    client, monkeypatch, test_auth_token_exchange, sort_dir, exp_indexed_on
):
    # Prevent DB lookup for ES results because DB is empty.
    monkeypatch.setattr("api.views.image_views.ImageSerializer.needs_db", False)

    time.sleep(1)
    token = test_auth_token_exchange["access_token"]
    query_params = {"unstable__sort_by": "indexed_on", "unstable__sort_dir": sort_dir}
    res = client.get("/v1/images/", query_params, HTTP_AUTHORIZATION=f"Bearer {token}")
    assert res.status_code == 200

    res_data = res.json()
    indexed_on = res_data["results"][0]["indexed_on"][:10]  # ``indexed_on`` is ISO.
    assert indexed_on == exp_indexed_on


@pytest.mark.django_db
@pytest.mark.parametrize(
    "authority_boost, exp_source",
    [
        ("1.0", "stocksnap"),
        ("0.0", "flickr"),  # Authority boost is disabled
    ],
)
def test_authority_authed(
    client, monkeypatch, test_auth_token_exchange, authority_boost, exp_source
):
    # Prevent DB lookup for ES results because DB is empty.
    monkeypatch.setattr("api.views.image_views.ImageSerializer.needs_db", False)

    time.sleep(1)
    token = test_auth_token_exchange["access_token"]
    query_params = {
        "q": "cat",
        "unstable__authority": "true",
        "unstable__authority_boost": authority_boost,
    }
    res = client.get("/v1/images/", query_params, HTTP_AUTHORIZATION=f"Bearer {token}")
    assert res.status_code == 200

    res_data = res.json()
    source = res_data["results"][0]["source"]
    assert source == exp_source


@pytest.mark.django_db
def test_page_size_limit_unauthed(client):
    query_params = {"page_size": 20}
    res = client.get("/v1/images/", query_params)
    assert res.status_code == 200
    query_params["page_size"] = 21
    res = client.get("/v1/images/", query_params)
    assert res.status_code == 401


@pytest.mark.django_db
def test_page_size_limit_authed(client, test_auth_token_exchange):
    time.sleep(1)
    token = test_auth_token_exchange["access_token"]
    query_params = {"page_size": 21}
    res = client.get("/v1/images/", query_params, HTTP_AUTHORIZATION=f"Bearer {token}")
    assert res.status_code == 200

    query_params = {"page_size": 500}
    res = client.get("/v1/images/", query_params, HTTP_AUTHORIZATION=f"Bearer {token}")
    assert res.status_code == 200

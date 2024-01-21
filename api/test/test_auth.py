import time
import uuid

from django.utils.http import urlencode

import pytest


import pickle

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
@pytest.mark.parametrize(
    "sort_dir, exp_indexed_on",
    [
        ("desc", "2022-12-31"),
        # ("asc", "2022-01-01"),
    ],
)
def test_sorting_authed(
    client, monkeypatch, test_auth_token_exchange, sort_dir, exp_indexed_on
):
    with open("test.pickle", "rb") as inp:
        tech_companies = pickle.load(inp)

    monkeypatch.setattr(
        "api.api.views.media_views.MediaViewSet.get_db_results", tech_companies
    )

    time.sleep(1)
    token = test_auth_token_exchange["access_token"]
    query_params = {"unstable__sort_by": "indexed_on", "unstable__sort_dir": sort_dir}
    res = client.get("/v1/images/", query_params, HTTP_AUTHORIZATION=f"Bearer {token}")
    assert res.status_code == 200

    res_data = res.json()
    indexed_on = res_data["results"][0]["indexed_on"][:10]  # ``indexed_on`` is ISO.
    assert indexed_on == exp_indexed_on

from test.factory.models.image import ImageFactory
from test.factory.models.oauth2 import AccessTokenFactory

from django.http import HttpResponse
from rest_framework.settings import api_settings
from rest_framework.test import force_authenticate
from rest_framework.views import APIView

import pytest

from api.utils import throttle
from api.views.media_views import MediaViewSet


cache_availability_params = pytest.mark.parametrize(
    "is_cache_reachable, cache_name",
    [(True, "throttle_cache"), (False, "unreachable_throttle_cache")],
)


@pytest.fixture(autouse=True)
def throttle_cache(django_cache, monkeypatch):
    cache = django_cache
    monkeypatch.setattr("rest_framework.throttling.SimpleRateThrottle.cache", cache)
    yield cache


@pytest.fixture
def unreachable_throttle_cache(unreachable_django_cache, monkeypatch):
    cache = unreachable_django_cache
    monkeypatch.setattr("rest_framework.throttling.SimpleRateThrottle.cache", cache)
    yield cache


@pytest.fixture(autouse=True)
def enable_throttles(settings):
    # Stash current settings so we can revert them after the test
    original_default_throttle_rates = api_settings.DEFAULT_THROTTLE_RATES

    # Put settings into base Django settings from which DRF reads
    # settings when we call `api_settings.reload()`
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = settings.DEFAULT_THROTTLE_RATES
    settings.REST_FRAMEWORK[
        "DEFAULT_THROTTLE_CLASSES"
    ] = settings.DEFAULT_THROTTLE_CLASSES

    # Reload the settings and read them from base Django settings
    # Also handles importing classes from class strings, etc
    api_settings.reload()

    # Put the parsed/imported default throttle classes onto the base media view set
    # to emulate the application startup. Without this, MediaViewSet has cached the
    # initial setting and won't re-retrieve it after we've called `api_settings.reload`
    MediaViewSet.throttle_classes = api_settings.DEFAULT_THROTTLE_CLASSES
    throttle.SimpleRateThrottle.THROTTLE_RATES = api_settings.DEFAULT_THROTTLE_RATES

    yield

    # Set everything back as it was before and reload settings again
    del settings.REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"]
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = original_default_throttle_rates
    api_settings.reload()
    MediaViewSet.throttle_classes = api_settings.DEFAULT_THROTTLE_CLASSES
    throttle.SimpleRateThrottle.THROTTLE_RATES = api_settings.DEFAULT_THROTTLE_RATES


@pytest.fixture
def access_token():
    token = AccessTokenFactory.create()
    token.application.verified = True
    token.application.save()
    return token


@pytest.fixture
def authed_request(access_token, request_factory):
    request = request_factory.get("/")

    force_authenticate(request, token=access_token.token)

    return request


@pytest.fixture
def view():
    return APIView()


def _gather_applied_rate_limit_scopes(api_response):
    scopes = set()
    for header in api_response.headers:
        if "X-RateLimit-Limit" in header:
            scopes.add(header.replace("X-RateLimit-Limit-", ""))

    return scopes


@pytest.mark.django_db
def test_anon_rate_limit_used_default_throttles(api_client):
    res = api_client.get("/v1/images/")
    applied_scopes = _gather_applied_rate_limit_scopes(res)

    anon_scopes = {
        throttle.BurstRateThrottle.scope,
        throttle.SustainedRateThrottle.scope,
    }

    assert anon_scopes == applied_scopes


@pytest.mark.django_db
def test_anon_frontend_referrer_used_default_throttles(api_client):
    res = api_client.get("/v1/images/", headers={"Referrer": "openverse.org"})
    applied_scopes = _gather_applied_rate_limit_scopes(res)

    ov_referrer_scopes = {
        throttle.OpenverseReferrerBurstRateThrottle.scope,
        throttle.OpenverseReferrerSustainedRateThrottle.scope,
    }

    assert ov_referrer_scopes == applied_scopes


@pytest.mark.django_db
@pytest.mark.parametrize(
    "rate_limit_model, expected_scopes",
    (
        pytest.param(
            "standard",
            {
                throttle.OAuth2IdBurstRateThrottle.scope,
                throttle.OAuth2IdSustainedRateThrottle.scope,
            },
            id="standard",
        ),
        pytest.param(
            "enhanced",
            {
                throttle.EnhancedOAuth2IdBurstRateThrottle.scope,
                throttle.EnhancedOAuth2IdSustainedRateThrottle.scope,
            },
            id="enhanced",
        ),
        pytest.param(
            "exempt",
            # Exempted requests have _no_ throttle class applied to them
            # This is a safe test because otherwise the anon scopes would apply
            # No scopes _must_ mean an exempt token, so long as the anon tests
            # are also working
            set(),
            id="exempt",
        ),
    ),
)
def test_oauth_rate_limit_used_default_throttles(
    rate_limit_model, expected_scopes, api_client, access_token
):
    access_token.application.rate_limit_model = rate_limit_model
    access_token.application.save()

    res = api_client.get(
        "/v1/images/", headers={"Authorization": f"Bearer {access_token.token}"}
    )
    applied_scopes = _gather_applied_rate_limit_scopes(res)

    assert expected_scopes == applied_scopes


@pytest.mark.django_db
def test_anon_rate_limit_used_thumbnail(api_client):
    image = ImageFactory.create()
    res = api_client.get(f"/v1/images/{image.identifier}/thumb/")
    applied_scopes = _gather_applied_rate_limit_scopes(res)

    anon_scopes = {
        throttle.AnonThumbnailRateThrottle.scope,
    }

    assert anon_scopes == applied_scopes


@pytest.mark.django_db
def test_anon_frontend_referrer_used_thumbnail(api_client):
    image = ImageFactory.create()
    res = api_client.get(
        f"/v1/images/{image.identifier}/thumb/", headers={"Referrer": "openverse.org"}
    )
    applied_scopes = _gather_applied_rate_limit_scopes(res)

    ov_referrer_scopes = {
        throttle.OpenverseReferrerAnonThumbnailRateThrottle.scope,
    }

    assert ov_referrer_scopes == applied_scopes


@pytest.mark.django_db
@pytest.mark.parametrize(
    "rate_limit_model, expected_scopes",
    (
        pytest.param(
            "standard",
            {throttle.OAuth2IdThumbnailRateThrottle.scope},
            id="standard",
        ),
        pytest.param(
            "enhanced",
            {throttle.OAuth2IdThumbnailRateThrottle.scope},
            id="enhanced",
        ),
        pytest.param(
            "exempt",
            # See note on test_oauth_rate_limit_used_default_throttles's
            # `exempt` entry. The same applies here. Exempt tokens should
            # have _no_ scopes applied.
            set(),
            id="exempt",
        ),
    ),
)
def test_oauth_rate_limit_used_thumbnail(
    rate_limit_model, expected_scopes, api_client, access_token
):
    # All oauth token scopes use the base oauth thumbnail rate limit
    access_token.application.rate_limit_model = rate_limit_model
    access_token.application.save()
    image = ImageFactory.create()

    res = api_client.get(
        f"/v1/images/{image.identifier}/thumb/",
        headers={"Authorization": f"Bearer {access_token.token}"},
    )
    applied_scopes = _gather_applied_rate_limit_scopes(res)

    assert expected_scopes == applied_scopes


@pytest.mark.django_db
@cache_availability_params
def test_rate_limit_headers(request_factory, is_cache_reachable, cache_name, request):
    request.getfixturevalue(cache_name)

    limit = 2  # number of allowed requests, we will go 1 above this limit

    class DummyThrottle(throttle.BurstRateThrottle):
        THROTTLE_RATES = {"anon_burst": f"{limit}/hour"}

    class ThrottledView(APIView):
        throttle_classes = [DummyThrottle]

        def get(self, request):
            return HttpResponse("ok")

    view = ThrottledView().as_view()
    request = request_factory.get("/")

    # Send three requests. The third one should be throttled.
    for idx in range(1, limit + 2):
        response = view(request)
        headers = [h for h in response.headers.items() if "X-RateLimit" in h[0]]

        if is_cache_reachable:
            # Assert that request returns 429 response if limit has been exceeded.
            assert response.status_code == 429 if idx == limit + 1 else 200
            # Assert that the 'Available' header constantly decrements, but not below zero.
            assert [
                ("X-RateLimit-Limit-anon_burst", f"{limit}/hour"),
                ("X-RateLimit-Available-anon_burst", str(max(0, limit - idx))),
            ] == headers
        else:
            # Throttling gets disabled if Redis cannot cache request history.
            assert response.status_code == 200
            # Headers are not set if Redis cannot cache request history.
            assert not headers


@pytest.mark.django_db
@cache_availability_params
def test_rate_limit_headers_when_no_scope(
    request_factory, is_cache_reachable, cache_name, request
):
    request.getfixturevalue(cache_name)

    limit = 10  # number of allowed requests, we will go 1 above this limit

    class ThrottledView(APIView):
        throttle_classes = [throttle.TenPerDay]

        def get(self, request):
            return HttpResponse("ok")

    view = ThrottledView().as_view()
    request = request_factory.get("/")

    # Send limit + 1 requests. The last one should be throttled.
    for idx in range(1, limit + 2):
        response = view(request)
        headers = [h for h in response.headers.items() if "X-RateLimit" in h[0]]

        if is_cache_reachable:
            # Assert that request returns 429 response if limit has been exceeded.
            assert response.status_code == 429 if idx == limit + 1 else 200
            # Assert that headers match the throttle class.
            assert [
                ("X-RateLimit-Limit-tenperday", "10/day"),
                ("X-RateLimit-Available-tenperday", str(max(0, limit - idx))),
            ] == headers
        else:
            # Throttling gets disabled if Redis cannot cache request history.
            assert response.status_code == 200
            # Headers are not set if Redis cannot cache request history.
            assert not headers

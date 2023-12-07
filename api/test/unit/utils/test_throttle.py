from test.factory.models.oauth2 import AccessTokenFactory

from django.core.cache import cache
from rest_framework.test import force_authenticate
from rest_framework.views import APIView

import pytest

from api.models.oauth import ThrottledApplication
from api.utils.throttle import (
    AbstractAnonRateThrottle,
    AbstractOAuth2IdRateThrottle,
    BurstRateThrottle,
    TenPerDay,
)


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


@pytest.mark.parametrize(
    "throttle_class",
    AbstractAnonRateThrottle.__subclasses__(),
)
@pytest.mark.django_db
def test_anon_rate_throttle_ignores_authed_requests(
    throttle_class, authed_request, view
):
    throttle = throttle_class()
    assert throttle.get_cache_key(view.initialize_request(authed_request), view) is None


@pytest.mark.parametrize(
    "throttle_class",
    AbstractAnonRateThrottle.__subclasses__(),
)
@pytest.mark.django_db
def test_anon_rate_throttle_returns_formatted_cache_key_for_anonymous_request(
    throttle_class, request_factory, view
):
    request = request_factory.get("/")
    throttle = throttle_class()
    assert throttle.get_cache_key(view.initialize_request(request), view) is not None


@pytest.mark.parametrize(
    "throttle_class",
    AbstractOAuth2IdRateThrottle.__subclasses__(),
)
@pytest.mark.django_db
def test_abstract_oauth2_id_rate_throttle_applies_if_token_app_rate_limit_model_matches(
    access_token, authed_request, view, throttle_class
):
    throttle = throttle_class()
    access_token.application.rate_limit_model = (
        throttle_class.applies_to_rate_limit_model
    )
    access_token.application.save()
    assert (
        throttle.get_cache_key(view.initialize_request(authed_request), view)
        is not None
    )


@pytest.mark.parametrize(
    "throttle_class",
    AbstractOAuth2IdRateThrottle.__subclasses__(),
)
@pytest.mark.django_db
def test_abstract_oauth2_id_rate_throttle_does_not_apply_if_token_app_rate_limit_model_differs(
    access_token, authed_request, view, throttle_class
):
    throttle = throttle_class()
    access_token.application.rate_limit_model = next(
        m[0]
        for m in ThrottledApplication.RATE_LIMIT_MODELS
        if m[0] != throttle_class.applies_to_rate_limit_model
    )
    access_token.application.save()
    assert throttle.get_cache_key(view.initialize_request(authed_request), view) is None


@pytest.mark.django_db
def test_rate_limit_headers(request_factory):
    cache.delete_pattern("throttle_*")
    limit = 2

    class DummyThrottle(BurstRateThrottle):
        THROTTLE_RATES = {"anon_burst": f"{limit}/hour"}

    class ThrottledView(APIView):
        throttle_classes = [DummyThrottle]

    view = ThrottledView().as_view()
    request = request_factory.get("/")

    # Send three requests. The third one should be throttled.
    for idx in range(1, limit + 2):
        response = view(request)
        headers = [h for h in response.headers.items() if "X-RateLimit" in h[0]]

        # Assert that request returns 429 response if limit has been exceeded.
        assert response.status_code == 429 if idx == limit + 1 else 200

        # Assert that the 'Available' header constantly decrements, but not below zero.
        assert [
            ("X-RateLimit-Limit-anon_burst", f"{limit}/hour"),
            ("X-RateLimit-Available-anon_burst", str(max(0, limit - idx))),
        ] == headers


@pytest.mark.django_db
def test_rate_limit_headers_when_no_scope(request_factory):
    cache.delete_pattern("throttle_*")

    class ThrottledView(APIView):
        throttle_classes = [TenPerDay]

    view = ThrottledView().as_view()
    request = request_factory.get("/")

    response = view(request)
    headers = [h for h in response.headers.items() if "X-RateLimit" in h[0]]
    assert [
        ("X-RateLimit-Limit-tenperday", "10/day"),
        ("X-RateLimit-Available-tenperday", "9"),
    ] == headers

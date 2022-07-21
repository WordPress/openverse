from test.factory.models.oauth2 import AccessTokenFactory

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.views import APIView

import pytest
from fakeredis import FakeRedis

from catalog.api.models.oauth import ThrottledApplication
from catalog.api.utils.throttle import (
    AbstractAnonRateThrottle,
    AbstractOAuth2IdRateThrottle,
)


@pytest.fixture(autouse=True)
def redis(monkeypatch) -> FakeRedis:
    fake_redis = FakeRedis()

    def get_redis_connection(*args, **kwargs):
        return fake_redis

    monkeypatch.setattr(
        "catalog.api.utils.throttle.get_redis_connection", get_redis_connection
    )

    yield fake_redis
    fake_redis.client().close()


@pytest.fixture
def request_factory() -> APIRequestFactory():
    request_factory = APIRequestFactory(defaults={"REMOTE_ADDR": "192.0.2.1"})

    return request_factory


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
def test_anon_rate_throttle_ignores_exempted_ips(
    throttle_class, redis, request_factory, view
):
    request = request_factory.get("/")
    redis.sadd("ip-whitelist", request.META["REMOTE_ADDR"])
    throttle = throttle_class()
    assert throttle.get_cache_key(view.initialize_request(request), view) is None


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

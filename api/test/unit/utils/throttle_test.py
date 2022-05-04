from test.factory.models.oauth2 import AccessTokenFactory

from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.views import APIView

import pytest
from fakeredis import FakeRedis

from catalog.api.utils.oauth2_helper import get_token_info
from catalog.api.utils.throttle import (
    ApiKeyExemption,
    ExemptionAwareThrottle,
    InternalNetworkExemption,
    ThrottleExemption,
)


class HardThrottle(ExemptionAwareThrottle):
    """
    A test throttle that denies all requests.

    This is helpful for testing whether the exemptions
    are working.
    """

    rate = "0/second"
    scope = "test"

    def get_cache_key(self, request, view):
        return {
            "scope": self.scope,
            "ident": self.get_ident(request),
        }


class MockInternalNetworkExemptThrottle(HardThrottle):
    exemption_classes = (InternalNetworkExemption,)


class MockApiKeyExemptThrottle(HardThrottle):
    exemption_classes = (ApiKeyExemption,)


class FooRouteExemption(ThrottleExemption):
    def is_exempt(self):
        return self.request.path.startswith("/foo")


class MockMultipleExemptionThrottle(HardThrottle):
    exemption_classes = (InternalNetworkExemption, ApiKeyExemption, FooRouteExemption)


def get_throttled_view(throttle_class):
    class MockView(APIView):
        throttle_classes = (throttle_class,)

        def get(self, request):
            return Response("foo")

    return MockView().as_view()


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
    return AccessTokenFactory.create()


@pytest.fixture
def authed_request(access_token, request_factory):
    request = request_factory.get("/")

    force_authenticate(request, token=access_token.token)

    return request


def assert_view_consistent_status_code(view, request, expected_status, times=4):
    for _ in range(times):
        assert view(request).status_code == expected_status


def assert_throttles(view, request, times=4):
    assert_view_consistent_status_code(view, request, expected_status=429, times=times)


def assert_does_not_throttle(view, request, times=4):
    assert_view_consistent_status_code(view, request, expected_status=200, times=times)


def test_hard_throttle_denies_requests(request_factory):
    view = get_throttled_view(HardThrottle)
    request = request_factory.get("/")
    assert_throttles(view, request)


def test_internal_network_exemption_passes_when_ip_in_allowlist(redis, request_factory):
    view = get_throttled_view(MockInternalNetworkExemptThrottle)
    request = request_factory.get("/")
    redis.sadd(InternalNetworkExemption.redis_set_name, request.META["REMOTE_ADDR"])
    assert_does_not_throttle(view, request)


def test_internal_network_exemption_throttles_when_ip_not_in_allowlist(
    redis, request_factory
):
    view = get_throttled_view(MockInternalNetworkExemptThrottle)
    request = request_factory.get("/")
    assert not redis.sismember(
        InternalNetworkExemption.redis_set_name, request.META["REMOTE_ADDR"]
    )
    assert_throttles(view, request)


@pytest.mark.django_db
def test_api_key_exemption_passes_when_token_in_allowlist(
    redis, access_token, authed_request
):
    view = get_throttled_view(MockApiKeyExemptThrottle)
    client_id, _, _ = get_token_info(access_token.token)
    redis.sadd(ApiKeyExemption.redis_set_name, client_id)
    assert_does_not_throttle(view, authed_request)


@pytest.mark.django_db
def test_api_key_exemption_throttles_when_token_not_in_allowlist(
    redis, access_token, authed_request
):
    view = get_throttled_view(MockApiKeyExemptThrottle)
    client_id, _, _ = get_token_info(access_token.token)
    assert not redis.sismember(ApiKeyExemption.redis_set_name, client_id)
    assert_throttles(view, authed_request)


@pytest.mark.django_db
def test_api_key_exemption_throttles_with_unauthed_request(request_factory):
    request = request_factory.get("/")
    view = get_throttled_view(MockApiKeyExemptThrottle)
    assert_throttles(view, request)


@pytest.mark.django_db
def test_multiple_exemptions_allows_if_one_passes_api_key(
    redis, access_token, authed_request
):
    view = get_throttled_view(MockMultipleExemptionThrottle)
    client_id, _, _ = get_token_info(access_token.token)
    redis.sadd(ApiKeyExemption.redis_set_name, client_id)
    assert not redis.sismember(
        InternalNetworkExemption.redis_set_name, authed_request.META["REMOTE_ADDR"]
    )
    assert_does_not_throttle(view, authed_request)


@pytest.mark.django_db
def test_multiple_exemptions_allows_if_one_passes_internal_network(
    redis, access_token, authed_request
):
    view = get_throttled_view(MockMultipleExemptionThrottle)
    client_id, _, _ = get_token_info(access_token.token)
    redis.sadd(
        InternalNetworkExemption.redis_set_name, authed_request.META["REMOTE_ADDR"]
    )
    assert not redis.sismember(ApiKeyExemption.redis_set_name, client_id)
    assert_does_not_throttle(view, authed_request)


@pytest.mark.django_db
def test_multiple_exemptions_throttles_if_none_pass(
    redis, access_token, authed_request
):
    view = get_throttled_view(MockMultipleExemptionThrottle)
    client_id, _, _ = get_token_info(access_token.token)
    assert not redis.sismember(
        InternalNetworkExemption.redis_set_name, authed_request.META["REMOTE_ADDR"]
    )
    assert not redis.sismember(ApiKeyExemption.redis_set_name, client_id)
    assert_throttles(view, authed_request)

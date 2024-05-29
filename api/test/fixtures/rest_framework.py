from rest_framework.test import APIClient, APIRequestFactory
from rest_framework.views import APIView

import pytest

from test.factory.models.oauth2 import AccessTokenFactory


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


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
    request = request_factory.get(
        "/", HTTP_AUTHORIZATION=f"Bearer {access_token.token}"
    )

    return APIView().initialize_request(request)


@pytest.fixture
def anon_request(request_factory):
    return APIView().initialize_request(request_factory.get("/"))

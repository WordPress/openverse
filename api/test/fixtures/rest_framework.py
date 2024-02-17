from rest_framework.test import APIClient, APIRequestFactory

import pytest


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def request_factory() -> APIRequestFactory():
    request_factory = APIRequestFactory(defaults={"REMOTE_ADDR": "192.0.2.1"})

    return request_factory

from test.factory.models import AudioFactory, ImageFactory
from test.factory.models.media import CREATED_BY_FIXTURE_MARKER
from unittest.mock import MagicMock

from rest_framework.test import APIClient, APIRequestFactory

import pytest
from elasticsearch import Elasticsearch


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture(autouse=True)
def capture_exception(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("sentry_sdk.capture_exception", mock)

    yield mock


@pytest.fixture
def request_factory() -> APIRequestFactory():
    request_factory = APIRequestFactory(defaults={"REMOTE_ADDR": "192.0.2.1"})

    return request_factory


@pytest.fixture(params=["image", "audio"])
def origin_index(request):
    return request.param


@pytest.fixture
def model_factory(request: pytest.FixtureRequest):
    match request.getfixturevalue("origin_index"):
        case "audio":
            return AudioFactory
        case "image":
            return ImageFactory
        case unknown:
            raise ValueError(f"Unknown origin_index '{unknown}'")


@pytest.fixture(autouse=True)
def cleanup_test_documents_elasticsearch(
    request, origin_index, model_factory, settings
):
    yield None
    # This fixture only matters after tests are finished

    if not request.node.get_closest_marker("django_db"):
        # If the test isn't configured to access the database
        # then it couldn't have created any new documents,
        # so we can skip cleanup
        return

    es: Elasticsearch = settings.ES

    es.delete_by_query(
        index="*",
        body={"query": {"match": {"tags.name": CREATED_BY_FIXTURE_MARKER}}},
        refresh=True,
    )

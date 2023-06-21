from dataclasses import dataclass
from test.factory import models as model_factories
from test.factory.models.media import CREATED_BY_FIXTURE_MARKER, MediaFactory
from unittest.mock import MagicMock

from rest_framework.test import APIClient, APIRequestFactory

import pytest
from elasticsearch import Elasticsearch
from fakeredis import FakeRedis

from api.serializers.audio_serializers import (
    AudioSearchRequestSerializer,
    AudioSerializer,
)
from api.serializers.image_serializers import (
    ImageSearchRequestSerializer,
    ImageSerializer,
)
from api.serializers.media_serializers import (
    MediaSearchRequestSerializer,
    MediaSerializer,
)


@pytest.fixture()
def redis(monkeypatch) -> FakeRedis:
    fake_redis = FakeRedis()

    def get_redis_connection(*args, **kwargs):
        return fake_redis

    monkeypatch.setattr("django_redis.get_redis_connection", get_redis_connection)

    yield fake_redis
    fake_redis.client().close()


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


@dataclass
class MediaTypeConfig:
    media_type: str
    url_prefix: str
    origin_index: str
    filtered_index: str
    model_factory: MediaFactory
    mature_factory: MediaFactory
    search_request_serializer: MediaSearchRequestSerializer
    model_serializer: MediaSerializer


MEDIA_TYPE_CONFIGS = {
    "image": MediaTypeConfig(
        media_type="image",
        url_prefix="images",
        origin_index="image",
        filtered_index="image-filtered",
        model_factory=model_factories.ImageFactory,
        mature_factory=model_factories.MatureImageFactory,
        search_request_serializer=ImageSearchRequestSerializer,
        model_serializer=ImageSerializer,
    ),
    "audio": MediaTypeConfig(
        media_type="audio",
        url_prefix="audio",
        origin_index="audio",
        filtered_index="audio-filtered",
        model_factory=model_factories.AudioFactory,
        mature_factory=model_factories.MatureAudioFactory,
        search_request_serializer=AudioSearchRequestSerializer,
        model_serializer=AudioSerializer,
    ),
}


@pytest.fixture
def image_media_type_config():
    return MEDIA_TYPE_CONFIGS["image"]


@pytest.fixture
def audio_media_type_config():
    return MEDIA_TYPE_CONFIGS["audio"]


@pytest.fixture(
    params=MEDIA_TYPE_CONFIGS.values(),
    ids=lambda x: f"{x.media_type}_media_type_config",
)
def media_type_config(request: pytest.FixtureRequest) -> MediaTypeConfig:
    return request.param


@pytest.fixture(autouse=True)
def cleanup_elasticsearch_test_documents(request, settings):
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

from dataclasses import dataclass
from test.factory import models as model_factories
from test.factory.models.media import (
    CREATED_BY_FIXTURE_MARKER,
    MediaFactory,
    MediaReportFactory,
)
from unittest.mock import MagicMock

from rest_framework.test import APIClient, APIRequestFactory

import pook
import pytest
from elasticsearch import Elasticsearch
from fakeredis import FakeRedis

from api.models import (
    Audio,
    DeletedAudio,
    DeletedImage,
    Image,
    MatureAudio,
    MatureImage,
)
from api.models.media import AbstractDeletedMedia, AbstractMatureMedia, AbstractMedia
from api.serializers.audio_serializers import (
    AudioReportRequestSerializer,
    AudioSearchRequestSerializer,
    AudioSerializer,
)
from api.serializers.image_serializers import (
    ImageReportRequestSerializer,
    ImageSearchRequestSerializer,
    ImageSerializer,
)
from api.serializers.media_serializers import (
    MediaReportRequestSerializer,
    MediaSearchRequestSerializer,
    MediaSerializer,
)
from api.views.audio_views import AudioViewSet
from api.views.image_views import ImageViewSet
from api.views.media_views import MediaViewSet


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
def sentry_capture_exception(monkeypatch):
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
    model_class: AbstractMedia
    mature_factory: MediaFactory
    mature_class: AbstractMatureMedia
    search_request_serializer: MediaSearchRequestSerializer
    model_serializer: MediaSerializer
    report_serializer: MediaReportRequestSerializer
    report_factory: MediaReportFactory
    deleted_class: AbstractDeletedMedia
    viewset_class: MediaViewSet

    @property
    def indexes(self):
        return (self.origin_index, self.filtered_index)


MEDIA_TYPE_CONFIGS = {
    "image": MediaTypeConfig(
        media_type="image",
        url_prefix="images",
        origin_index="image",
        filtered_index="image-filtered",
        model_factory=model_factories.ImageFactory,
        model_class=Image,
        mature_factory=model_factories.MatureImageFactory,
        search_request_serializer=ImageSearchRequestSerializer,
        model_serializer=ImageSerializer,
        report_serializer=ImageReportRequestSerializer,
        report_factory=model_factories.ImageReportFactory,
        mature_class=MatureImage,
        deleted_class=DeletedImage,
        viewset_class=ImageViewSet,
    ),
    "audio": MediaTypeConfig(
        media_type="audio",
        url_prefix="audio",
        origin_index="audio",
        filtered_index="audio-filtered",
        model_factory=model_factories.AudioFactory,
        model_class=Audio,
        mature_factory=model_factories.MatureAudioFactory,
        search_request_serializer=AudioSearchRequestSerializer,
        model_serializer=AudioSerializer,
        report_serializer=AudioReportRequestSerializer,
        report_factory=model_factories.AudioReportFactory,
        mature_class=MatureAudio,
        deleted_class=DeletedAudio,
        viewset_class=AudioViewSet,
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

    # If pook was activated by a test and not deactivated
    # (usually because the test failed and something prevent
    # pook from cleaning up after itself), disable here so that
    # the ES request on the next line doesn't get intercepted,
    # causing pook to raise an exception about the request not
    # matching and the fixture documents not getting cleaned.
    pook.disable()

    es.delete_by_query(
        index="*",
        query={"match": {"tags.name": CREATED_BY_FIXTURE_MARKER}},
        refresh=True,
    )

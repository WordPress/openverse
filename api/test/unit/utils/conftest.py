import json
from pathlib import Path

import pytest
from fakeredis import FakeRedis


@pytest.fixture(autouse=True)
def redis(monkeypatch) -> FakeRedis:
    fake_redis = FakeRedis()

    def get_redis_connection(*args, **kwargs):
        return fake_redis

    monkeypatch.setattr("django_redis.get_redis_connection", get_redis_connection)

    yield fake_redis
    fake_redis.client().close()


@pytest.fixture(scope="session")
def mock_image_data():
    mock_image_path = Path(__file__).parent / ".." / ".." / "factory"
    mock_image_file = mock_image_path / "sample-image.jpg"
    mock_image_info = json.loads(
        (mock_image_path / "sample-image-info.json").read_text()
    )

    yield {
        "file": mock_image_file,
        "byes": mock_image_file.read_bytes(),
        "info": mock_image_info,
    }

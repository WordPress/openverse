import json
from pathlib import Path

import pook
import pytest

from api.utils.watermark import HEADERS, watermark


_MOCK_IMAGE_PATH = Path(__file__).parent / ".." / ".." / "factory"
_MOCK_IMAGE_BYTES = (_MOCK_IMAGE_PATH / "sample-image.jpg").read_bytes()
_MOCK_IMAGE_INFO = json.loads((_MOCK_IMAGE_PATH / "sample-image-info.json").read_text())


@pytest.fixture
def mock_request():
    with pook.use():
        mock = (
            pook.get("http://example.com/")
            .header("User-Agent", HEADERS["User-Agent"])
            .reply(200)
            .body(_MOCK_IMAGE_BYTES, binary=True)
            .mock
        )
        yield mock


def test_watermark_image_sends_ua_header(mock_request):
    watermark("http://example.com/", _MOCK_IMAGE_INFO)
    # ``pook`` will only match if UA header is sent.
    assert mock_request.total_matches > 0


# Previously, wrapped titles would throw a TypeError:
# slice indices must be integers or None or have an __index__ method.
# See: https://github.com/WordPress/openverse/issues/2466
def test_long_title_wraps_correctly(mock_request):
    # Make the title 400 chars long
    _MOCK_IMAGE_INFO_LONG_TITLE = dict(_MOCK_IMAGE_INFO)
    _MOCK_IMAGE_INFO_LONG_TITLE["title"] = "a" * 400

    watermark("http://example.com/", _MOCK_IMAGE_INFO_LONG_TITLE)
    assert mock_request.total_matches > 0

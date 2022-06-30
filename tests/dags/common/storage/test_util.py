import logging

import pytest
from common.storage import util
from common.storage.audio import AudioStore
from common.storage.image import ImageStore


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.DEBUG
)


def test_get_media_store_class():
    assert util.get_media_store_class("image") == ImageStore
    assert util.get_media_store_class("audio") == AudioStore


def test_get_media_store_class_raises_error_for_undefined_class():
    with pytest.raises(ValueError, match="No MediaStore is configured for type: foo"):
        util.get_media_store_class("foo")

from indexer_worker.elasticsearch_models import Image
from tests.utils import create_mock_image


class TestImage:
    @staticmethod
    def test_size():
        small = create_mock_image({"height": 600, "width": 300})
        assert small.size == "small"
        huge = create_mock_image({"height": 4096, "width": 4096})
        assert huge.size == "large"

    @staticmethod
    def test_aspect_ratio():
        square = create_mock_image({"height": 300, "width": 300})
        assert square.aspect_ratio == "square"
        tall = create_mock_image({"height": 500, "width": 200})
        assert tall.aspect_ratio == Image.AspectRatios.TALL.name.lower()
        wide = create_mock_image({"height": 200, "width": 500})
        assert wide.aspect_ratio == Image.AspectRatios.WIDE.name.lower()

    @staticmethod
    def test_extension():
        no_extension = create_mock_image({"url": "https://creativecommons.org/hello"})
        assert no_extension.extension is None
        jpg = create_mock_image({"url": "https://creativecommons.org/hello.jpg"})
        assert jpg.extension == "jpg"

    @staticmethod
    def test_mature_metadata():
        # Received upstream indication the work is mature
        meta = {"mature": True}
        mature_metadata = create_mock_image({"meta_data": meta})
        assert mature_metadata["mature"]

    @staticmethod
    def test_mature_api():
        # Manually flagged work as mature ourselves
        mature_work = create_mock_image({"mature": True})
        assert mature_work["mature"]

    @staticmethod
    def test_default_maturity():
        # Default to not flagged
        sfw = create_mock_image()
        assert not sfw["mature"]

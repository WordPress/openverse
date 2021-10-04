import datetime
from uuid import uuid4

from psycopg2.extras import Json

from ingestion_server.cleanup import CleanupFunctions
from ingestion_server.elasticsearch_models import Image


def create_mock_image(override=None):
    """
    Produce a mock image. Override default fields by passing in a dict with the
    desired keys and values.

    For example, to make an image with a custom title and default everything
    else:
    >>> create_mock_image({'title': 'My title'})
    :return:
    """
    test_popularity = {"views": 50, "likes": 3, "comments": 1}
    license_url = "https://creativecommons.org/licenses/by/2.0/fr/legalcode"
    meta_data = {"popularity_metrics": test_popularity, "license_url": license_url}
    test_data = {
        "id": 0,
        "title": "Unit test title",
        "identifier": str(uuid4()),
        "creator": "Eric Idle",
        "creator_url": "https://creativecommons.org",
        "tags": [{"name": "test", "accuracy": 0.9}],
        "created_on": datetime.datetime.now(),
        "url": "https://creativecommons.org",
        "thumbnail": "https://creativecommons.org",
        "provider": "test",
        "source": "test",
        "license": "cc-by",
        "license_version": "4.0",
        "foreign_landing_url": "https://creativecommons.org",
        "view_count": 0,
        "height": 500,
        "width": 500,
        "mature": False,
        "meta_data": meta_data,
    }
    if override:
        for k, v in override.items():
            test_data[k] = v
    schema = {}
    row = []
    idx = 0
    for k, v in test_data.items():
        schema[k] = idx
        row.append(v)
        idx += 1
    return Image.database_row_to_elasticsearch_doc(row, schema)


class TestImage:
    @staticmethod
    def test_size():
        small = create_mock_image({"height": 600, "width": 300})
        assert small.size == Image.ImageSizes.SMALL.name.lower()
        huge = create_mock_image({"height": 4096, "width": 4096})
        assert huge.size == Image.ImageSizes.LARGE.name.lower()

    @staticmethod
    def test_aspect_ratio():
        square = create_mock_image({"height": 300, "width": 300})
        assert square.aspect_ratio == Image.AspectRatios.SQUARE.name.lower()
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


class TestCleanup:
    @staticmethod
    def test_tag_blacklist():
        tags = [
            {"name": "cc0"},
            {"name": " cc0"},
            {"name": "valid", "accuracy": 0.99},
            {"name": "valid_no_accuracy"},
            {
                "name": "garbage:=metacrap",
            },
        ]
        result = str(CleanupFunctions.cleanup_tags(tags))
        expected = str(
            Json([{"name": "valid", "accuracy": 0.99}, {"name": "valid_no_accuracy"}])
        )

        assert result == expected

    @staticmethod
    def test_tag_no_update():
        tags = [{"name": "valid", "accuracy": 0.92}]
        result = CleanupFunctions.cleanup_tags(tags)
        assert result is None

    @staticmethod
    def test_accuracy_filter():
        tags = [
            {"name": "inaccurate", "accuracy": 0.5},
            {"name": "accurate", "accuracy": 0.999},
        ]
        result = str(CleanupFunctions.cleanup_tags(tags))
        expected = str(Json([{"name": "accurate", "accuracy": 0.999}]))
        assert result == expected

    @staticmethod
    def test_url_protocol_fix():
        bad_url = "flickr.com"
        tls_support_cache = {}
        result = CleanupFunctions.cleanup_url(bad_url, tls_support_cache)
        expected = "'https://flickr.com'"

        bad_http = "neverssl.com"
        result_http = CleanupFunctions.cleanup_url(bad_http, tls_support_cache)
        expected_http = "'http://neverssl.com'"
        assert result == expected
        assert result_http == expected_http

    @staticmethod
    def test_rank_feature_verify():
        img = create_mock_image({"standardized_popularity": 200})
        assert img.standardized_popularity == 100
        img2 = create_mock_image({"standardized_popularity": 0})
        assert img2.standardized_popularity is None

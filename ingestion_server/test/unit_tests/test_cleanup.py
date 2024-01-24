from unittest.mock import MagicMock

from psycopg2._json import Json

from ingestion_server.cleanup import CleanupFunctions, TlsTest
from test.unit_tests.conftest import create_mock_image


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
        TlsTest.test_tls_supported = MagicMock(return_value=False)
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

import json
import os
import unittest
from unittest.mock import call, patch

from common.storage.audio import AudioStore, MockAudioStore
from common.storage.image import ImageStore, MockImageStore

from tests.dags.providers.provider_api_scripts.resources.provider_data_ingester.mock_provider_data_ingester import (
    AUDIO_PROVIDER,
    EXPECTED_BATCH_DATA,
    IMAGE_PROVIDER,
    MOCK_RECORD_DATA_LIST,
    MockProviderDataIngester,
)


RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "resources/provider_data_ingester"
)


class TestProviderDataIngester(unittest.TestCase):
    def setUp(self):
        self.ingester = MockProviderDataIngester()

        # Use mock media stores
        self.audio_store = MockAudioStore(AUDIO_PROVIDER)
        self.image_store = MockImageStore(IMAGE_PROVIDER)
        self.ingester.media_stores = {
            "audio": self.audio_store,
            "image": self.image_store,
        }

    def _get_resource_json(self, json_name):
        with open(os.path.join(RESOURCES, json_name)) as f:
            resource_json = json.load(f)
        return resource_json

    def test_init_media_stores(self):
        ingester = MockProviderDataIngester()

        # We should have two media stores, with the correct types
        assert len(ingester.media_stores) == 2
        assert isinstance(ingester.media_stores["audio"], AudioStore)
        assert isinstance(ingester.media_stores["image"], ImageStore)

    def test_init_with_date(self):
        ingester = MockProviderDataIngester(date="2020-06-27")
        assert ingester.date == "2020-06-27"

    def test_init_without_date(self):
        ingester = MockProviderDataIngester()
        assert ingester.date is None

    def test_batch_limit_is_capped_to_ingestion_limit(self):
        with patch(
            "providers.provider_api_scripts.provider_data_ingester.Variable"
        ) as MockVariable:
            MockVariable.get.side_effect = [20]

            ingester = MockProviderDataIngester()
            assert ingester.batch_limit == 20
            assert ingester.limit == 20

    def test_get_batch_data(self):
        response_json = self._get_resource_json("complete_response.json")
        batch = self.ingester.get_batch_data(response_json)

        assert batch == EXPECTED_BATCH_DATA

    def test_process_batch_adds_items_to_correct_media_stores(self):
        with (
            patch.object(self.audio_store, "add_item") as audio_store_mock,
            patch.object(self.image_store, "add_item") as image_store_mock,
        ):
            record_count = self.ingester.process_batch(EXPECTED_BATCH_DATA)

            assert record_count == 3
            assert audio_store_mock.call_count == 1
            assert image_store_mock.call_count == 2

    def test_process_batch_handles_list_of_records(self):
        with (
            patch.object(self.audio_store, "add_item") as audio_store_mock,
            patch.object(self.image_store, "add_item") as image_store_mock,
            patch.object(self.ingester, "get_record_data") as get_record_data_mock,
        ):
            # Mock `get_record_data` to return a list of records
            get_record_data_mock.return_value = MOCK_RECORD_DATA_LIST

            record_count = self.ingester.process_batch(EXPECTED_BATCH_DATA[:1])

            # Both records are added, and to the appropriate stores
            assert record_count == 2
            assert audio_store_mock.call_count == 1
            assert image_store_mock.call_count == 1

    def test_ingest_records(self):
        with (
            patch.object(self.ingester, "get_batch") as get_batch_mock,
            patch.object(
                self.ingester, "process_batch", return_value=3
            ) as process_batch_mock,
            patch.object(self.ingester, "commit_records") as commit_mock,
        ):
            get_batch_mock.side_effect = [
                (EXPECTED_BATCH_DATA, True),  # First batch
                (EXPECTED_BATCH_DATA, True),  # Second batch
                (None, True),  # Final batch
            ]

            self.ingester.ingest_records()

            # get_batch is not called again after getting None
            assert get_batch_mock.call_count == 3

            # process_batch is called for each batch
            process_batch_mock.assert_has_calls(
                [
                    call(EXPECTED_BATCH_DATA),
                    call(EXPECTED_BATCH_DATA),
                ]
            )
            # process_batch is not called for a third time with None
            assert process_batch_mock.call_count == 2

            assert commit_mock.called

    def test_ingest_records_halts_ingestion_when_should_continue_is_false(self):
        with (
            patch.object(self.ingester, "get_batch") as get_batch_mock,
            patch.object(
                self.ingester, "process_batch", return_value=3
            ) as process_batch_mock,
        ):
            get_batch_mock.side_effect = [
                (EXPECTED_BATCH_DATA, False),  # First batch, should_continue is False
            ]

            self.ingester.ingest_records()

            # get_batch is not called a second time
            assert get_batch_mock.call_count == 1

            assert process_batch_mock.call_count == 1
            process_batch_mock.assert_has_calls(
                [
                    call(EXPECTED_BATCH_DATA),
                ]
            )

    def test_ingest_records_does_not_process_empty_batch(self):
        with (
            patch.object(self.ingester, "get_batch") as get_batch_mock,
            patch.object(
                self.ingester, "process_batch", return_value=3
            ) as process_batch_mock,
        ):
            get_batch_mock.side_effect = [
                ([], True),  # Empty batch
            ]

            self.ingester.ingest_records()

            # get_batch is not called a second time
            assert get_batch_mock.call_count == 1
            # process_batch is not called with an empty batch
            assert not process_batch_mock.called

    def test_ingest_records_stops_after_reaching_limit(self):
        # Set the ingestion limit for the test to one batch
        with patch(
            "providers.provider_api_scripts.provider_data_ingester.Variable"
        ) as MockVariable:
            # Mock the calls to Variable.get, in order
            MockVariable.get.side_effect = [3]

            ingester = MockProviderDataIngester()

            with (
                patch.object(ingester, "get_batch") as get_batch_mock,
                patch.object(
                    ingester, "process_batch", return_value=3
                ) as process_batch_mock,
            ):
                get_batch_mock.side_effect = [
                    (EXPECTED_BATCH_DATA, True),  # First batch
                    (EXPECTED_BATCH_DATA, True),  # Second batch
                    (None, True),  # Final batch
                ]

                ingester.ingest_records()

                # get_batch is not called again after the first batch
                assert get_batch_mock.call_count == 1
                assert process_batch_mock.call_count == 1

    def test_commit_commits_all_stores(self):
        with (
            patch.object(self.audio_store, "commit") as audio_store_mock,
            patch.object(self.image_store, "commit") as image_store_mock,
        ):
            self.ingester.commit_records()

            assert audio_store_mock.called
            assert image_store_mock.called

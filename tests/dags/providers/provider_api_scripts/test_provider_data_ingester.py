import json
import os
from unittest.mock import MagicMock, call, patch

import pytest
import requests
from airflow.exceptions import AirflowException
from common.requester import RetriesExceeded
from common.storage.audio import AudioStore, MockAudioStore
from common.storage.image import ImageStore, MockImageStore
from providers.provider_api_scripts.provider_data_ingester import (
    AggregateIngestionError,
)

from tests.dags.providers.provider_api_scripts.resources.provider_data_ingester.mock_provider_data_ingester import (
    AUDIO_PROVIDER,
    EXPECTED_BATCH_DATA,
    IMAGE_PROVIDER,
    MOCK_RECORD_DATA_LIST,
    IncorrectlyConfiguredMockProviderDataIngester,
    MockAudioOnlyProviderDataIngester,
    MockImageOnlyProviderDataIngester,
    MockProviderDataIngester,
)


RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "resources/provider_data_ingester"
)

ingester = MockProviderDataIngester()
image_ingester = MockImageOnlyProviderDataIngester()
audio_ingester = MockAudioOnlyProviderDataIngester()
misconfigured_ingester = IncorrectlyConfiguredMockProviderDataIngester()
audio_store = MockAudioStore(AUDIO_PROVIDER)
image_store = MockImageStore(IMAGE_PROVIDER)
ingester.media_stores = {"audio": audio_store, "image": image_store}


def _get_resource_json(json_name):
    with open(os.path.join(RESOURCES, json_name)) as f:
        resource_json = json.load(f)
    return resource_json


def test_init_media_stores():
    ingester = MockProviderDataIngester()

    # We should have two media stores, with the correct types
    assert len(ingester.media_stores) == 2
    assert isinstance(ingester.media_stores["audio"], AudioStore)
    assert isinstance(ingester.media_stores["image"], ImageStore)


def test_init_with_date():
    ingester = MockProviderDataIngester(date="2020-06-27")
    assert ingester.date == "2020-06-27"


def test_init_without_date():
    ingester = MockProviderDataIngester()
    assert ingester.date is None


@pytest.mark.parametrize(
    "endpoint, expected",
    [
        (None, MockProviderDataIngester.endpoint),
        ("https://fake-endpoint.biz", "https://fake-endpoint.biz"),
    ],
)
def test_get_response_json(endpoint, expected):
    ingester = MockProviderDataIngester()
    with patch.object(ingester.delayed_requester, "get_response_json") as mock_get:
        ingester.get_response_json({}, endpoint=endpoint)
        actual_endpoint = mock_get.call_args.args[0]
        assert actual_endpoint == expected


def test_batch_limit_is_capped_to_ingestion_limit():
    with patch(
        "providers.provider_api_scripts.provider_data_ingester.Variable"
    ) as MockVariable:
        MockVariable.get.side_effect = [20]

        ingester = MockProviderDataIngester()
        assert ingester.batch_limit == 20
        assert ingester.limit == 20


def test_get_batch_data():
    response_json = _get_resource_json("complete_response.json")
    batch = ingester.get_batch_data(response_json)

    assert batch == EXPECTED_BATCH_DATA


def test_get_batch_raises_error():
    r = requests.Response()
    r.status_code = 500
    r.json = MagicMock(return_value={"error": ""})
    with (
        patch.object(ingester.delayed_requester, "get", return_value=r),
        pytest.raises(RetriesExceeded),
    ):
        ingester.get_batch({})


def test_process_batch_adds_items_to_correct_media_stores():
    with (
        patch.object(audio_store, "add_item") as audio_store_mock,
        patch.object(image_store, "add_item") as image_store_mock,
    ):
        record_count = ingester.process_batch(EXPECTED_BATCH_DATA)

        assert record_count == 3
        assert audio_store_mock.call_count == 1
        assert image_store_mock.call_count == 2


def test_process_batch_handles_list_of_records():
    with (
        patch.object(audio_store, "add_item") as audio_store_mock,
        patch.object(image_store, "add_item") as image_store_mock,
        patch.object(ingester, "get_record_data") as get_record_data_mock,
    ):
        # Mock `get_record_data` to return a list of records
        get_record_data_mock.return_value = MOCK_RECORD_DATA_LIST

        record_count = ingester.process_batch(EXPECTED_BATCH_DATA[:1])

        # Both records are added, and to the appropriate stores
        assert record_count == 2
        assert audio_store_mock.call_count == 1
        assert image_store_mock.call_count == 1


def test_process_batch_halts_processing_after_reaching_ingestion_limit():
    # Set up an ingester with an ingestion limit of 1
    ingester = MockProviderDataIngester()
    ingester.limit = 1

    with (
        patch.object(audio_store, "add_item"),
        patch.object(image_store, "add_item"),
        patch.object(ingester, "get_record_data") as get_record_data_mock,
    ):

        # Mock `get_record_data` to return a list of 2 records
        get_record_data_mock.return_value = MOCK_RECORD_DATA_LIST
        record_count = ingester.process_batch(EXPECTED_BATCH_DATA)

        # Only the first record was added, and then ingestion stopped
        assert record_count == 1


def test_ingest_records():
    with (
        patch.object(ingester, "get_batch") as get_batch_mock,
        patch.object(ingester, "process_batch", return_value=3) as process_batch_mock,
        patch.object(ingester, "_commit_records") as commit_mock,
    ):
        get_batch_mock.side_effect = [
            (EXPECTED_BATCH_DATA, True),  # First batch
            (EXPECTED_BATCH_DATA, True),  # Second batch
            (None, True),  # Final batch
        ]

        ingester.ingest_records()

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


def test_ingest_records_halts_ingestion_when_should_continue_is_false():
    with (
        patch.object(ingester, "get_batch") as get_batch_mock,
        patch.object(ingester, "process_batch", return_value=3) as process_batch_mock,
    ):
        get_batch_mock.side_effect = [
            (EXPECTED_BATCH_DATA, False),  # First batch, should_continue is False
        ]

        ingester.ingest_records()

        # get_batch is not called a second time
        assert get_batch_mock.call_count == 1

        assert process_batch_mock.call_count == 1
        process_batch_mock.assert_has_calls(
            [
                call(EXPECTED_BATCH_DATA),
            ]
        )


def test_ingest_records_does_not_process_empty_batch():
    with (
        patch.object(ingester, "get_batch") as get_batch_mock,
        patch.object(ingester, "process_batch", return_value=3) as process_batch_mock,
    ):
        get_batch_mock.side_effect = [
            ([], True),  # Empty batch
        ]

        ingester.ingest_records()

        # get_batch is not called a second time
        assert get_batch_mock.call_count == 1
        # process_batch is not called with an empty batch
        assert not process_batch_mock.called


def test_ingest_records_stops_after_reaching_limit():
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


def test_ingest_records_commits_on_exception():
    with (
        patch.object(ingester, "get_batch") as get_batch_mock,
        patch.object(ingester, "process_batch", return_value=3) as process_batch_mock,
        patch.object(ingester, "_commit_records") as commit_mock,
    ):
        get_batch_mock.side_effect = [
            (EXPECTED_BATCH_DATA, True),  # First batch
            (EXPECTED_BATCH_DATA, True),  # Second batch
            ValueError("Whoops :C"),  # Problem batch
            (EXPECTED_BATCH_DATA, True),  # Fourth batch, should not be reached
        ]

        with pytest.raises(ValueError, match="Whoops :C"):
            ingester.ingest_records()

        # Check that get batch was only called thrice
        assert get_batch_mock.call_count == 3

        # process_batch is called for each successful batch
        process_batch_mock.assert_has_calls(
            [
                call(EXPECTED_BATCH_DATA),
                call(EXPECTED_BATCH_DATA),
            ]
        )
        # process_batch is not called for a third time with exception
        assert process_batch_mock.call_count == 2

        # Even with the exception, records were still saved
        assert commit_mock.called


def test_ingest_records_uses_initial_query_params_from_dagrun_conf():
    # Initialize the ingester with a conf
    ingester = MockProviderDataIngester(
        {"initial_query_params": {"has_image": 1, "page": 5}}
    )

    # Mock get_batch to halt ingestion after a single batch
    with (
        patch.object(ingester, "get_batch", return_value=([], False)) as get_batch_mock,
    ):
        ingester.ingest_records()

        # get_batch is called with the query_params supplied in the conf
        get_batch_mock.assert_called_with({"has_image": 1, "page": 5})


def test_ingest_records_uses_query_params_list_from_dagrun_conf():
    # Initialize the ingester with a conf
    ingester = MockProviderDataIngester(
        {
            "query_params_list": [
                {"has_image": 1, "page": 5},
                {"has_image": 1, "page": 12},
                {"has_image": 1, "page": 142},
            ]
        }
    )

    with (
        patch.object(
            ingester, "get_batch", return_value=(EXPECTED_BATCH_DATA, True)
        ) as get_batch_mock,
        patch.object(ingester, "process_batch", return_value=3),
    ):
        ingester.ingest_records()

        # get_batch is called only three times, for each set of query_params
        # in the list, even though `should_continue` is still True
        assert get_batch_mock.call_count == 3
        get_batch_mock.assert_has_calls(
            [
                call({"has_image": 1, "page": 5}),
                call({"has_image": 1, "page": 12}),
                call({"has_image": 1, "page": 142}),
            ]
        )


def test_ingest_records_raises_IngestionError():
    with (patch.object(ingester, "get_batch") as get_batch_mock,):
        get_batch_mock.side_effect = [
            Exception("Mock exception message"),
            (EXPECTED_BATCH_DATA, True),  # Second batch should not be reached
        ]

        with pytest.raises(Exception, match="Mock exception message"):
            ingester.ingest_records()

        # By default, `skip_ingestion_errors` is False and get_batch_data
        # is no longer called after encountering an error
        assert get_batch_mock.call_count == 1


@pytest.mark.parametrize(
    "batches, expected_call_count, expected_error",
    [
        # Multiple errors are skipped
        (
            [
                Exception("Mock exception 1"),
                (EXPECTED_BATCH_DATA, True),  # First error
                Exception("Mock exception 2"),
                (EXPECTED_BATCH_DATA, False),  # Second error, `should_continue` False
            ],
            4,  # get_batch is called until `should_continue` is False, ignoring errors
            AggregateIngestionError,
        ),
        # An AirflowException should not be skipped
        (
            [
                (EXPECTED_BATCH_DATA, True),
                AirflowException("An Airflow exception"),  # Second batch, should raise
                (EXPECTED_BATCH_DATA, True),  # This batch should not be reached
            ],
            2,  # The final batch should not be reached
            AirflowException,
        ),
        # An AirflowException is raised, but there were already other ingestion errors
        (
            [
                Exception("Some other exception"),  # First batch, should be skipped
                AirflowException("An Airflow exception"),  # Second batch, should raise
                (EXPECTED_BATCH_DATA, True),  # This batch should not be reached
            ],
            2,  # The final batch should not be reached
            AggregateIngestionError,  # Ingestion errors reported
        ),
    ],
)
def test_ingest_records_with_skip_ingestion_errors(
    batches, expected_call_count, expected_error
):
    ingester = MockProviderDataIngester({"skip_ingestion_errors": True})

    with (
        patch.object(ingester, "get_batch") as get_batch_mock,
        patch.object(ingester, "process_batch", return_value=10),
    ):
        get_batch_mock.side_effect = batches

        # ingest_records ultimately raises an exception
        with pytest.raises(expected_error):
            ingester.ingest_records()

        # get_batch was called four times before the exception was thrown,
        # despite errors being raised
        assert get_batch_mock.call_count == expected_call_count


def test_ingest_records_exits_immediately_if_limit_already_reached():
    # A child class may override `ingest_records` to run multiple times.
    # Once the ingestion limit has been reached, subsequent calls to
    # `ingest_records` should immediately return without attempting to
    # ingest new data.
    with patch(
        "providers.provider_api_scripts.provider_data_ingester.Variable"
    ) as MockVariable:
        # Mock the calls to Variable.get to set an ingestion limit
        MockVariable.get.side_effect = [5]

        ingester = MockProviderDataIngester()

        # Mock batch processing to reach the ingestion limit
        with (
            patch.object(ingester, "get_batch") as get_batch_mock,
            patch.object(
                ingester, "process_batch", return_value=5
            ) as process_batch_mock,
        ):
            get_batch_mock.side_effect = [
                (EXPECTED_BATCH_DATA, True),  # First batch
                (EXPECTED_BATCH_DATA, True),  # Second batch
            ]

            ingester.ingest_records()

            # get_batch was only called once, and then the limit was reached
            assert get_batch_mock.call_count == 1
            assert process_batch_mock.call_count == 1

            # Ingest records again
            ingester.ingest_records()

            # get_batch was not called any additional times
            assert get_batch_mock.call_count == 1
            assert process_batch_mock.call_count == 1


def test_commit_commits_all_stores():
    with (
        patch.object(audio_store, "commit") as audio_store_mock,
        patch.object(image_store, "commit") as image_store_mock,
    ):
        ingester._commit_records()

        assert audio_store_mock.called
        assert image_store_mock.called


def test_get_media_type_default_behaviour_multiple_media_types_fails():
    with pytest.raises(NotImplementedError):
        misconfigured_ingester.get_media_type({})


def test_get_media_type_default_behaviour_image_only_provider():
    assert image_ingester.get_media_type({}) == "image"


def test_get_media_type_default_behaviour_audio_only_provider():
    assert audio_ingester.get_media_type({}) == "audio"

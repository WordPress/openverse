from datetime import datetime, timedelta, timezone
from itertools import repeat
from unittest.mock import MagicMock, call, patch

import pytest

from catalog.tests.dags.providers.provider_api_scripts.resources.provider_data_ingester.mock_provider_data_ingester import (
    MAX_RECORDS,
    MockTimeDelineatedProviderDataIngester,
)


FROZEN_DATE = "2020-04-01"
ingester = MockTimeDelineatedProviderDataIngester(date=FROZEN_DATE)


def test_raises_error_when_date_is_undefined():
    expected_error = (
        "TimeDelineatedProviderDataIngester should only be used for dated DAGs."
    )
    with pytest.raises(ValueError, match=expected_error):
        # Attempt to initialize without a date
        MockTimeDelineatedProviderDataIngester()


@pytest.mark.parametrize(
    "num_divisions, expected_pairs",
    [
        # One division
        (1, [(datetime(2020, 4, 1, 1, 0), datetime(2020, 4, 1, 2, 0))]),
        # Two divisions divides into 30 min increments
        (
            2,
            [
                (datetime(2020, 4, 1, 1, 0), datetime(2020, 4, 1, 1, 30)),
                (datetime(2020, 4, 1, 1, 30), datetime(2020, 4, 1, 2, 0)),
            ],
        ),
        # 8 divisions divides into 7.5 min increments
        (
            8,
            [
                (datetime(2020, 4, 1, 1, 0, 0), datetime(2020, 4, 1, 1, 7, 30)),
                (datetime(2020, 4, 1, 1, 7, 30), datetime(2020, 4, 1, 1, 15, 0)),
                (datetime(2020, 4, 1, 1, 15, 0), datetime(2020, 4, 1, 1, 22, 30)),
                (datetime(2020, 4, 1, 1, 22, 30), datetime(2020, 4, 1, 1, 30, 0)),
                (datetime(2020, 4, 1, 1, 30, 0), datetime(2020, 4, 1, 1, 37, 30)),
                (datetime(2020, 4, 1, 1, 37, 30), datetime(2020, 4, 1, 1, 45, 0)),
                (datetime(2020, 4, 1, 1, 45, 0), datetime(2020, 4, 1, 1, 52, 30)),
                (datetime(2020, 4, 1, 1, 52, 30), datetime(2020, 4, 1, 2, 0, 0)),
            ],
        ),
        # 7 does not divide evenly into 60, so error is raised
        pytest.param(7, None, marks=pytest.mark.raises(exception=ValueError)),
    ],
)
def test_get_timestamp_query_params_list(num_divisions, expected_pairs):
    # Hour long time slice
    start_date = datetime(2020, 4, 1, 1, 0)
    end_date = datetime(2020, 4, 1, 2, 0)

    actual_pairs = ingester._get_timestamp_query_params_list(
        start_date, end_date, num_divisions
    )
    assert actual_pairs == expected_pairs


def test_get_timestamp_pairs_returns_empty_list_when_no_records_found():
    # mock _get_record_count to return 0 records
    with patch.object(ingester, "_get_record_count", return_value=0):
        actual_pairs_list = ingester._get_timestamp_pairs()

        assert len(actual_pairs_list) == 0


def test_get_timestamp_pairs_returns_full_day_when_few_records_found():
    # When < max_records are found for the day, we should get back a single
    # timestamp pair representing the whole day
    expected_pairs_list = [
        (
            datetime(2020, 4, 1, 0, 0, tzinfo=timezone.utc),
            datetime(2020, 4, 2, 0, 0, tzinfo=timezone.utc),
        )
    ]

    with patch.object(ingester, "_get_record_count", return_value=MAX_RECORDS - 1):
        actual_pairs_list = ingester._get_timestamp_pairs()
        assert actual_pairs_list == expected_pairs_list


def test_get_timestamp_pairs_with_large_record_counts():
    with patch.object(ingester, "_get_record_count") as mock_count:
        # Mock the calls to _get_record_count in order
        mock_count.side_effect = (
            [
                150_000,  # Getting total count for the entire day
                0,  # Get count for first hour, count == 0
                10,  # Get count for second hour, count < max_records
                101_000,  # Get count for third hour, count > division_threshold
                49_090,  # Get count for fourth hour, max_records < count < division_threshold
            ]
            + list(repeat(0, 20))
        )  # Fill list with count == 0 for the remaining hours

        # We only get timestamp pairs for the hours that had records. For the
        # hour with > 100k records, we get 20 3-min pairs. For the hour with
        # < 100k records, we get 12 5-min pairs.
        expected_pairs_list = [
            # Single intervals for second hour
            ("2020-04-01T01:00:00Z", "2020-04-01T02:00:00Z"),
            # 20 3-min intervals across the third hour
            ("2020-04-01T02:00:00Z", "2020-04-01T02:03:00Z"),
            ("2020-04-01T02:03:00Z", "2020-04-01T02:06:00Z"),
            ("2020-04-01T02:06:00Z", "2020-04-01T02:09:00Z"),
            ("2020-04-01T02:09:00Z", "2020-04-01T02:12:00Z"),
            ("2020-04-01T02:12:00Z", "2020-04-01T02:15:00Z"),
            ("2020-04-01T02:15:00Z", "2020-04-01T02:18:00Z"),
            ("2020-04-01T02:18:00Z", "2020-04-01T02:21:00Z"),
            ("2020-04-01T02:21:00Z", "2020-04-01T02:24:00Z"),
            ("2020-04-01T02:24:00Z", "2020-04-01T02:27:00Z"),
            ("2020-04-01T02:27:00Z", "2020-04-01T02:30:00Z"),
            ("2020-04-01T02:30:00Z", "2020-04-01T02:33:00Z"),
            ("2020-04-01T02:33:00Z", "2020-04-01T02:36:00Z"),
            ("2020-04-01T02:36:00Z", "2020-04-01T02:39:00Z"),
            ("2020-04-01T02:39:00Z", "2020-04-01T02:42:00Z"),
            ("2020-04-01T02:42:00Z", "2020-04-01T02:45:00Z"),
            ("2020-04-01T02:45:00Z", "2020-04-01T02:48:00Z"),
            ("2020-04-01T02:48:00Z", "2020-04-01T02:51:00Z"),
            ("2020-04-01T02:51:00Z", "2020-04-01T02:54:00Z"),
            ("2020-04-01T02:54:00Z", "2020-04-01T02:57:00Z"),
            ("2020-04-01T02:57:00Z", "2020-04-01T03:00:00Z"),
            # 12 5-min intervals across the fourth hour
            ("2020-04-01T03:00:00Z", "2020-04-01T03:05:00Z"),
            ("2020-04-01T03:05:00Z", "2020-04-01T03:10:00Z"),
            ("2020-04-01T03:10:00Z", "2020-04-01T03:15:00Z"),
            ("2020-04-01T03:15:00Z", "2020-04-01T03:20:00Z"),
            ("2020-04-01T03:20:00Z", "2020-04-01T03:25:00Z"),
            ("2020-04-01T03:25:00Z", "2020-04-01T03:30:00Z"),
            ("2020-04-01T03:30:00Z", "2020-04-01T03:35:00Z"),
            ("2020-04-01T03:35:00Z", "2020-04-01T03:40:00Z"),
            ("2020-04-01T03:40:00Z", "2020-04-01T03:45:00Z"),
            ("2020-04-01T03:45:00Z", "2020-04-01T03:50:00Z"),
            ("2020-04-01T03:50:00Z", "2020-04-01T03:55:00Z"),
            ("2020-04-01T03:55:00Z", "2020-04-01T04:00:00Z"),
        ]

        actual_pairs_list = ingester._get_timestamp_pairs()
        # Formatting the timestamps so the test will be more readable
        formatted_actual_pairs_list = [
            (ingester.format_ts(x), ingester.format_ts(y)) for x, y in actual_pairs_list
        ]
        assert formatted_actual_pairs_list == expected_pairs_list


def test_ingest_records_calls_super_for_each_ts_pair():
    with (
        patch(
            "providers.provider_api_scripts.provider_data_ingester.ProviderDataIngester.ingest_records"
        ) as super_mock,
        patch.object(ingester, "_get_timestamp_pairs") as ts_mock,
    ):
        # Make some mock timestamp pairs
        start = datetime(2020, 4, 1, 11, 0, tzinfo=timezone.utc)
        ts_0 = (start, start + timedelta(hours=1))
        ts_1 = (start + timedelta(hours=1), start + timedelta(hours=2))
        ts_2 = (start + timedelta(hours=2), start + timedelta(hours=3))
        ts_mock.return_value = [ts_0, ts_1, ts_2]

        ingester.ingest_records(test_kwarg="test")

        # There should be a call to the super `ingest_records` for each set of pairs,
        # with the timestamps passed through as kwargs along with any other kwargs
        assert super_mock.call_count == 3
        super_mock.assert_has_calls(
            [
                call(start_ts=ts_0[0], end_ts=ts_0[1], test_kwarg="test"),
                call(start_ts=ts_1[0], end_ts=ts_1[1], test_kwarg="test"),
                call(start_ts=ts_2[0], end_ts=ts_2[1], test_kwarg="test"),
            ]
        )


def test_ts_pairs_and_kwargs_are_available_in_get_next_query_params():
    with (
        patch.object(ingester, "_get_timestamp_pairs") as ts_mock,
        patch.object(ingester, "get_batch", return_value=([], False)),
    ):
        mock_start = datetime(2020, 4, 1, 11, 0, tzinfo=timezone.utc)
        mock_end = mock_start + timedelta(hours=1)
        ts_mock.return_value = [(mock_start, mock_end)]

        # Spy on get_next_query_params
        ingester.get_next_query_params = MagicMock(
            side_effect=ingester.get_next_query_params
        )

        ingester.ingest_records(foo="foo", bar="bar")

        # When get_next_query_params is called, the start and end timestamps
        # are passed in as kwargs *in addition to any other kwargs passed to
        # ingest_records*
        assert ingester.get_next_query_params.called_with(
            start_ts=mock_start, end_ts=mock_end, foo="foo", bar="bar"
        )


def test_ingest_records_raises_error_if_the_total_count_has_been_exceeded():
    # Test that `ingest_records` raises an Exception if the external
    # API continues returning data in excess of the stated `resultCount`
    # (https://github.com/WordPress/openverse-catalog/pull/934)
    with (
        patch.object(ingester, "_get_timestamp_pairs") as ts_mock,
        patch.object(ingester, "get_batch_data") as get_mock,
        patch.object(ingester, "get_record_count_from_response") as count_mock,
        patch.object(ingester, "process_batch", return_value=2) as process_mock,
        patch.object(ingester, "get_response_json", return_value={MagicMock()}),
    ):
        ts_mock.return_value = [
            (
                datetime(2020, 4, 1, 11, 0, tzinfo=timezone.utc),
                datetime(2020, 4, 1, 12, 0, tzinfo=timezone.utc),
            ),
        ]

        # Mock the API response to indicate that the total result count is 2
        count_mock.return_value = 2

        # Each time get_response_json is called, it will return json containing
        # 2 records. After two calls, this will exceed the expected total count.
        get_mock.return_value = {
            "status": "ok",
            "records": [MagicMock(), MagicMock()],  # Two mock records,
        }

        expected_error_string = (
            "Expected 2 records, but 4 have been fetched. Consider reducing the ingestion"
            " interval."
        )
        # Assert that attempting to ingest records raises an exception when
        # `should_raise_error` is enabled
        with pytest.raises(Exception, match=expected_error_string):
            ingester.ingest_records()

        # get_mock should have been called 4 times, twice for each batch (once in `get_batch`
        # and a second time in `get_should_continue`). Each time, it returned 2 'new' records,
        # even though the resultCount indicated there should only be 2 records total.
        assert get_mock.call_count == 4
        # process_mock should only have been called once. We raise an error when getting the
        # second batch as soon as it is detected that we've processed too many records.
        assert process_mock.call_count == 1


def test_ingest_records_does_not_raise_when_should_raise_error_is_false():
    # Test that no error is raised when we keep receiving data in excess of the
    # stated resultCount, if `should_raise_error` is explicitly disabled.
    ingester = MockTimeDelineatedProviderDataIngester(date=FROZEN_DATE)
    ingester.should_raise_error = False

    with (
        patch.object(ingester, "_get_timestamp_pairs") as ts_mock,
        patch.object(ingester, "get_batch_data") as get_mock,
        patch.object(ingester, "get_record_count_from_response") as count_mock,
        patch.object(ingester, "process_batch", return_value=2) as process_mock,
        patch.object(ingester, "get_response_json", return_value={MagicMock()}),
    ):
        ts_mock.return_value = [
            (
                datetime(2020, 4, 1, 11, 0, tzinfo=timezone.utc),
                datetime(2020, 4, 1, 12, 0, tzinfo=timezone.utc),
            ),
        ]

        # Mock the API response to indicate that the total result count is 2
        count_mock.return_value = 2

        mock_response = {
            "status": "ok",
            "records": [MagicMock(), MagicMock()],  # Two mock records,
        }
        # Mock the calls to get_batch_data in order. For each batch, it is
        # called once to get the batch data, and a second time in
        # `get_should_continue`.
        get_mock.side_effect = [
            # Two calls for the first batch, which ingests 2 records
            mock_response,
            mock_response,
            # Two calls for the second batch, which ingests 2 more records.
            # We have now exceeded the count reported by the API
            mock_response,
            mock_response,
            # A third batch is requested even though the count is exceeded.
            # We make it an empty batch in order to halt ingestion
            None,
            None,
        ]

        ingester.ingest_records()

        # get_mock should have been called 6 times, for each of the calls described
        # above
        assert get_mock.call_count == 6
        # process_mock should only have been called twice, once for each non-empty batch.
        # We did not raise an error and allowed ingestion to continue.
        assert process_mock.call_count == 2

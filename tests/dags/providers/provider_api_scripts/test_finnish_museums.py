import json
import logging
import os
from datetime import datetime, timedelta, timezone
from itertools import repeat
from unittest.mock import MagicMock, patch

import pytest
from airflow.exceptions import AirflowException
from common.licenses import LicenseInfo
from common.loader import provider_details as prov
from common.storage.image import ImageStore
from providers.provider_api_scripts.finnish_museums import FinnishMuseumsDataIngester


RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "resources/finnishmuseums"
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.DEBUG
)

FROZEN_DATE = "2020-04-01"
FROZEN_UTC_DATE = datetime.strptime(FROZEN_DATE, "%Y-%m-%d").replace(
    tzinfo=timezone.utc
)
fm = FinnishMuseumsDataIngester(date=FROZEN_DATE)
image_store = ImageStore(provider=prov.FINNISH_DEFAULT_PROVIDER)
fm.media_stores = {"image": image_store}


def _get_resource_json(json_name):
    with open(os.path.join(RESOURCES, json_name)) as f:
        resource_json = json.load(f)
    return resource_json


@pytest.mark.parametrize(
    "response_json, expected_count",
    [
        # Happy path
        ({"resultCount": 20}, 20),
        # Defaults to 0
        (None, 0),
        ({}, 0),
    ],
)
def test_get_record_count(response_json, expected_count):
    with patch.object(fm, "get_response_json", return_value=response_json):
        actual_count = fm._get_record_count(
            datetime(2022, 4, 1), datetime(2022, 4, 2), "test_building"
        )
        assert actual_count == expected_count


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

    actual_pairs = fm._get_timestamp_query_params_list(
        start_date, end_date, num_divisions
    )
    assert actual_pairs == expected_pairs


def test_get_timestamp_pairs_returns_empty_list_when_no_records_found():
    # mock _get_record_count to return 0 records
    with patch.object(fm, "_get_record_count", return_value=0):
        actual_pairs_list = fm._get_timestamp_pairs("test_building")

        assert len(actual_pairs_list) == 0


def test_get_timestamp_pairs_returns_full_day_when_few_records_found():
    # When < 10_000 records are found for the day, we should get back a single
    # timestamp pair representing the whole day
    expected_pairs_list = [
        (
            datetime(2020, 4, 1, 0, 0, tzinfo=timezone.utc),
            datetime(2020, 4, 2, 0, 0, tzinfo=timezone.utc),
        )
    ]

    with patch.object(fm, "_get_record_count", return_value=9999):
        actual_pairs_list = fm._get_timestamp_pairs("test_building")
        assert actual_pairs_list == expected_pairs_list


def test_get_timestamp_pairs_with_large_record_counts():
    with patch.object(fm, "_get_record_count") as mock_count:
        # Mock the calls to _get_record_count in order
        mock_count.side_effect = [
            150_000,  # Getting total count for the entire day
            0,  # Get count for first hour, count == 0
            10,  # Get count for second hour, count < 10_000
            101_000,  # Get count for third hour, count > 100_000
            49_090,  # Get count for fourth hour, 10_000 < count < 100_000
        ] + list(
            repeat(0, 20)
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

        actual_pairs_list = fm._get_timestamp_pairs("test_building")
        # Formatting the timestamps so the test will be more readable
        formatted_actual_pairs_list = [
            (fm.format_ts(x), fm.format_ts(y)) for x, y in actual_pairs_list
        ]
        assert formatted_actual_pairs_list == expected_pairs_list


def test_ingest_records_raises_error_if_the_total_count_has_been_exceeded():
    # Test that `ingest_records` raises an AirflowException if the external
    # API continues returning data in excess of the stated `resultCount`
    # (https://github.com/WordPress/openverse-catalog/pull/934)
    fm = FinnishMuseumsDataIngester(date=FROZEN_DATE)
    fm.buildings = ["test_building"]

    with (
        patch.object(fm, "_get_timestamp_pairs") as ts_mock,
        patch.object(fm, "get_response_json") as get_mock,
        patch.object(fm, "process_batch", return_value=2) as process_mock,
    ):
        ts_mock.return_value = [
            (
                datetime(2020, 4, 1, 11, 0, tzinfo=timezone.utc),
                datetime(2020, 4, 1, 12, 0, tzinfo=timezone.utc),
            ),
        ]

        # Each time get_response_json is called, it will return json containing
        # 2 records, and a resultCount of 2
        get_mock.return_value = {
            "status": "ok",
            "records": [MagicMock(), MagicMock()],  # Two mock records,
            "resultCount": 2,  # Claim there are only two records total
        }

        expected_error_string = (
            "Expected 2 records, but 4 have been fetched. Consider reducing the ingestion"
            " interval."
        )
        # Assert that attempting to ingest records raises an exception
        with (pytest.raises(AirflowException, match=expected_error_string)):
            fm.ingest_records()

        # get_mock should have been called 2 times. Each time, it returned 2 'new' records,
        # even though the resultCount indicated there should only be 2 records total.
        assert get_mock.call_count == 2
        # process_mock should only have been called once. We raise an error when getting the
        # second batch as soon as it is detected that we've processed too many records.
        assert process_mock.call_count == 1


def test_build_query_param_default():
    actual_param_made = fm.get_next_query_params(
        None,
        building="0/Museovirasto/",
        start_ts=FROZEN_UTC_DATE,
        end_ts=FROZEN_UTC_DATE + timedelta(days=1),
    )
    expected_param = {
        "filter[]": [
            'format:"0/Image/"',
            'building:"0/Museovirasto/"',
            'last_indexed:"[2020-04-01T00:00:00Z TO 2020-04-02T00:00:00Z]"',
        ],
        "limit": 100,
        "page": 1,
    }
    assert actual_param_made == expected_param


def test_build_query_param_given():
    prev_query_params = {
        "filter[]": ['format:"0/Image/"', 'building:"0/Museovirasto/"'],
        "limit": 100,
        "page": 3,
    }
    actual_param_made = fm.get_next_query_params(prev_query_params)
    # Page is incremented
    expected_param = {
        "filter[]": ['format:"0/Image/"', 'building:"0/Museovirasto/"'],
        "limit": 100,
        "page": 4,
    }
    assert actual_param_made == expected_param


def test_get_object_list_from_json_returns_expected_output():
    json_resp = _get_resource_json("finna_full_response_example.json")
    actual_items_list = fm.get_batch_data(json_resp)
    expect_items_list = _get_resource_json("object_list_example.json")
    assert actual_items_list == expect_items_list


def test_get_object_list_return_none_if_empty():
    test_dict = {"records": []}
    assert fm.get_batch_data(test_dict) is None


def test_get_object_list_return_none_if_missing():
    test_dict = {}
    assert fm.get_batch_data(test_dict) is None


def test_get_object_list_return_none_if_none_json():
    assert fm.get_batch_data(None) is None


def test_process_object_with_real_example():
    object_data = _get_resource_json("object_complete_example.json")
    data = fm.get_record_data(object_data)

    assert len(data) == 1
    assert data[0] == {
        "license_info": LicenseInfo(
            "by",
            "4.0",
            "https://creativecommons.org/licenses/by/4.0/",
            "http://creativecommons.org/licenses/by/4.0/",
        ),
        "foreign_identifier": "museovirasto.CC0641BB5337F541CBD19169838BAC1F",
        "foreign_landing_url": (
            "https://www.finna.fi/Record/museovirasto.CC0641BB5337F541CBD19169838BAC1F"
        ),
        "image_url": (
            "https://api.finna.fi/Cover/Show?id=museovirasto.CC0641BB5337F541CBD19169838BAC1F&index=0&size=large"
        ),
        "title": "linnunpönttö koivussa",
        "source": "finnish_heritage_agency",
        "raw_tags": [
            "koivu",
            "koivussa",
            "linnunpöntöt",
            "Revonristi",
            "valmistusaika: 11.06.1923",
        ],
    }


def test_get_image_url():
    response_json = _get_resource_json("full_image_object.json")
    image_url = fm._get_image_url(response_json)
    expected_image_url = "https://api.finna.fi/Cover/Show?id=museovirasto.CC0641BB5337F541CBD19169838BAC1F&index=0&size=large"
    assert image_url == expected_image_url


@pytest.mark.parametrize(
    "image_rights_obj, expected_license_url",
    [
        ({}, None),
        (
            {
                "imageRights": {
                    "link": "http://creativecommons.org/licenses/by/4.0/deed.fi"
                }
            },
            "http://creativecommons.org/licenses/by/4.0/",
        ),
        (
            {"imageRights": {"link": "http://creativecommons.org/licenses/by/4.0/"}},
            "http://creativecommons.org/licenses/by/4.0/",
        ),
    ],
)
def test_get_license_url(image_rights_obj, expected_license_url):
    assert fm.get_license_url(image_rights_obj) == expected_license_url

import json
import logging
from unittest.mock import MagicMock, patch

import pytest
import requests
from tests.dags.providers.provider_api_scripts.resources.json_load import (
    make_resource_json_func,
)

from common.licenses import LicenseInfo
from providers.provider_api_scripts.metropolitan_museum import MetMuseumDataIngester


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

mma = MetMuseumDataIngester()


_get_resource_json = make_resource_json_func("metropolitan_museum_of_art")

# abbreviated response without other images 45733
single_object_response = _get_resource_json("sample_response_without_additional.json")
# single expected record if 45733 with no additional images
single_expected_data = _get_resource_json("sample_image_data.json")

# response for objectid 45734 with 2 additional image urls
full_object_response = _get_resource_json("sample_response.json")
# 3 expected image records for objectid 45734
full_expected_data = _get_resource_json("sample_additional_image_data.json")


CC0 = LicenseInfo(
    "cc0", "1.0", "https://creativecommons.org/publicdomain/zero/1.0/", None
)


@pytest.mark.parametrize(
    "test_date, expected",
    [
        pytest.param("2022-07-01", {"metadataDate": "2022-07-01"}, id="happy_path"),
        pytest.param(None, {}, id="None"),
        pytest.param("", {}, id="empty_string"),
    ],
)
def test_get_next_query_params(test_date, expected):
    ingester = MetMuseumDataIngester(date=test_date)
    actual = ingester.get_next_query_params()
    assert actual == expected


@pytest.mark.parametrize(
    "response_json, expected",
    [
        pytest.param(
            {"total": 4, "objectIDs": [153, 1578, 465, 546]},
            [153, 1578, 465, 546],
            id="happy_path",
        ),
        pytest.param({}, None, id="empty_dict"),
        pytest.param(None, None, id="None"),
    ],
)
def test_get_batch_data(response_json, expected):
    actual = mma.get_batch_data(response_json)
    assert actual == expected


@pytest.mark.parametrize(
    "response_json, expected",
    [
        pytest.param(
            single_object_response,
            single_expected_data[0].get("meta_data"),
            id="single_image",
        ),
        pytest.param(
            full_object_response,
            full_expected_data[0].get("meta_data"),
            id="full_object",
        ),
    ],
)
def test_get_meta_data(response_json, expected):
    actual = mma._get_meta_data(response_json)
    assert expected == actual


@pytest.mark.parametrize(
    "response_json, expected",
    [
        pytest.param(
            single_object_response,
            single_expected_data[0].get("raw_tags"),
            id="single_image",
        ),
        pytest.param(
            full_object_response,
            full_expected_data[0].get("raw_tags"),
            id="full_object",
        ),
    ],
)
def test_get_tag_list(response_json, expected):
    actual = mma._get_tag_list(response_json)
    assert expected == actual


@pytest.mark.parametrize(
    "response_json, expected",
    [
        pytest.param(
            {"title": "Yes, regular case", "objectName": "Wrong"},
            "Yes, regular case",
            id="happy_path",
        ),
        pytest.param(
            {"objectName": "Yes, no title at all"},
            "Yes, no title at all",
            id="no_title",
        ),
        pytest.param(
            {"title": "", "objectName": "Yes, empty title"},
            "Yes, empty title",
            id="empty_string_title",
        ),
    ],
)
def test_get_title(response_json, expected):
    actual = mma._get_title(response_json)
    assert actual == expected


@pytest.mark.parametrize(
    "response_json, expected",
    [
        pytest.param({}, None, id="empty_json"),
        pytest.param(
            {"artistDisplayName": "Unidentified flying obj"},
            "Unidentified flying obj",
            id="happy_path",
        ),
    ],
)
def test_get_artist_name(response_json, expected):
    actual = mma._get_artist_name(response_json)
    assert actual == expected


def test_get_record_data_with_none_response():
    with patch.object(mma.delayed_requester, "get", return_value=None) as mock_get:
        with pytest.raises(Exception):
            assert mma.get_record_data(10)
    assert mock_get.call_count == 6


def test_get_record_data_with_non_ok():
    r = requests.Response()
    r.status_code = 504
    r.json = MagicMock(return_value={})
    with patch.object(mma.delayed_requester, "get", return_value=r) as mock_get:
        with pytest.raises(Exception):
            assert mma.get_record_data(10)
    assert mock_get.call_count == 6


@pytest.mark.parametrize(
    "response_json, expected",
    [
        pytest.param(single_object_response, single_expected_data, id="single_image"),
        pytest.param(full_object_response, full_expected_data, id="full_object"),
        pytest.param(
            json.loads('{"isPublicDomain": false, "otherData": "is here too"}'),
            None,
            id="not_cc0",
        ),
        pytest.param(
            json.loads('{"otherData": "is here"}'),  # isPublicDomain missing
            None,
            id="missing_cc0_info",
        ),
        pytest.param(
            json.loads('{"isPublicDomain": false, "primaryImage": "test.com"}'),
            None,
            id="missing_foreign_landing_url",
        ),
        pytest.param(
            json.loads('{"isPublicDomain": false, "objectURL": ""}'),
            None,
            id="empty_string_for_foreign_landing_url",
        ),
        pytest.param(
            json.loads('{"isPublicDomain": true, "objectURL": "test.com"}'),
            None,
            id="missing_images",
        ),
        pytest.param(
            json.loads(
                '{"isPublicDomain": true, "objectURL": "test.com", "primaryImage": ""}'
            ),
            None,
            id="missing_url",
        ),
    ],
)
def test_get_record_data_returns_response_json_when_all_ok(
    response_json, expected, monkeypatch
):
    monkeypatch.setattr(
        mma.delayed_requester, "get_response_json", lambda x, y: response_json
    )
    actual = mma.get_record_data(response_json.get("objectID"))

    if expected is None:
        assert actual is None
    else:
        assert len(actual) == len(expected)
        for actual_result, expected_result in zip(actual, expected):
            for key, value in expected_result.items():
                if key == "license_info":
                    assert actual_result.get(key) == CC0
                else:
                    assert actual_result.get(key) == value

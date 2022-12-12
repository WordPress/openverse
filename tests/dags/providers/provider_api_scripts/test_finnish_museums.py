import json
import logging
import os

import pytest
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
fm = FinnishMuseumsDataIngester(date=FROZEN_DATE)
image_store = ImageStore(provider=prov.FINNISH_DEFAULT_PROVIDER)
fm.media_stores = {"image": image_store}


def _get_resource_json(json_name):
    with open(os.path.join(RESOURCES, json_name)) as f:
        resource_json = json.load(f)
    return resource_json


def test_get_timestamp_query_params_list():
    actual_list = fm._get_timestamp_query_params_list(FROZEN_DATE)
    # Expected timestamp list from splitting the FROZEN_DATE into 48 segments
    expected_list = [
        ("2020-04-01T00:00:00Z", "2020-04-01T00:30:00Z"),
        ("2020-04-01T00:30:00Z", "2020-04-01T01:00:00Z"),
        ("2020-04-01T01:00:00Z", "2020-04-01T01:30:00Z"),
        ("2020-04-01T01:30:00Z", "2020-04-01T02:00:00Z"),
        ("2020-04-01T02:00:00Z", "2020-04-01T02:30:00Z"),
        ("2020-04-01T02:30:00Z", "2020-04-01T03:00:00Z"),
        ("2020-04-01T03:00:00Z", "2020-04-01T03:30:00Z"),
        ("2020-04-01T03:30:00Z", "2020-04-01T04:00:00Z"),
        ("2020-04-01T04:00:00Z", "2020-04-01T04:30:00Z"),
        ("2020-04-01T04:30:00Z", "2020-04-01T05:00:00Z"),
        ("2020-04-01T05:00:00Z", "2020-04-01T05:30:00Z"),
        ("2020-04-01T05:30:00Z", "2020-04-01T06:00:00Z"),
        ("2020-04-01T06:00:00Z", "2020-04-01T06:30:00Z"),
        ("2020-04-01T06:30:00Z", "2020-04-01T07:00:00Z"),
        ("2020-04-01T07:00:00Z", "2020-04-01T07:30:00Z"),
        ("2020-04-01T07:30:00Z", "2020-04-01T08:00:00Z"),
        ("2020-04-01T08:00:00Z", "2020-04-01T08:30:00Z"),
        ("2020-04-01T08:30:00Z", "2020-04-01T09:00:00Z"),
        ("2020-04-01T09:00:00Z", "2020-04-01T09:30:00Z"),
        ("2020-04-01T09:30:00Z", "2020-04-01T10:00:00Z"),
        ("2020-04-01T10:00:00Z", "2020-04-01T10:30:00Z"),
        ("2020-04-01T10:30:00Z", "2020-04-01T11:00:00Z"),
        ("2020-04-01T11:00:00Z", "2020-04-01T11:30:00Z"),
        ("2020-04-01T11:30:00Z", "2020-04-01T12:00:00Z"),
        ("2020-04-01T12:00:00Z", "2020-04-01T12:30:00Z"),
        ("2020-04-01T12:30:00Z", "2020-04-01T13:00:00Z"),
        ("2020-04-01T13:00:00Z", "2020-04-01T13:30:00Z"),
        ("2020-04-01T13:30:00Z", "2020-04-01T14:00:00Z"),
        ("2020-04-01T14:00:00Z", "2020-04-01T14:30:00Z"),
        ("2020-04-01T14:30:00Z", "2020-04-01T15:00:00Z"),
        ("2020-04-01T15:00:00Z", "2020-04-01T15:30:00Z"),
        ("2020-04-01T15:30:00Z", "2020-04-01T16:00:00Z"),
        ("2020-04-01T16:00:00Z", "2020-04-01T16:30:00Z"),
        ("2020-04-01T16:30:00Z", "2020-04-01T17:00:00Z"),
        ("2020-04-01T17:00:00Z", "2020-04-01T17:30:00Z"),
        ("2020-04-01T17:30:00Z", "2020-04-01T18:00:00Z"),
        ("2020-04-01T18:00:00Z", "2020-04-01T18:30:00Z"),
        ("2020-04-01T18:30:00Z", "2020-04-01T19:00:00Z"),
        ("2020-04-01T19:00:00Z", "2020-04-01T19:30:00Z"),
        ("2020-04-01T19:30:00Z", "2020-04-01T20:00:00Z"),
        ("2020-04-01T20:00:00Z", "2020-04-01T20:30:00Z"),
        ("2020-04-01T20:30:00Z", "2020-04-01T21:00:00Z"),
        ("2020-04-01T21:00:00Z", "2020-04-01T21:30:00Z"),
        ("2020-04-01T21:30:00Z", "2020-04-01T22:00:00Z"),
        ("2020-04-01T22:00:00Z", "2020-04-01T22:30:00Z"),
        ("2020-04-01T22:30:00Z", "2020-04-01T23:00:00Z"),
        ("2020-04-01T23:00:00Z", "2020-04-01T23:30:00Z"),
        ("2020-04-01T23:30:00Z", "2020-04-02T00:00:00Z"),
    ]
    assert actual_list == expected_list


def test_build_query_param_default():
    actual_param_made = fm.get_next_query_params(
        None,
        building="0/Museovirasto/",
        start_ts="2020-04-01T00:30:00Z",
        end_ts="2020-04-01T01:00:00Z",
    )
    expected_param = {
        "filter[]": [
            'format:"0/Image/"',
            'building:"0/Museovirasto/"',
            'last_indexed:"[2020-04-01T00:30:00Z TO 2020-04-01T01:00:00Z]"',
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

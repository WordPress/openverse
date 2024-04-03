import logging
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from tests.dags.providers.provider_api_scripts.resources.json_load import (
    make_resource_json_func,
)

from common.licenses import LicenseInfo
from common.loader import provider_details as prov
from common.storage.image import ImageStore
from providers.provider_api_scripts.finnish_museums import FinnishMuseumsDataIngester


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


_get_resource_json = make_resource_json_func("finnishmuseums")


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
            datetime(2022, 4, 1), datetime(2022, 4, 2), building="test_building"
        )
        assert actual_count == expected_count


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
        "field[]": [
            "authors",
            "buildings",
            "id",
            "imageRights",
            "images",
            "subjects",
            "title",
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


@pytest.mark.parametrize(
    "response_json",
    [
        {"records": None},
        {"records": {}},
        {"records": ""},
        {"records": []},
        {"status": "OK"},
        None,
        {},
        [],
    ],
)
def test_get_object_list_returns_none_if_response_json_invalid(response_json):
    assert fm.get_batch_data(response_json) is None


def test_process_object_with_real_example():
    expected_data = {
        "license_info": LicenseInfo(
            "by",
            "4.0",
            "https://creativecommons.org/licenses/by/4.0/",
            "http://creativecommons.org/licenses/by/4.0/",
        ),
        "foreign_identifier": "sa-kuva.sa-kuva-1835",
        "foreign_landing_url": "https://www.finna.fi/Record/sa-kuva.sa-kuva-1835",
        "url": "https://api.finna.fi/Cover/Show?source=Solr&id=sa-kuva.sa-kuva-1835&index=0&size=large",
        "title": "Vuokkiniemen koulu",
        "source": "finnish_military_museum",
        "creator": "Uomala, valokuvaaja",
        "raw_tags": ["1942-03-02"],
    }
    object_data = _get_resource_json("object_complete_example.json")
    actual_data = fm.get_record_data(object_data)

    assert len(actual_data) == 1
    assert actual_data[0] == expected_data


def test_get_record_data_returns_none_without_license_info():
    object_data = _get_resource_json("object_complete_example.json")
    object_data["imageRights"]["link"] = ""

    actual_data = fm.get_record_data(object_data)

    assert actual_data is None


def test_get_image_url():
    response_json = _get_resource_json("full_image_object.json")
    image_url = fm._get_image_url(response_json)
    expected_image_url = "https://api.finna.fi/Cover/Show?id=museovirasto.CC0641BB5337F541CBD19169838BAC1F&index=0&size=large"
    assert image_url == expected_image_url


@pytest.mark.parametrize(
    "image_rights_obj, expected_license_url",
    [
        ({}, None),
        ({"imageRights": {"link": ""}}, None),
        (
            {
                "imageRights": {
                    "link": "http://creativecommons.org/licenses/by/4.0/deed.fi"
                }
            },
            "https://creativecommons.org/licenses/by/4.0/",
        ),
        (
            {"imageRights": {"link": "http://creativecommons.org/licenses/by/4.0/"}},
            "https://creativecommons.org/licenses/by/4.0/",
        ),
    ],
)
def test_get_license_url(image_rights_obj, expected_license_url):
    if expected_license_url is None:
        assert fm.get_license_info(image_rights_obj) is None
    else:
        assert fm.get_license_info(image_rights_obj).url == expected_license_url


@pytest.mark.parametrize(
    "authors_raw, expected_creator",
    [
        (
            {"primary": [], "secondary": [], "corporate": []},  # Case with no author
            None,
        ),
        (
            {  # Case with only a primary author
                "primary": {"Name": {"role": ["-"]}},
                "secondary": [],
                "corporate": [],
            },
            "Name",
        ),
        (
            {  # Case with only a secondary author
                "primary": [],
                "secondary": {"Name2": {"role": ["-"]}},
                "corporate": [],
            },
            "Name2",
        ),
        (
            {  # Case with primary and secondary authors
                "primary": {"Lastname, Name": {"role": ["-"]}},
                "secondary": {"Name2": {"role": ["-"]}},
                "corporate": [],
            },
            "Lastname, Name; Name2",
        ),
        (
            {  # Case with all the authors
                "primary": {"Name": {"role": ["-"]}},
                "secondary": {"Name2": {"role": ["-"]}},
                "corporate": {"Name3": {"role": ["-"]}},
            },
            "Name; Name2; Name3",
        ),
    ],
)
def test_get_creator(authors_raw, expected_creator):
    assert fm.get_creator(authors_raw) == expected_creator

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from common.licenses import LicenseInfo
from providers.provider_api_scripts.nypl import (
    NyplDataIngester,
    get_value_from_dict_or_list,
)


RESOURCES = Path(__file__).parent / "resources/nypl"
CC0 = LicenseInfo(
    license="cc0",
    version="1.0",
    url="https://creativecommons.org/publicdomain/zero/1.0/",
    raw_url="https://creativecommons.org/publicdomain/zero/1.0/",
)


@pytest.fixture(autouse=True)
def validate_url_string():
    with patch("common.urls.rewrite_redirected_url") as mock_validate_url_string:
        mock_validate_url_string.side_effect = lambda x: x
        yield


nypl = NyplDataIngester()
image_store = nypl.media_stores["image"]


def _get_resource_json(json_name):
    with open(RESOURCES / json_name) as f:
        resource_json = json.load(f)
        return resource_json


def test_get_next_query_params_default():
    actual_param = nypl.get_next_query_params({})
    expected_param = {"q": "CC_0", "field": "use_rtxt_s", "page": 1, "per_page": 500}
    assert actual_param == expected_param


def test_get_next_query_params_increments_offset():
    previous_query_params = {
        "q": "CC_0",
        "field": "use_rtxt_s",
        "page": 10,
        "per_page": 500,
    }

    actual_param = nypl.get_next_query_params(previous_query_params)
    expected_param = {"q": "CC_0", "field": "use_rtxt_s", "page": 11, "per_page": 500}
    assert actual_param == expected_param


def test_get_batch_data_success():
    response_search_success = _get_resource_json("response_search_success.json")
    actual_response = nypl.get_batch_data(response_search_success)

    assert len(actual_response) == 1


def test_get_batch_data_failure():
    response_search_failure = {}
    actual_response = nypl.get_batch_data(response_search_failure)

    assert actual_response is None


def test_get_creators_success():
    creatorinfo = _get_resource_json("creator_info_success.json")
    actual_creator = nypl._get_creators(creatorinfo)
    expected_creator = "Hillman, Barbara"

    assert actual_creator == expected_creator


def test_get_creators_failure():
    creatorinfo = []
    actual_creator = nypl._get_creators(creatorinfo)

    assert actual_creator is None


def test_get_metadata():
    item_response = _get_resource_json("response_itemdetails_success.json")
    mods = item_response.get("nyplAPI").get("response").get("mods")
    actual_metadata = nypl._get_metadata(mods)
    expected_metadata = _get_resource_json("metadata.json")

    assert actual_metadata == expected_metadata


def test_get_metadata_missing_attrs():
    item_response = _get_resource_json("response_itemdetails_success.json")
    mods = item_response.get("nyplAPI").get("response").get("mods")
    # Remove data to simulate it being missing
    mods["originInfo"].pop("dateIssued")
    mods["originInfo"].pop("publisher")
    mods["physicalDescription"].pop("note")
    # Remove data from expected values too
    expected_metadata = _get_resource_json("metadata.json")
    for attr in ["date_issued", "publisher", "physical_description"]:
        expected_metadata.pop(attr)

    actual_metadata = nypl._get_metadata(mods)

    assert actual_metadata == expected_metadata


def test_get_record_data_success():
    search_response = _get_resource_json("response_search_success.json")
    result = search_response["nyplAPI"]["response"]["result"][0]
    item_response = _get_resource_json("response_itemdetails_success.json")

    with patch.object(nypl, "get_response_json", return_value=item_response):
        images = nypl.get_record_data(result)
    assert len(images) == 7
    expected_image = {
        "category": None,
        "creator": "Hillman, Barbara",
        "filetype": "jpeg",
        "foreign_identifier": "56738462",
        "foreign_landing_url": "http://digitalcollections.nypl.org/items/0cabe3d0-3d50-0134-a8e0-00505686a51c",
        "image_url": "http://images.nypl.org/index.php?id=56738462&t=g&suffix=0cabe3d0-3d50-0134-a8e0-00505686a51c.001",
        "meta_data": {
            "date_issued": "1981",
            "genre": "Maps",
            "publisher": "New York Public Library, Local History and Genealogy Division",
            "tags": "Census districts",
            "type_of_resource": "cartographic",
            "physical_description": "4 polyester film encapsulations, some containing 2 sheets back-to-back. "
            "Accompanying text formatted as 1 large sheet (46 x 59 cm), in one of "
            "the encapsulations.",
        },
        "title": "1900 census enumeration districts, Manhattan and Bronx",
        "license_info": CC0,
    }
    assert images[0] == expected_image


def test_get_record_data_failure():
    search_response = _get_resource_json("response_search_success.json")
    result = search_response["nyplAPI"]["response"]["result"][0]

    item_response = None
    with patch.object(nypl, "get_response_json", return_value=item_response):
        images = nypl.get_record_data(result)
    assert images is None


@pytest.mark.parametrize(
    "dict_or_list, keys, expected",
    [
        ({"genre": None}, [], {"genre": None}),
        ({"genre": None}, ["$"], None),
        ([{"genre": None}], ["$"], None),
        (
            {
                "genre": {
                    "$": "Maps",
                    "authority": "lctgm",
                    "valueURI": "http://id.loc.gov/vocabulary/graphicMaterials/tgm006261",
                }
            },
            ["genre"],
            {
                "$": "Maps",
                "authority": "lctgm",
                "valueURI": "http://id.loc.gov/vocabulary/graphicMaterials/tgm006261",
            },
        ),
        (
            {
                "genre": {
                    "$": "Maps",
                    "authority": "lctgm",
                    "valueURI": "http://id.loc.gov/vocabulary/graphicMaterials/tgm006261",
                }
            },
            ["genre", "$"],
            "Maps",
        ),
        ({"a": [{"b": "b_value"}, {"c": "c_value"}]}, ["a", "c"], "c_value"),
    ],
    ids=[
        "empty list of keys",
        "key not present in a dict",
        "key not present in a list",
        "return a dict value with one key",
        "return a string value with a list of keys",
        "return a string value with a list of keys, from a list",
    ],
)
def test_get_value_from_dict_or_list(keys, dict_or_list, expected):
    assert get_value_from_dict_or_list(dict_or_list, keys) == expected

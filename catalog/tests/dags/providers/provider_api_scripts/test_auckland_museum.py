"""
TODO: Add additional tests for any methods you added in your subclass.
Try to test edge cases (missing keys, different data types returned, Nones, etc).
You may also need to update the given test names to be more specific.

Run your tests locally with `just test -k auckland_museum`
"""
import json
from pathlib import Path

from catalog.tests.dags.providers.provider_api_scripts.resources.json_load import (
    make_resource_json_func,
)
from common.licenses import get_license_info
from providers.provider_api_scripts.auckland_museum import AucklandMuseumDataIngester


# TODO: API responses used for testing can be added to this directory
RESOURCES = Path(__file__).parent / "resources/auckland_museum"
CC_BY_4_0 = get_license_info("https://creativecommons.org/licenses/by/4.0/")

# Set up test class
ingester = AucklandMuseumDataIngester()
_get_resource_json = make_resource_json_func("aucklandmuseum")


def test_get_next_query_params_default_response():
    actual_param = ingester.get_next_query_params(None)
    expected_param = {
        "q": "_exists_:primaryRepresentation+copyright:CC",
        "size": "100",
        "from": ingester.from_start,
    }
    assert actual_param == expected_param


def test_get_next_query_params_updates_parameters():
    previous_query_params = {
        "q": "_exists_:primaryRepresentation+copyright:CC",
        "size": "100",
        "from": ingester.from_start,
    }
    actual_result = ingester.get_next_query_params(previous_query_params)

    expected_result = {
        "q": "_exists_:primaryRepresentation+copyright:CC",
        "size": "100",
        "from": ingester.from_start + 100,
    }
    assert actual_result == expected_result


def test_get_record_data():
    # High level test for `get_record_data`. One way to test this is to create a
    # `tests/resources/AucklandMuseum/single_item.json` file containing a sample json
    # representation of a record from the API under test, call `get_record_data` with
    # the json, and directly compare to expected output.
    #
    # Make sure to add additional tests for records of each media type supported by
    # your provider.

    # Sample code for loading in the sample json

    with open(RESOURCES / "single_item.json") as f:
        resource_json = json.load(f)

    actual_data = ingester.get_record_data(resource_json)
    meta_data = {
        "type": "ecrm:E20_Biological_Object",
        "geopos": "",
        "department": "botany",
    }
    expected_data = {
        "url": "http://api.aucklandmuseum.com/id/media/v/214749",
        "license_info": CC_BY_4_0,
        "thumbnail_url": "http://api.aucklandmuseum.com/id/media/v/214749?rendering=thumbnail.jpg",
        "filesize": "2484439",
        "creator": "R. O. Gardner",
        "title": "Cypholophus macrocephalus mollis (Blume) Wedd. var. mollis (Wedd.) Wedd.",
        "meta_data": meta_data,
    }

    assert actual_data == expected_data

from pathlib import Path

from catalog.tests.dags.providers.provider_api_scripts.resources.json_load import (
    make_resource_json_func,
)
from common.licenses import get_license_info
from providers.provider_api_scripts.auckland_museum import AucklandMuseumDataIngester


RESOURCES = Path(__file__).parent / "resources/aucklandmuseum"
CC_BY_4_0 = get_license_info("https://creativecommons.org/licenses/by/4.0/")

ingester = AucklandMuseumDataIngester()
_get_resource_json = make_resource_json_func("aucklandmuseum")


def test_get_next_query_params_default_response():
    actual_param = ingester.get_next_query_params(None)
    expected_param = {
        "q": "_exists_:primaryRepresentation+copyright:CC",
        "size": "2000",
        "from": ingester.batch_start,
    }
    assert actual_param == expected_param


def test_get_record_data():
    # High level test for `get_record_data`. One way to test this is to create a
    # `tests/resources/AucklandMuseum/single_item.json` file containing a sample json
    # representation of a record from the API under test, call `get_record_data` with
    # the json, and directly compare to expected output.
    #
    # Make sure to add additional tests for records of each media type supported by
    # your provider.

    # Sample code for loading in the sample json

    single_item = _get_resource_json("single_item.json")
    actual_data = ingester.get_record_data(single_item)
    meta_data = {
        "type": "ecrm:E20_Biological_Object",
        "geopos": "",
        "department": "botany",
    }
    expected_data = {
        "foreign_landing_url": "https://www.aucklandmuseum.com/collections-research/collections/record/am_naturalsciences-object-691102",
        "foreign_identifier": "691102",
        "url": "http://api.aucklandmuseum.com/id/media/v/214749",
        "license_info": CC_BY_4_0,
        "thumbnail_url": "http://api.aucklandmuseum.com/id/media/v/214749?rendering=thumbnail.jpg",
        "creator": "R. O. Gardner",
        "title": "Cypholophus macrocephalus mollis (Blume) Wedd. var. mollis (Wedd.) Wedd.",
        "meta_data": meta_data,
    }

    assert actual_data == expected_data

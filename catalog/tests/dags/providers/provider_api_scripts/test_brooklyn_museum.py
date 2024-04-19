from unittest.mock import patch

import pytest
from tests.dags.providers.provider_api_scripts.resources.json_load import (
    make_resource_json_func,
)

from common.licenses import get_license_info
from common.loader import provider_details as prov
from common.storage.image import ImageStore
from providers.provider_api_scripts.brooklyn_museum import BrooklynMuseumDataIngester


bkm = BrooklynMuseumDataIngester()
image_store = ImageStore(provider=prov.BROOKLYN_DEFAULT_PROVIDER)
bkm.media_stores = {"image": image_store}
_get_resource_json = make_resource_json_func("brooklynmuseum")

CC_BY_3_0 = get_license_info("https://creativecommons.org/licenses/by/3.0/")
CC0 = get_license_info("https://creativecommons.org/publicdomain/zero/1.0/")


def test_build_query_param_default():
    actual_param = bkm.get_next_query_params(None)
    expected_param = {
        "has_images": 1,
        "rights_type_permissive": 1,
        "limit": bkm.batch_limit,
        "offset": 0,
    }
    assert actual_param == expected_param


def test_build_query_param_given():
    offset = 70
    actual_param = bkm.get_next_query_params({"foo": "bar", "offset": offset})
    expected_param = {
        "foo": "bar",
        "offset": offset + bkm.batch_limit,
    }
    assert actual_param == expected_param


@pytest.mark.parametrize(
    "resource_name, expected",
    [
        ("response_success.json", _get_resource_json("response_success.json")["data"]),
        ("response_error.json", None),
        ("response_nodata.json", []),
    ],
)
def test_get_data_from_response(resource_name, expected):
    response_json = _get_resource_json(resource_name)
    actual = bkm._get_data_from_response(response_json)
    assert actual == expected


@pytest.mark.parametrize(
    "batch_objects_name, object_data_name, expected_count",
    [
        ("batch_objects.json", "object_data.json", 1),
        ("no_batch_objects.json", "non_cc_object_data.json", 0),
    ],
)
def test_process_batch(batch_objects_name, object_data_name, expected_count):
    batch_objects = _get_resource_json(batch_objects_name)
    response_json = _get_resource_json(object_data_name)

    with (
        patch.object(bkm, "get_response_json"),
        patch.object(bkm, "_get_data_from_response", return_value=response_json),
        patch.object(image_store, "add_item"),
    ):
        actual_count = bkm.process_batch(batch_objects)

    assert actual_count == expected_count


@pytest.mark.parametrize(
    "resource_name, expected",
    [
        (
            "object_data.json",
            [
                {
                    "creator": None,
                    "foreign_identifier": 170425,
                    "foreign_landing_url": "https://www.brooklynmuseum.org/opencollection/objects/90636",
                    "height": 1152,
                    "url": "d1lfxha3ugu3d4.cloudfront.net/images/opencollection/objects/size4/CUR.66.242.29.jpg",
                    "license_info": CC_BY_3_0,
                    "meta_data": {
                        "accession_number": "66.242.29",
                        "classification": "Clothing",
                        "credit_line": "Gift of John C. Monks",
                        "medium": "Silk",
                    },
                    "title": "Caftan",
                    "width": 1536,
                },
            ],
        ),
        ("object_data_noimage.json", []),
    ],
)
def test_handle_object_data(resource_name, expected):
    response_json = _get_resource_json(resource_name)

    actual = bkm._handle_object_data(response_json, license_info=CC_BY_3_0)
    assert actual == expected


@pytest.mark.parametrize("field", ["id", "largest_derivative_url"])
def test_handle_object_data_missing_field(field):
    response_json = _get_resource_json("object_data.json")

    # Remove the requested field
    response_json["images"][0].pop(field)
    actual = bkm._handle_object_data(response_json, license_info=CC_BY_3_0)
    assert actual == []


@pytest.mark.parametrize("field", ["id", "largest_derivative_url"])
def test_handle_object_data_falsy_field(field):
    response_json = _get_resource_json("object_data.json")
    license_url = "https://creativecommons.org/licenses/by/3.0/"
    # Remove the requested field
    response_json["images"][0][field] = ""
    actual = bkm._handle_object_data(response_json, license_url)
    assert actual == []


@pytest.mark.parametrize(
    "resource_name, expected",
    [
        ("image_details.json", (1152, 1536)),
        ("image_nosize.json", (None, None)),
    ],
)
def test_get_image_size(resource_name, expected):
    response_json = _get_resource_json(resource_name)
    actual = bkm._get_image_sizes(response_json)

    assert actual == expected


@pytest.mark.parametrize(
    "resource_name, expected",
    [
        ("cc_license_info.json", CC_BY_3_0),
        ("public_license_info.json", CC0),
        ("no_license_info.json", None),
    ],
)
def test_get_license_info(resource_name, expected):
    response_json = {"rights_type": _get_resource_json(resource_name)}
    actual = bkm._get_license_info(response_json)

    assert actual == expected


def test_get_metadata():
    response_json = _get_resource_json("object_data.json")
    actual_metadata = bkm._get_metadata(response_json)
    expected_metadata = _get_resource_json("expected_metadata.json")

    assert actual_metadata == expected_metadata


@pytest.mark.parametrize(
    "data, expected",
    [
        (_get_resource_json("artists_details.json"), "John La Farge"),
        ({}, None),
    ],
)
def test_get_creators(data, expected):
    actual = bkm._get_creators(data)
    assert actual == expected


@pytest.mark.parametrize(
    "license_info, license_is_none",
    [
        (None, True),
        (get_license_info("https://creativecommons.org/licenses/by/4.0"), False),
    ],
)
@pytest.mark.parametrize(
    "data, data_is_none",
    [
        ({}, True),
        ({"doesnt-have-id": "foobar"}, True),
        ({"id": ""}, True),
        ({"id": "foobar"}, False),
    ],
)
@pytest.mark.parametrize(
    "object_data, object_data_is_none",
    [
        (None, True),
        ({"some-data": 1}, False),
    ],
)
def test_get_record_data(
    license_info, license_is_none, data, data_is_none, object_data, object_data_is_none
):
    should_be_none = any([license_is_none, data_is_none, object_data_is_none])
    with (
        patch.object(bkm, "_get_license_info", return_value=license_info),
        patch.object(bkm, "get_response_json"),
        patch.object(bkm, "_get_data_from_response", return_value=object_data),
        patch.object(bkm, "_handle_object_data"),
    ):
        actual = bkm.get_record_data(data)
        assert (actual is None) == should_be_none

import logging
from unittest.mock import MagicMock, patch

import pytest
import requests
from tests.dags.providers.provider_api_scripts.resources.json_load import (
    make_resource_json_func,
)

from common.licenses import LicenseInfo
from common.loader import provider_details as prov
from common.storage.image import ImageStore
from providers.provider_api_scripts.cleveland_museum import ClevelandDataIngester


@pytest.fixture(autouse=True)
def validate_url_string():
    with patch("common.urls.validate_url_string") as mock_validate_url_string:
        mock_validate_url_string.side_effect = lambda x, y=True: x
        yield


_license_info = (
    "cc0",
    "1.0",
    "https://creativecommons.org/publicdomain/zero/1.0/",
    None,
)
CC0_LICENSE = LicenseInfo(*_license_info)
license_info = LicenseInfo(*_license_info)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.DEBUG
)

clm = ClevelandDataIngester()
image_store = ImageStore(provider=prov.CLEVELAND_DEFAULT_PROVIDER)
clm.media_stores = {"image": image_store}


_get_resource_json = make_resource_json_func("clevelandmuseum")


def test_build_query_param_default():
    actual_param = clm.get_next_query_params({})
    expected_param = {"cc": "1", "has_image": "1", "limit": 1000, "skip": 0}
    assert actual_param == expected_param


def test_build_query_param_increments_offset():
    previous_query_params = {"cc": "1", "has_image": "1", "limit": 1000, "skip": 0}

    actual_param = clm.get_next_query_params(previous_query_params)
    expected_param = {"cc": "1", "has_image": "1", "limit": 1000, "skip": 1000}
    assert actual_param == expected_param


def test_get_image_data_web():
    image_data = _get_resource_json("image_type_web.json")
    actual_image = clm._get_image_data(image_data)

    expected_image = {
        "url": "https://openaccess-cdn.clevelandart.org/1335.1917/1335.1917_web.jpg",
        "width": "1263",
        "height": "775",
        "filesize": "716717",
        "filename": "1335.1917_web.jpg",
    }
    assert actual_image == expected_image


def test_get_image_data_print():
    image_data = _get_resource_json("image_type_print.json")
    actual_image = clm._get_image_data(image_data)

    expected_image = {
        "url": "https://openaccess-cdn.clevelandart.org/1335.1917/1335.1917_print.jpg",
        "width": "3400",
        "height": "2086",
        "filesize": "5582485",
        "filename": "1335.1917_print.jpg",
    }

    assert actual_image == expected_image


def test_get_image_data_full():
    image_data = _get_resource_json("image_type_full.json")
    actual_image = clm._get_image_data(image_data)

    expected_image = {
        "url": "https://openaccess-cdn.clevelandart.org/1335.1917/1335.1917_full.tif",
        "width": "6280",
        "height": "3853",
        "filesize": "72628688",
        "filename": "1335.1917_full.tif",
    }

    assert actual_image == expected_image


@pytest.mark.parametrize(
    "image_data",
    [_get_resource_json("image_type_none.json"), None, {}, []],
)
def test_get_image_data_falsy_returns_none(image_data):
    actual_image = clm._get_image_data(image_data)

    assert actual_image is None


def test_get_metadata():
    data = _get_resource_json("complete_data.json")
    actual_metadata = clm._get_metadata(data)
    expected_metadata = _get_resource_json("expect_metadata.json")
    assert actual_metadata == expected_metadata


def test_get_metadata_missing_attrs():
    data = _get_resource_json("complete_data.json")
    # Remove data to simulate it being missing
    data.pop("technique")
    data.pop("culture")
    actual_metadata = clm._get_metadata(data)

    # Remove data from expected values too
    expected_metadata = _get_resource_json("expect_metadata.json")
    expected_metadata.pop("technique")
    expected_metadata.pop("culture")

    assert actual_metadata == expected_metadata


def test_get_response_success():
    query_param = {"cc": 1, "has_image": 1, "limit": 1, "skip": 30000}
    response_json = _get_resource_json("response_success.json")
    r = requests.Response()
    r.status_code = 200
    r.json = MagicMock(return_value=response_json)
    with patch.object(clm.delayed_requester, "get", return_value=r) as mock_get:
        batch, _ = clm.get_batch(query_param)
    expected_response = _get_resource_json("expected_batch_data.json")

    assert mock_get.call_count == 1
    assert batch == [expected_response]
    assert len(batch) == 1


def test_get_response_no_data():
    query_param = {"cc": 1, "has_image": 1, "limit": 1, "skip": 33000}
    response_json = _get_resource_json("response_no_data.json")
    r = requests.Response()
    r.status_code = 200
    r.json = MagicMock(return_value=response_json)
    with patch.object(clm.delayed_requester, "get", return_value=r) as mock_get:
        batch, should_continue = clm.get_batch(query_param)

    assert mock_get.call_count == 1
    assert batch == []
    assert len(batch) == 0


def test_handle_response():
    response_json = _get_resource_json("handle_response_data.json")
    data = response_json["data"]
    actual_total_images = clm.process_batch(data)
    expected_total_images = 100

    assert actual_total_images == expected_total_images


def test_handle_single_response():
    response_json = _get_resource_json("response_success.json")
    batch = response_json["data"]
    # Patching save_item because it will have the filetype after clean_metadata
    with patch.object(image_store, "save_item") as mock_save_item:
        clm.process_batch(batch)
    expected_image = {
        "creator": "",
        "foreign_identifier": "96887",
        "foreign_landing_url": "https://clevelandart.org/art/1916.586.a",
        "width": 641,
        "height": 900,
        "filesize": 222248,
        "filetype": "jpg",
        "url": "https://openaccess-cdn.clevelandart.org/1916.586.a/1916.586.a_web.jpg",
        "license_": CC0_LICENSE.license,
        "license_version": CC0_LICENSE.version,
        "meta_data": {
            "license_url": CC0_LICENSE.url,
            "raw_license_url": None,
            "accession_number": "1916.586.a",
            "classification": "Miscellaneous",
            "credit_line": "Gift of Mr. and Mrs. J. H. Wade",
            "culture": "Germany, 18th century",
            "date": "1700s",
            "tombstone": "Scent Bottle, 1700s. Germany, 18th century. Glass with "
            "enamel decoration; overall: 10.2 cm (4 in.). The Cleveland "
            "Museum of Art, Gift of Mr. and Mrs. J. H. Wade 1916.586.a",
            "technique": "glass with enamel decoration",
        },
        "title": "Scent Bottle",
    }

    actual_image = mock_save_item.call_args[0][0]
    for key, value in expected_image.items():
        assert getattr(actual_image, key) == value

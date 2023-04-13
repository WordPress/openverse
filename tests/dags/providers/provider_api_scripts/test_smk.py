import pytest

from common.licenses import LicenseInfo
from providers.provider_api_scripts.smk import SmkDataIngester
from tests.dags.providers.provider_api_scripts.resources.json_load import (
    make_resource_json_func,
)


smk = SmkDataIngester()

CC0 = LicenseInfo(
    "cc0",
    "1.0",
    "https://creativecommons.org/publicdomain/zero/1.0/",
    None,
)


_get_resource_json = make_resource_json_func("smk")


def test_get_next_query_params_first_call():
    actual_param = smk.get_next_query_params(prev_query_params=None)
    expected_param = {
        "keys": "*",
        "filters": "[has_image:true],[public_domain:true]",
        "offset": 0,
        "rows": 2000,
        "lang": "en",
    }

    assert actual_param == expected_param


def test_get_next_query_params_increments_offset():
    actual_param = smk.get_next_query_params(
        {
            "keys": "*",
            "filters": "[has_image:true],[public_domain:true]",
            "offset": 0,
            "rows": 2000,
            "lang": "en",
        }
    )
    expected_param = {
        "keys": "*",
        "filters": "[has_image:true],[public_domain:true]",
        "offset": 2000,
        "rows": 2000,
        "lang": "en",
    }

    assert actual_param == expected_param


@pytest.mark.parametrize(
    "object_number, expected_url",
    [
        ("KKSgb22423", "https://open.smk.dk/en/artwork/image/KKSgb22423"),
        (
            "KKSgb22423 version 1",
            "https://open.smk.dk/en/artwork/image/KKSgb22423%20version%201",
        ),
        ("KSMB 25 106.5", "https://open.smk.dk/en/artwork/image/KSMB%2025%20106.5"),
    ],
)
def test__get_foreign_landing_url(object_number, expected_url):
    item = {"object_number": object_number}
    actual_url = smk._get_foreign_landing_url(item)
    assert actual_url == expected_url


def test__get_image_url():
    image_iiif_id = "https://iip.smk.dk/iiif/jp2/1z40kx99j_kksgb22423.tif.jp2"
    actual_url = smk._get_image_url(image_iiif_id)
    expected_url = "https://iip.smk.dk/iiif/jp2/1z40kx99j_kksgb22423.tif.jp2/full/!2048,/0/default.jpg"
    assert actual_url == expected_url


def test__get_title():
    item = {"titles": [{"title": "sample"}]}
    actual_title = smk._get_title(item)
    assert actual_title == "sample"


def test__get_title_none():
    item = {"id": "123_object"}
    actual_title = smk._get_title(item)
    assert actual_title is None


def test__get_images_high_quality():
    item = _get_resource_json("image_data_hq.json")
    expected_images_data = _get_resource_json("expected_image_data_hq.json")
    actual_images_data = smk._get_images(item)

    assert actual_images_data == expected_images_data


def test__get_images_legacy():
    item = _get_resource_json("image_data_legacy.json")
    expected_images_data = _get_resource_json("expected_image_data_legacy.json")
    actual_images_data = smk._get_images(item)

    assert actual_images_data == expected_images_data


def test__get_images_partial():
    # Left in as a regression test for
    # https://github.com/WordPress/openverse-catalog/issues/875
    item = _get_resource_json("image_data_partial.json")
    actual_images_data = smk._get_images(item)

    assert actual_images_data == []


def test__get_metadata():
    item = _get_resource_json("item.json")
    actual_metadata = smk._get_metadata(item)

    expected_metadata = {
        "created_date": "2020-03-21T10:18:17Z",
        "collection": "Gammel bestand",
        "techniques": "Kobberstik",
    }
    assert actual_metadata == expected_metadata


def test_get_record_data_returns_main_image():
    item = _get_resource_json("item.json")
    images = smk.get_record_data(item)

    assert len(images) == 1

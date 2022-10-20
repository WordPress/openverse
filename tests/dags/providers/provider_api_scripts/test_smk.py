import json
from pathlib import Path

from common.licenses import LicenseInfo
from providers.provider_api_scripts.smk import SmkDataIngester


RESOURCES = Path(__file__).parent.resolve() / "resources/smk"

smk = SmkDataIngester()

CC0 = LicenseInfo(
    "cc0",
    "1.0",
    "https://creativecommons.org/publicdomain/zero/1.0/",
    None,
)


def _get_resource_json(json_name):
    with open(RESOURCES / json_name) as f:
        resource_json = json.load(f)
    return resource_json


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


def test__get_foreign_landing_url():
    item = {"object_number": "KKSgb22423"}
    actual_url = smk._get_foreign_landing_url(item)
    expected_url = "https://open.smk.dk/en/artwork/image/KKSgb22423"
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
    item = _get_resource_json("image_data_partial.json")
    expected_images_data = _get_resource_json("expected_image_data_partial.json")

    actual_images_data = smk._get_images(item)

    assert actual_images_data == expected_images_data


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


def test_get_record_data_returns_alternative_images():
    item = _get_resource_json("item_with_alternative_images.json")
    images = smk.get_record_data(item)

    assert len(images) == 3

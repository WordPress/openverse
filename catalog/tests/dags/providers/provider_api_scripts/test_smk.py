import pytest

from catalog.tests.dags.providers.provider_api_scripts.resources.json_load import (
    make_resource_json_func,
)
from common.licenses import LicenseInfo
from providers.provider_api_scripts.smk import SmkDataIngester


smk = SmkDataIngester()

# With a different raw_license_info
CC0_SMK = LicenseInfo(
    "cc0",
    "1.0",
    "https://creativecommons.org/publicdomain/zero/1.0/",
    "https://creativecommons.org/share-your-work/public-domain/cc0/",
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
        ("", None),
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


@pytest.mark.parametrize(
    "quality",
    [
        pytest.param("hq", id="high_quality"),
        pytest.param("legacy", id="legacy"),
    ],
)
def test__get_record_data_quality(quality):
    file_name = f"image_data_{quality}.json"
    item = _get_resource_json(file_name)
    expected_images_data = _get_resource_json(f"expected_{file_name}")
    expected_record_data = {**expected_images_data, "license_info": CC0_SMK}
    actual_images_data = smk.get_record_data(item)

    assert actual_images_data == expected_record_data


def test__get_images_legacy_returns_none_with_falsy_id():
    item = _get_resource_json("image_data_legacy.json")
    item["id"] = ""
    actual_images_data = smk.get_record_data(item)

    assert actual_images_data is None


def test__get_images_partial():
    # Left in as a regression test for
    # https://github.com/WordPress/openverse-catalog/issues/875
    item = _get_resource_json("image_data_partial.json")
    actual_images_data = smk.get_record_data(item)

    assert actual_images_data is None


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
    image = smk.get_record_data(item)

    assert image == {
        "creator": "Altdorfer, Albrecht",
        "filesize": 47466428,
        "foreign_identifier": "https://iip.smk.dk/iiif/jp2/kks1615.tif.jp2",
        "foreign_landing_url": "https://open.smk.dk/en/artwork/image/KKS1615",
        "height": 5141,
        "width": 3076,
        "thumbnail_url": "https://iip-thumb.smk.dk/iiif/jp2/kks1615.tif.jp2/full/!1024,/0/default.jpg",
        "url": "https://iip.smk.dk/iiif/jp2/kks1615.tif.jp2/full/!2048,/0/default.jpg",
        "license_info": CC0_SMK,
        "meta_data": {
            "collection": "Gammel bestand",
            "techniques": "Kobberstik",
            "created_date": "2020-03-21T10:18:17Z",
        },
        "title": "Jomfru Maria med barnet og Sankt Anne ved vuggen",
    }


@pytest.mark.parametrize(
    "property_names",
    [
        pytest.param(["object_number"], id="falsy foreign_landing_url"),
        pytest.param(["rights"], id="falsy license_info"),
        # For items with iiif id, the image_url is constructed from it.
        pytest.param(["image_native", "image_iiif_id"], id="falsy url"),
        pytest.param(["id", "image_iiif_id"], id="falsy foreign_identifier"),
    ],
)
def test_get_record_data_returns_none_with_falsy_required_property(property_names):
    item = _get_resource_json("item.json")
    for prop in property_names:
        item[prop] = ""

    assert smk.get_record_data(item) is None


def test_get_record_data_with_spaces_in_urls():
    item = _get_resource_json("image_data_spaces.json")
    expected_image_data = _get_resource_json("expected_image_data_spaces.json")
    expected_record_data = {**expected_image_data, "license_info": CC0_SMK}
    actual_record_data = smk.get_record_data(item)

    assert actual_record_data == expected_record_data

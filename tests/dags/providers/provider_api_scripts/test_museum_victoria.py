import json
import logging
from pathlib import Path
from unittest.mock import patch

import pytest
from common.licenses import LicenseInfo, get_license_info
from common.loader import provider_details as prov
from common.storage.image import ImageStore
from providers.provider_api_scripts.museum_victoria import VictoriaDataIngester


RESOURCES = Path(__file__).parent / "resources/museumvictoria"


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.DEBUG
)
mv = VictoriaDataIngester()
image_store = ImageStore(provider=prov.VICTORIA_DEFAULT_PROVIDER)
mv.media_stores = {"image": image_store}


@pytest.fixture(autouse=True)
def after_test():
    yield
    mv.RECORDS_IDS = set()


def _get_resource_json(json_name):
    with open(RESOURCES / json_name) as f:
        resource_json = json.load(f)
        return resource_json


def test_get_query_param_default():
    actual_param = mv.get_next_query_params(None, **{"license_": mv.LICENSE_LIST[0]})
    expected_param = {
        "hasimages": "yes",
        "perpage": 100,
        "imagelicense": "public domain",
        "page": 0,
    }

    assert actual_param == expected_param


def test_get_query_param_offset():
    actual_param = mv.get_next_query_params(
        {
            "hasimages": "yes",
            "perpage": 100,
            "imagelicense": "public domain",
            "page": 10,
        }
    )

    expected_param = {
        "hasimages": "yes",
        "perpage": 100,
        "imagelicense": "public domain",
        "page": 11,
    }

    assert actual_param == expected_param


def test_get_record_data():
    media = _get_resource_json("record_data.json")
    actual_image_data = mv.get_record_data(media)
    assert len(actual_image_data) == 2

    expected_image_data = {
        "foreign_identifier": "media/488013",
        "image_url": "https://collections.museumsvictoria.com.au/content/media/13/488013-large.jpg",
        "height": 1753,
        "width": 3000,
        "creator": "",
        "license_info": LicenseInfo(
            "by",
            "4.0",
            "https://creativecommons.org/licenses/by/4.0/",
            "https://creativecommons.org/licenses/by/4.0",
        ),
        "foreign_landing_url": "https://collections.museumsvictoria.com.au/items/415715",
        "title": "Baggage Label - ICEM, Sailing Details, 15 Mar 1957",
        "meta_data": {
            "datemodified": "2017-12-12T05:56:00Z",
            "category": "History & Technology",
            "description": "Rectangular white blue and grey cardboard baggage label.",
            "keywords": "Immigrant Shipping,Immigrant Voyages,Immigration,Shipping,Station Pier,Women's Work",
            "classifications": "Migration,Processing - planning & departure,Luggage handling",
        },
    }

    assert actual_image_data[0] == expected_image_data


def test_filetype_gets_added_by_image_store():
    media = _get_resource_json("record_data.json")
    with patch.object(mv.media_stores["image"], "save_item") as mock_save:
        mv.process_batch([media])

    actual_image = mock_save.call_args[0][0]

    assert "jpg" == actual_image.filetype


def test_no_duplicate_records():
    media = _get_resource_json("record_data.json")
    mv.RECORDS_IDS.add("items/415715")
    actual_image_data = mv.get_record_data(media)

    assert actual_image_data is None


def test_get_images_success():
    media = _get_resource_json("media_data_success.json")
    actual_image_data = mv._get_images([media])

    expected_image_data = {
        "creator": "Photographer: Deb Tout-Smith",
        "foreign_identifier": "media/329745",
        "image_url": "https://collections.museumsvictoria.com.au/content/media/45/329745-large.jpg",
        "license_info": get_license_info(
            license_url="https://creativecommons.org/licenses/by/4.0"
        ),
        "width": 2785,
        "height": 2581,
    }

    assert actual_image_data[0] == expected_image_data


def test_get_media_info_failure():
    media = _get_resource_json("media_data_failure.json")
    actual_image_data = mv.get_record_data(media)

    assert actual_image_data is None


def test_get_image_data_large():
    image_data = _get_resource_json("large_image_data.json")

    actual_image_url, actual_height, actual_width, actual_filesize = mv._get_image_data(
        image_data
    )

    assert actual_image_url == (
        "https://collections.museumsvictoria.com.au/content/media/45/"
        "329745-large.jpg"
    )
    assert actual_height == 2581
    assert actual_width == 2785
    assert actual_filesize == 890933


def test_get_image_data_medium():
    image_data = _get_resource_json("medium_image_data.json")

    actual_image_url, actual_height, actual_width, actual_filesize = mv._get_image_data(
        image_data
    )

    assert actual_image_url == (
        "https://collections.museumsvictoria.com.au/content/media/45/"
        "329745-medium.jpg"
    )
    assert actual_height == 1390
    assert actual_width == 1500
    assert actual_filesize == 170943


def test_get_image_data_small():
    image_data = _get_resource_json("small_image_data.json")

    actual_image_url, actual_height, actual_width, actual_filesize = mv._get_image_data(
        image_data
    )

    assert actual_image_url == (
        "https://collections.museumsvictoria.com.au/content/media/45/"
        "329745-small.jpg"
    )
    assert actual_height == 500
    assert actual_width == 540
    assert actual_filesize == 20109


def test_get_image_data_none():
    image_data = {}

    actual_image_url, actual_height, actual_width, actual_filesize = mv._get_image_data(
        image_data
    )

    assert actual_image_url is None
    assert actual_height is None
    assert actual_width is None
    assert actual_filesize is None


def test_get_license_info():
    media = _get_resource_json("cc_image_data.json")
    actual_license = mv._get_license_info(media)
    expected_license_url = "https://creativecommons.org/licenses/by/4.0/"

    assert actual_license.url == expected_license_url


def test_get_license_info_failure():
    media = _get_resource_json("media_data_failure.json")
    actual_license = mv._get_license_info(media)

    assert actual_license is None


def test_get_metadata():
    obj = _get_resource_json("batch_objects.json")
    expected_metadata = _get_resource_json("metadata.json")
    actual_metadata = mv._get_metadata(obj[0])

    assert actual_metadata == expected_metadata


def test_get_creator():
    media = _get_resource_json("cc_image_data.json")
    actual_creator = mv._get_creator(media)

    assert actual_creator == "Photographer: Deb Tout-Smith"

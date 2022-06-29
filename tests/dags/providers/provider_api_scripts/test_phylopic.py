import json
import logging
from functools import partial
from pathlib import Path
from unittest.mock import patch

import pytest
from common.licenses import get_license_info
from providers.provider_api_scripts import phylopic as pp


RESOURCES = Path(__file__).parent / "resources/phylopic"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s",
    level=logging.DEBUG,
)


@pytest.fixture
def image_data():
    yield get_json("correct_meta_data_example.json")


def get_json(filename):
    with open(RESOURCES / filename) as f:
        return json.load(f)


def test_get_total_images_giving_zero():
    with patch.object(pp.delayed_requester, "get_response_json", return_value=None):
        img_count = pp._get_total_images()
        assert img_count == 0


def test_get_total_images_correct():
    r = get_json("total_images_example.json")
    with patch.object(pp.delayed_requester, "get_response_json", return_value=r):
        img_count = pp._get_total_images()
        assert img_count == 10


invalid_endpoint = partial(pytest.param, marks=pytest.mark.raises(exception=ValueError))


@pytest.mark.parametrize(
    "data, expected",
    [
        # Happy paths
        (
            {"date_start": "2020-02-10", "date_end": "2020-02-11"},
            "http://phylopic.org/api/a/image/list/modified/2020-02-10/2020-02-11",
        ),
        ({"offset": 0}, "http://phylopic.org/api/a/image/list/0/5"),
        # Missing/None parameters
        invalid_endpoint({}, None),
        invalid_endpoint({"offset": None}, None),
        invalid_endpoint({"date_start": None}, None),
        invalid_endpoint({"date_start": None, "date_end": None}, None),
        invalid_endpoint({"date_start": "2020-02-10", "date_end": None}, None),
    ],
)
def test_create_endpoint_for_IDs(data, expected):
    actual = pp._create_endpoint_for_IDs(**data)
    assert actual == expected


def test_get_image_IDs_for_no_content():
    with patch.object(pp.delayed_requester, "get_response_json", return_value=None):
        image_ids = pp._get_image_IDs("")
        expect_image_ids = None
        assert image_ids == expect_image_ids


def test_get_img_IDs_correct():
    r = get_json("image_ids_example.json")
    with patch.object(pp.delayed_requester, "get_response_json", return_value=r):
        actual_img_ids = pp._get_image_IDs("")
        expect_img_ids = [
            "863694ac-9f36-40f5-9452-1b435337d9cc",
            "329ff574-4bec-4f94-9dd6-9acfec2a6275",
            "9c98ff56-8044-483e-b9f1-bf368e4f3322",
        ]
        assert actual_img_ids == expect_img_ids


def test_get_meta_data_with_no_img_url():
    r = get_json("no_image_url_example.json")
    with patch.object(pp.delayed_requester, "get_response_json", return_value=r):
        meta_data = pp._get_meta_data({})
        assert meta_data is None


cc0_license = get_license_info(
    license_url="http://creativecommons.org/publicdomain/zero/1.0/"
)


def test_get_creator_details(image_data):
    with patch.object(
        pp.delayed_requester, "get_response_json", return_value=image_data
    ):
        result = image_data["result"]
        actual_creator_details = pp._get_creator_details(result)
        expect_creator_details = (
            "Jonathan Wells",
            "Jonathan Wells",
            "2020-02-26 11:59:53",
        )
        assert actual_creator_details == expect_creator_details


def test_get_taxa_details(image_data):
    with patch.object(
        pp.delayed_requester, "get_response_json", return_value=image_data
    ):
        result = image_data["result"]
        actual_taxa = pp._get_taxa_details(result)
        expect_taxa = (
            ["Chondrus crispus NODC Taxonomic Code, database (version 8.0) 1996"],
            "Chondrus crispus NODC Taxonomic Code, database (version 8.0) 1996",
        )
        assert actual_taxa == expect_taxa


def test_get_image_info(image_data):
    with patch.object(
        pp.delayed_requester, "get_response_json", return_value=image_data
    ):
        result = image_data["result"]
        actual_img_info = pp._get_image_info(
            result, "e9df48fe-68ea-419e-b9df-441e0b208335"
        )
        expect_img_info = (
            (
                "http://phylopic.org/assets/images/submissions/e9df48fe-68ea-"
                "419e-b9df-441e0b208335.1024.png"
            ),
            847,
            1024,
        )
        assert actual_img_info == expect_img_info


def test_process_item(image_data):
    image_uuid = "e9df48fe-68ea-419e-b9df-441e0b208335"
    with patch.object(pp.image_store, "save_item") as mock_save:
        item_data = image_data["result"]
        pp._process_item(item_data)
    actual_image = mock_save.call_args[0][0]
    expected_image = {
        "foreign_identifier": image_uuid,
        "foreign_landing_url": f"http://phylopic.org/image/{image_uuid}",
        "url": "http://phylopic.org/assets/images/submissions/e9df48fe-68ea-419e-b9df-441e0b208335.1024.png",
        "width": 847,
        "height": 1024,
        "filetype": "png",
        "creator": "Jonathan Wells",
        "license_": "cc0",
        "license_version": "1.0",
        "title": "Chondrus crispus NODC Taxonomic Code, database (version 8.0) 1996",
        "meta_data": {
            "taxa": [
                "Chondrus crispus NODC Taxonomic Code, database (version 8.0) 1996"
            ],
            "credit_line": "Jonathan Wells",
            "pub_date": "2020-02-26 11:59:53",
            "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
            "raw_license_url": "http://creativecommons.org/publicdomain/zero/1.0/",
        },
    }
    for key, value in expected_image.items():
        assert getattr(actual_image, key) == value


def test_get_image_info_with_no_img_url():
    r = get_json("no_image_url_example.json")
    with patch.object(pp.delayed_requester, "get_response_json", return_value=r):
        result = r["result"]
        actual_img_info = list(
            pp._get_image_info(result, "7f7431c6-8f78-498b-92e2-ebf8882a8923")
        )
        expect_img_info = [None, None, None]
        assert actual_img_info == expect_img_info


@pytest.mark.parametrize(
    "date_start, days, expected",
    [
        ("2022-01-10", 10, "2022-01-20"),
        ("2022-02-28", 7, "2022-03-07"),
        ("2022-02-28", -7, "2022-02-21"),
    ],
)
def test_compute_date_range(date_start, days, expected):
    actual = pp._compute_date_range(date_start, days)
    assert actual == expected

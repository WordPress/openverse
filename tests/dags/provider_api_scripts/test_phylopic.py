import json
import logging
import os
from unittest.mock import patch

import provider_api_scripts.phylopic as pp
from common.licenses.licenses import LicenseInfo


RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "resources/phylopic"
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s",
    level=logging.DEBUG,
)


def test_get_total_images_giving_zero():
    with patch.object(pp.delayed_requester, "get_response_json", return_value=None):
        img_count = pp._get_total_images()
        assert img_count == 0


def test_get_total_images_correct():
    with open(os.path.join(RESOURCES, "total_images_example.json")) as f:
        r = json.load(f)
    with patch.object(pp.delayed_requester, "get_response_json", return_value=r):
        img_count = pp._get_total_images()
        assert img_count == 10


def test_create_endpoint_for_IDs_by_date():
    actual_endpoint = pp._create_endpoint_for_IDs(**{"date": "2020-02-10"})
    expect_endpoint = str("http://phylopic.org/api" "/a/image/list/modified/2020-02-10")
    assert actual_endpoint == expect_endpoint


def test_create_endpoint_for_IDs_all():
    actual_endpoint = pp._create_endpoint_for_IDs(**{"offset": 0})
    expect_endpoint = "http://phylopic.org/api/a/image/list/0/5"
    assert actual_endpoint == expect_endpoint


def test_get_image_IDs_for_no_content():
    with patch.object(pp.delayed_requester, "get_response_json", return_value=None):
        image_ids = pp._get_image_IDs("")
        expect_image_ids = [None]
        assert image_ids == expect_image_ids


def test_get_img_IDs_correct():
    with open(os.path.join(RESOURCES, "image_ids_example.json")) as f:
        r = json.load(f)
    with patch.object(pp.delayed_requester, "get_response_json", return_value=r):
        actual_img_ids = pp._get_image_IDs("")
        expect_img_ids = [
            "863694ac-9f36-40f5-9452-1b435337d9cc",
            "329ff574-4bec-4f94-9dd6-9acfec2a6275",
            "9c98ff56-8044-483e-b9f1-bf368e4f3322",
        ]
        assert actual_img_ids == expect_img_ids


def test_get_meta_data_with_no_img_url():
    with open(os.path.join(RESOURCES, "no_image_url_example.json")) as f:
        r = json.load(f)
    with patch.object(pp.delayed_requester, "get_response_json", return_value=r):
        meta_data = pp._get_meta_data("")
        assert meta_data is None


def test_get_meta_data_for_none_response():
    with patch.object(pp.delayed_requester, "get_response_json", return_value=None):
        meta_data = pp._get_meta_data("")
        assert meta_data is None


def test_get_meta_data_correct():
    with open(os.path.join(RESOURCES, "correct_meta_data_example.json")) as f:
        r = json.load(f)
    with patch.object(pp.delayed_requester, "get_response_json", return_value=r):
        actual_meta_data = pp._get_meta_data("e9df48fe-68ea-419e-b9df-441e0b208335")
        expect_meta_data = [
            (
                "http://phylopic.org/assets/images/submissions/e9df48fe-68ea-"
                "419e-b9df-441e0b208335.1024.png"
            ),
            "http://phylopic.org/image/e9df48fe-68ea-419e-b9df-441e0b208335",
            (
                "http://phylopic.org/assets/images/submissions/e9df48fe-68ea-"
                "419e-b9df-441e0b208335.1024.png"
            ),
            "",
            "847",
            "1024",
            "http://creativecommons.org/publicdomain/zero/1.0/",
            "Jonathan Wells",
            ("Chondrus crispus NODC Taxonomic Code, database " "(version 8.0) 1996"),
            {
                "taxa": [
                    (
                        "Chondrus crispus NODC Taxonomic Code, database "
                        "(version 8.0) 1996"
                    )
                ],
                "credit_line": "Jonathan Wells",
                "pub_date": "2020-02-26 11:59:53",
            },
        ]
        assert actual_meta_data == expect_meta_data


def test_get_creator_details():
    with open(os.path.join(RESOURCES, "correct_meta_data_example.json")) as f:
        r = json.load(f)
    with patch.object(pp.delayed_requester, "get_response_json", return_value=r):
        result = r["result"]
        actual_creator_details = pp._get_creator_details(result)
        expect_creator_details = (
            "Jonathan Wells",
            "Jonathan Wells",
            "2020-02-26 11:59:53",
        )
        assert actual_creator_details == expect_creator_details


def test_get_taxa_details():
    with open(os.path.join(RESOURCES, "correct_meta_data_example.json")) as f:
        r = json.load(f)
    with patch.object(pp.delayed_requester, "get_response_json", return_value=r):
        result = r["result"]
        actual_taxa = pp._get_taxa_details(result)
        expect_taxa = (
            [("Chondrus crispus NODC Taxonomic Code, database " "(version 8.0) 1996")],
            "Chondrus crispus NODC Taxonomic Code, database (version 8.0) 1996",
        )
        assert actual_taxa == expect_taxa


def test_get_image_info():
    with open(os.path.join(RESOURCES, "correct_meta_data_example.json")) as f:
        r = json.load(f)
    with patch.object(pp.delayed_requester, "get_response_json", return_value=r):
        result = r["result"]
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
            "",
        )
        assert actual_img_info == expect_img_info


def test_get_image_info_with_no_img_url():
    with open(os.path.join(RESOURCES, "no_image_url_example.json")) as f:
        r = json.load(f)
    with patch.object(pp.delayed_requester, "get_response_json", return_value=r):
        result = r["result"]
        actual_img_info = list(
            pp._get_image_info(result, "7f7431c6-8f78-498b-92e2-ebf8882a8923")
        )
        expect_img_info = [None, None, None, None]
        assert actual_img_info == expect_img_info


def test_create_args():
    id_ = "e6014244-4dd5-4785-bf2e-c67dc4d05ca8"
    d = [
        (
            "http://phylopic.org/assets/images/submissions/e6014244-4dd5-"
            "4785-bf2e-c67dc4d05ca8.1024.png"
        ),
        "http://phylopic.org/image/e6014244-4dd5-4785-bf2e-c67dc4d05ca8",
        (
            "http://phylopic.org/assets/images/submissions/e6014244-4dd5-"
            "4785-bf2e-c67dc4d05ca8.1024.png"
        ),
        (
            "http://phylopic.org/assets/images/submissions/e6014244-4dd5-4785-"
            "bf2e-c67dc4d05ca8.256.png"
        ),
        "1024",
        "1024",
        "http://creativecommons.org/publicdomain/zero/1.0/",
        "Jonathan Wells",
        "Apicomplexa",
        {
            "taxa": [
                "Apicomplexa",
                "Plasmodiidae Mesnil 1903",
                "Sporozoa",
                "Plasmodium Marchiafava & Celli 1885",
                "Plasmodium falciparum",
                "Plasmodium (Laverania)",
                "Haemospororida Danilewsky",
                "Aconoidasida Mehlhorn, Peters & Haberkorn 1980",
            ],
            "credit_line": "Jonathan Wells",
            "pub_date": "2020-02-26 13:07:08",
        },
    ]
    actual_args = pp._create_args(d, id_)
    expect_args = {
        "foreign_landing_url": (
            "http://phylopic.org/image/e6014244-4dd5-" "4785-bf2e-c67dc4d05ca8"
        ),
        "image_url": (
            "http://phylopic.org/assets/images/submissions/e6014244"
            "-4dd5-4785-bf2e-c67dc4d05ca8.1024.png"
        ),
        "thumbnail_url": (
            "http://phylopic.org/assets/images/submissions/"
            "e6014244-4dd5-4785-bf2e-c67dc4d05ca8.256.png"
        ),
        "license_info": (
            LicenseInfo(
                license="cc0",
                version="1.0",
                url="https://creativecommons.org/publicdomain/zero/1.0/",
                raw_url="http://creativecommons.org/publicdomain/zero/1.0/",
            )
        ),
        "width": "1024",
        "height": "1024",
        "creator": "Jonathan Wells",
        "title": "Apicomplexa",
        "meta_data": {
            "taxa": (
                [
                    "Apicomplexa",
                    "Plasmodiidae Mesnil 1903",
                    "Sporozoa",
                    "Plasmodium Marchiafava & Celli 1885",
                    "Plasmodium falciparum",
                    "Plasmodium (Laverania)",
                    "Haemospororida Danilewsky",
                    ("Aconoidasida Mehlhorn, " "Peters & Haberkorn 1980"),
                ]
            ),
            "credit_line": "Jonathan Wells",
            "pub_date": "2020-02-26 13:07:08",
        },
        "foreign_identifier": "e6014244-4dd5-4785-bf2e-c67dc4d05ca8",
    }
    assert actual_args == expect_args
    assert len(actual_args) == 10

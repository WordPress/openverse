import json
import logging
import os
import requests
from unittest.mock import patch, MagicMock
import pytest
import metropolitan_museum_of_art as mma
from common.licenses.licenses import LicenseInfo

RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    "tests/resources/metropolitan_museum_of_art",
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def test_get_object_ids():
    r = requests.Response()
    r.status_code = 200
    r.json = MagicMock(return_value={
        "total": 4, "objectIDs": [153, 1578, 465, 546]})
    with patch.object(mma.delayed_requester, "get", return_value=r):
        total_objects = mma._get_object_ids("")
    assert total_objects[0] == 4
    assert total_objects[1] == [153, 1578, 465, 546]


def test_get_response_json():
    expect_json = {"it": "works"}
    endpoint = "https://abc.com"
    query_params = {"a": "b"}
    retries = 2
    with patch.object(
        mma.delayed_requester, "get_response_json", return_value=expect_json
    ) as mock_get_response_json:
        r_json = mma._get_response_json(
            query_params, endpoint, retries=retries)

    assert r_json == expect_json
    mock_get_response_json.assert_called_once_with(
        endpoint, query_params=query_params, retries=retries
    )


def test_create_meta_data():
    exact_response = {
        "accessionNumber": "36.100.45",
        "classification": "Paintings",
        "creditLine": (
            "The Howard Mansfield Collection, Purchase, Rogers Fund, 1936"),
        "culture": "Japan",
        "objectDate": "late 17th century",
        "medium": "Hanging scroll; ink and color on silk",
    }
    exact_meta_data = {
        "accession_number": "36.100.45",
        "classification": "Paintings",
        "credit_line": (
            "The Howard Mansfield Collection, Purchase, Rogers Fund, 1936"),
        "culture": "Japan",
        "date": "late 17th century",
        "medium": "Hanging scroll; ink and color on silk",
    }
    r = requests.Response()
    r.status_code = 200
    r.json = MagicMock(return_value=exact_response)
    with patch.object(mma.delayed_requester, "get", return_value=r):
        response = mma._get_response_json(None, "", retries=2)
        meta_data = mma._create_meta_data(response)

    assert exact_meta_data == meta_data


def test_get_data_for_image_with_none_response():
    with patch.object(
            mma.delayed_requester, "get", return_value=None) as mock_get:
        with pytest.raises(Exception):
            assert mma._get_data_for_image(10)

    assert mock_get.call_count == 6


def test_get_data_for_image_with_non_ok():
    r = requests.Response()
    r.status_code = 504
    r.json = MagicMock(return_value={})
    with patch.object(
            mma.delayed_requester, "get", return_value=r) as mock_get:
        with pytest.raises(Exception):
            assert mma._get_data_for_image(10)

    assert mock_get.call_count == 6


def test_get_data_for_image_returns_response_json_when_all_ok(monkeypatch):
    with open(os.path.join(
            RESOURCES, "sample_response_without_additional.json")) as f:
        actual_response_json = json.load(f)

    def mock_get_response_json(query_params, retries=0):
        return actual_response_json

    monkeypatch.setattr(mma, "_get_response_json", mock_get_response_json)
    with open(os.path.join(
            RESOURCES, "sample_additional_image_data.json")) as f:
        image_data = json.load(f)

    r = requests.Response()
    r.status_code = 200
    r.json = MagicMock(return_value=image_data)
    with patch.object(
            mma.image_store, "add_item", return_value=image_data) as mock_add:
        mma._get_data_for_image(45733)

    mock_add.assert_called_with(
        creator="",
        foreign_identifier="45733-79_2_414b_S1_sf",
        foreign_landing_url=(
            "https://www.metmuseum.org/art/collection/search/47533"),
        image_url=(
            "https://images.metmuseum.org/CRDImages/as/original/79_2_414b_S1"
            "_sf.jpg"),
        license_info=(LicenseInfo('cc0', '1.0', 'https://creativecommons.org/publicdomain/zero/1.0/', None)),
        meta_data={
            "accession_number": "79.2.414b",
            "classification": "Ceramics",
            "culture": "China",
            "date": "",
            "medium": "Porcelain painted in underglaze blue",
            "credit_line": "Purchase by subscription, 1879",
        },
        thumbnail_url=(
            "https://images.metmuseum.org/CRDImages/as/web-large/79_2_414b_S1"
            "_sf.jpg"),
        title="Cover",
    )

    assert mock_add.call_count == 1


def test_get_data_for_image_returns_response_json_with_additional_images(
        monkeypatch):
    with open(os.path.join(RESOURCES, "sample_response.json")) as f:
        actual_response_json = json.load(f)

    def mock_get_response_json(query_params, retries=0):
        return actual_response_json

    monkeypatch.setattr(mma, "_get_response_json", mock_get_response_json)
    with open(os.path.join(
            RESOURCES, "sample_additional_image_data.json")) as f:
        image_data = json.load(f)

    r = requests.Response()
    r.status_code = 200
    r.json = MagicMock(return_value=image_data)
    with patch.object(
            mma.image_store, "add_item", return_value=image_data) as mock_add:
        mma._get_data_for_image(45734)

    mock_add.assert_called_with(
        creator="Kiyohara Yukinobu",
        foreign_identifier="45734-DP251120",
        foreign_landing_url=(
            "https://wwwstg.metmuseum.org/art/collection/search/45734"),
        image_url=(
            "https://images.metmuseum.org/CRDImages/as/original/DP251120.jpg"),
        license_info=(LicenseInfo("cc0", "1.0", 'https://creativecommons.org/publicdomain/zero/1.0/', None)),
        meta_data={
            "accession_number": "36.100.45",
            "classification": "Paintings",
            "culture": "Japan",
            "date": "late 17th century",
            "medium": "Hanging scroll; ink and color on silk",
            "credit_line": (
                "The Howard Mansfield Collection, Purchase, Rogers Fund, 1936"
            ),
        },
        thumbnail_url=None,
        title="Quail and Millet",
    )

    assert mock_add.call_count == 3

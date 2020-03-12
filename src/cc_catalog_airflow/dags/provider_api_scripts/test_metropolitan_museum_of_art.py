import json
import logging
import os
import requests
from unittest.mock import patch, MagicMock
import pytest
import metropolitan_museum_of_art as mma

RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'tests/resources/metropolitan_museum_of_art'
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def test_get_object_ids():
    r = requests.Response()
    r.status_code = 200
    r.json = MagicMock(return_value={
        'total': 4,
        'objectIDs': [153, 1578, 465, 546]
        })
    with patch.object(
        mma.delayed_requester,
        'get',
        return_value=r
    ) as mock_get:
        total_objects = mma._get_object_ids('')
    assert total_objects[0] == 4
    assert total_objects[1] == [153, 1578, 465, 546]


def test_get_response_json_retries_with_none_response():
    with patch.object(
            mma.delayed_requester,
            'get',
            return_value=None
    ) as mock_get:
        with pytest.raises(Exception):
            assert mma._get_response_json(None, '', retries=2)

    assert mock_get.call_count == 3


def test_get_response_json_retries_with_non_ok():
    r = requests.Response()
    r.status_code = 504
    r.json = MagicMock(return_value={})
    with patch.object(
            mma.delayed_requester,
            'get',
            return_value=r
    ) as mock_get:
        with pytest.raises(Exception):
            assert mma._get_response_json(None, '', retries=2)

    assert mock_get.call_count == 3


def test_get_response_json_returns_response_json_when_all_ok():
    expect_response_json = {
        'accessionNumber': '36.100.45',
        'artistAlphaSort': 'Kiyohara Yukinobu',
        'artistBeginDate': '1643'
    }
    r = requests.Response()
    r.status_code = 200
    r.json = MagicMock(return_value=expect_response_json)
    with patch.object(
            mma.delayed_requester,
            'get',
            return_value=r
    ) as mock_get:
        actual_response_json = mma._get_response_json(None, '', retries=2)

    assert mock_get.call_count == 1
    assert actual_response_json == expect_response_json


def test_create_meta_data():
    exact_response = {
        'accessionNumber': '36.100.45',
        'classification': 'Paintings',
        'creditLine': (
            'The Howard Mansfield Collection, Purchase, Rogers Fund, 1936'
            ),
        'culture': 'Japan',
        'objectDate': 'late 17th century',
        'medium': 'Hanging scroll; ink and color on silk',
    }
    exact_meta_data = {
        'accession_number': '36.100.45',
        'classification': 'Paintings',
        'credit_line': (
            'The Howard Mansfield Collection, Purchase, Rogers Fund, 1936'
            ),
        'culture': 'Japan',
        'date': 'late 17th century',
        'medium': 'Hanging scroll; ink and color on silk',
    }
    r = requests.Response()
    r.status_code = 200
    r.json = MagicMock(return_value=exact_response)
    with patch.object(
        mma.delayed_requester,
        'get',
        return_value=r
    ) as mock_get:
        response = mma._get_response_json(None, '', retries=2)
        meta_data = mma._create_meta_data(response)

    assert exact_meta_data == meta_data


def test_process_image_data_handles_example_dict():
    with open(os.path.join(RESOURCES, 'sample_image_data.json')) as f:
        image_data = json.load(f)

    with patch.object(
        mma.image_store,
        'add_item',
        return_value=1
    ) as mock_add:
        mma._process_image_data(image_data)

    mock_add.assert_called_once_with(
        foreign_landing_url=(
            "https://wwwstg.metmuseum.org/art/collection/search/45734"
            ),
        image_url=(
            "https://images.metmuseum.org/CRDImages/as/original/DP251139.jpg"
            ),
        thumbnail_url=(
            "https://images.metmuseum.org/CRDImages/as/web-large/DP251139.jpg"
            ),
        license_="cc0",
        license_version="1.0",
        foreign_identifier=45734,
        creator="Kiyohara Yukinobu",
        title="Quail and Millet",
        meta_data={
            "accession_number": "36.100.45",
            "classification": "Paintings",
            "credit_line": (
                "The Howard Mansfield Collection, Purchase, Rogers Fund, 1936"
                ),
            "culture": "Japan"
        }
    )

def test_get_data_for_image_with_none_response():
    with patch.object(
            mma.delayed_requester,
            'get',
            return_value=None
    ) as mock_get:
        with pytest.raises(Exception):
            assert mma._get_data_for_image(10)

    assert mock_get.call_count == 6

def test_get_data_for_image_with_non_ok():
    r = requests.Response()
    r.status_code = 504
    r.json = MagicMock(return_value={})
    with patch.object(
            mma.delayed_requester,
            'get',
            return_value=r
    ) as mock_get:
        with pytest.raises(Exception):
            assert mma._get_data_for_image(10)

    assert mock_get.call_count == 6

def test_get_image_data_returns_response_json_when_all_ok():
    with open(os.path.join(RESOURCES, 'sample_image_data.json')) as f:
        image_data = json.load(f)

    r = requests.Response()
    r.status_code = 200
    r.json = MagicMock(return_value=image_data)
    with patch.object(
        mma.image_store,
        'add_item',
        return_value=image_data
    ) as mock_add:
        mma._get_data_for_image(45734)

    mock_add.assert_called_with(
        creator="Kiyohara Yukinobu",
        foreign_identifier="45734-1",
        foreign_landing_url="https://www.metmuseum.org/art/collection/search/45734",
        image_url="https://images.metmuseum.org/CRDImages/as/original/DP251120.jpg",
        license_="cc0",
        license_version="1.0",
        meta_data={
            "accession_number": "36.100.45",
            "classification": "Paintings",
            "culture": "Japan",
            "date": "late 17th century",
            "medium": "Hanging scroll; ink and color on silk",
            "credit_line": (
                "The Howard Mansfield Collection, Purchase, Rogers Fund, 1936"
                )
            },
        thumbnail_url="", 
        title="Quail and Millet"
    )

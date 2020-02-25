import json
import logging
import os
import requests
from unittest.mock import patch, MagicMock
import pytest
import metropolitan_museum_of_art as mma

RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'tests/resources/metropolitan_museum_of_art'
)

endpoint = 'https://collectionapi.metmuseum.org/public/collection/v1/objects/{}'.format(553)

logging.basicConfig(format='%(asctime)s: [%(levelname)s - Met Museum API] =======> %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def test_get_object_ids():
    r = requests.Response()
    r.status_code = 200
    r.json = MagicMock(return_value={
        'total': 4,
        'objectIDs': [153,1578,465,546]
        })
    with patch.object(
        mma.delayed_requester,
        'get',
        return_value=r
    ) as mock_get:
        total_objects = mma._get_object_ids('')
    assert total_objects[0] == 4
    assert total_objects[1] == [153,1578,465,546]

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
        'accession_number': '14.11.3',
        'artistAphaSort': 'United States Pottery Company',
        'artistBeginDate': '1852'
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
        'accession_number': '14.11.3',
        'classification': 'Ceramics',
        'credit_line': 'Rogers Fund, 1914',
        'culture': 'American'
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
    
    assert response == exact_response

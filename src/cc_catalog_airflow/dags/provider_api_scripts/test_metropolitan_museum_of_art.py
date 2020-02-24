import json
import logging
import os
import requests
from unittest.mock import patch, MagicMock
import pytest
import metropolitan_museum_of_art as mma

endpoint = 'https://collectionapi.metmuseum.org/public/collection/v1/objects/{}'.format(553)

RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'tests/resources/metropolitan_museum_of_art'
)

logging.basicConfig(format='%(asctime)s: [%(levelname)s - Met Museum API] =======> %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def test_get_object_ids():
    total_objects = mma.get_object_ids('2019-02-01')
    assert total_objects[0] == 333893

def test_get_response_json():
    response = mma._get_response_json(None,endpoint)
    assert response['accessionNumber'] == '14.11.3'
    assert response['artistAlphaSort'] == 'United States Pottery Company'
    assert response['artistBeginDate'] == '1852'


import os
import json
import logging
import requests
from unittest.mock import MagicMock, patch

import staten_museum as sm

RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'tests/resources/statenmuseum'
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.DEBUG
)


def _get_resource_json(json_name):
    with open(os.path.join(RESOURCES, json_name)) as f:
        resource_json = json.load(f)
    return resource_json


def test_get_query_param_default():
    actual_param = sm._get_query_param()
    expected_param = {
        "keys": "*",
        "filter": "[has_image:true],[public_domain:true]",
        "offset": 0,
        "rows": 2000
    }

    assert actual_param == expected_param


def test_get_query_param_offset():
    actual_param = sm._get_query_param(offset=100)
    expected_param = {
        "keys": "*",
        "filter": "[has_image:true],[public_domain:true]",
        "offset": 100,
        "rows": 2000
    }

    assert actual_param == expected_param




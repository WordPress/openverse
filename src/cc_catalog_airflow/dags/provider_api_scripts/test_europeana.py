import json
import logging
import os
import requests
from unittest.mock import patch, MagicMock

import europeana

RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'tests/resources/europeana'
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.DEBUG,
)


def _get_resource_json(json_name):
    with open(os.path.join(RESOURCES, json_name)) as f:
        resource_json = json.load(f)

    return resource_json


def test_derive_timestamp_pair():
    # Note that the timestamps are derived as if input was in UTC.
    start_ts, end_ts = europeana._derive_timestamp_pair('2018-01-15')
    assert start_ts == '2018-01-15T00:00:00Z'
    assert end_ts == '2018-01-16T00:00:00Z'


def test_get_image_list_retries_with_empty_response():
    response_json = _get_resource_json('europeana_example.json')
    response_json['items'] = []
    r = requests.Response()
    r.json = MagicMock(return_value=response_json)
    with patch.object(
            europeana.delayed_requester,
            'get',
            return_value=r
    ) as mock_get:
        europeana._get_image_list('1234', '5678', 'test_cursor', max_tries=3)

    assert mock_get.call_count == 3


def test_get_image_list_retries_with_non_ok_response():
    response_json = _get_resource_json('europeana_example.json')
    r = requests.Response()
    r.status_code = 504
    r.json = MagicMock(return_value=response_json)
    with patch.object(
            europeana.delayed_requester,
            'get',
            return_value=r
    ) as mock_get:
        europeana._get_image_list('1234', '5678', 'test_cursor', max_tries=3)

    assert mock_get.call_count == 3

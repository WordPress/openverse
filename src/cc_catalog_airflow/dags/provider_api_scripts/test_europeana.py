import json
import logging
import os
import requests
from unittest.mock import patch, MagicMock

import europeana

RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'tests/resources/flickr'
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
    assert start_ts == '1515974400'
    assert end_ts == '1516060800'




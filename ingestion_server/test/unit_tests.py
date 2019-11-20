import pytest
import datetime
from uuid import uuid4
from ingestion_server.elasticsearch_models import Image


def create_mock_image(override=None):
    """
    Produce a mock image. Override default fields by passing in a dict with the
    desired keys and values.

    For example, to make an image with a custom title and default everything
    else:
    >>> create_mock_image({'title': 'My title'})
    :return:
    """
    test_popularity = {
        'views': 50,
        'likes': 3,
        'comments': 1
    }
    test_data = {
        'id': 0,
        'title': 'Unit test title',
        'identifier': str(uuid4()),
        'creator': 'Eric Idle',
        'creator_url': 'https://creativecommons.org',
        'tags': [{'name': 'test', 'accuracy': 0.9}],
        'created_on': datetime.datetime.now(),
        'url': 'https://creativecommons.org',
        'thumbnail': 'https://creativecommons.org',
        'provider': 'test',
        'source': 'test',
        'license': 'cc-by',
        'license_version': '4.0',
        'foreign_landing_url': 'https://creativecommons.org',
        'view_count': 0,
        'height': 500,
        'width': 500,
        'meta_data': {'popularity_metrics': test_popularity}
    }
    for k, v in override.items():
        test_data[k] = v
    schema = {}
    row = []
    idx = 0
    for k, v in test_data.items():
        schema[k] = idx
        row.append(v)
        idx += 1
    return Image.database_row_to_elasticsearch_doc(row, schema)


def test_size():
    small = create_mock_image({'height': 600, 'width': 300})
    assert small.size == 'small'
    huge = create_mock_image({'height': 4096, 'width': 4096})
    assert huge.size == 'large'


def test_aspect_ratio():
    square = create_mock_image({'height': 300, 'width': 300})
    assert square.aspect_ratio == 'square'
    tall = create_mock_image({'height': 500, 'width': 200})
    assert tall.aspect_ratio == 'tall'
    wide = create_mock_image({'height': 200, 'width': 500})
    assert wide.aspect_ratio == 'wide'

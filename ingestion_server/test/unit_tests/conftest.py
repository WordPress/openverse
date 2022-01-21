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
    test_popularity = {"views": 50, "likes": 3, "comments": 1}
    license_url = "https://creativecommons.org/licenses/by/2.0/fr/legalcode"
    meta_data = {"popularity_metrics": test_popularity, "license_url": license_url}
    test_data = {
        "id": 0,
        "title": "Unit test title",
        "identifier": str(uuid4()),
        "creator": "Eric Idle",
        "creator_url": "https://creativecommons.org",
        "tags": [{"name": "test", "accuracy": 0.9}],
        "created_on": datetime.datetime.now(),
        "url": "https://creativecommons.org",
        "thumbnail": "https://creativecommons.org",
        "provider": "test",
        "source": "test",
        "license": "cc-by",
        "license_version": "4.0",
        "foreign_landing_url": "https://creativecommons.org",
        "view_count": 0,
        "height": 500,
        "width": 500,
        "mature": False,
        "meta_data": meta_data,
    }
    if override:
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

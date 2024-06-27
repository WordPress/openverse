import datetime
from uuid import uuid4

from indexer_worker.elasticsearch_models import Audio, Image


def create_mock_audio(override=None):
    """
    Produce a mock audio.

    Override default fields by passing in a dict with the desired keys and values.
    For example, to make an image with a custom title and default everything
    else:
    >>> create_mock_audio({'title': 'My title'})
    :return:
    """

    test_popularity = {"downloads": 3}
    license_url = "http://creativecommons.org/publicdomain/zero/1.0/"
    meta_data = {"popularity_metrics": test_popularity, "license_url": license_url}
    test_data = {
        "id": 0,
        "title": "Torneira de água",
        "identifier": str(uuid4()),
        "creator": "MartaSarmento",
        "creator_url": "https://freesound.org/people/MartaSarmento",
        "tags": [{"name": "test", "accuracy": 0.9}],
        "created_on": datetime.datetime.now(),
        "foreign_landing_url": "https://freesound.org/people/MartaSarmento/sounds/509257",
        "url": "https://cdn.freesound.org/previews/509/509257_11129467-hq.mp3",
        "genres": ["genre1", "genre2"],
        "category": "test_category",
        "duration": 8544,
        "bit_rate": 128000,
        "sample_rate": None,
        "filesize": 168919,
        "filetype": "mp3",
        "provider": "test",
        "source": "test",
        "license": "cc0",
        "license_version": "1.0",
        "mature": False,
        "meta_data": meta_data,
        "alt_files": [
            {
                "url": "https://freesound.org/apiv2/sounds/509257/download/",
                "bit_rate": "70000",
                "filesize": "75591",
                "filetype": "m4a",
                "sample_rate": "44100",
            }
        ],
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
    return Audio.database_row_to_elasticsearch_doc(row, schema)


def create_mock_image(override=None):
    """
    Produce a mock image.

    Override default fields by passing in a dict with the desired keys and values.
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

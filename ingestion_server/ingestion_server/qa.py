import uuid
import random
from enum import Enum
from ingestion_server.elasticsearch_models import Image


class TaskTypes(Enum):
    TARGET = 1
    LESS_RELEVANT = 2
    NOT_RELEVANT = 3


def create_search_qa_index():
    test_idx = 'search-qa'
    _phrase_relevance(test_idx)


def test_image(title, tags, creator, relevance):
    _id = random.randint(0, 1000000000)
    sample_url = 'https://example.com/'
    img = Image(
        _id=_id,
        id=relevance,
        title=title,
        identifier=str(uuid.uuid4()),
        creator=creator,
        creator_url=sample_url,
        tags=tags,
        created_on=None,
        url=sample_url,
        thumbnail='',
        provider='test',
        source=sample_url,
        license='by',
        license_version='3.0',
        foreign_landing_url=sample_url,
        metadata=None,
        view_count=0
    )
    return img


def _phrase_relevance(index):
    # This should be the top result.
    target_tags = [
        {'name': 'home office'},
        {'name': 'noise'},
        {'name': 'clutter'}
    ]
    target = test_image(
        'My home office', target_tags, 'John Fooson', TaskTypes.TARGET.value
    )
    target.save(index=index)

    less_relevant1 = test_image(
        'A picture of my office',
        [{'name': 'office'}],
        'Alice Foo'
        ,
        TaskTypes.LESS_RELEVANT.value
    )
    less_relevant1.save(index=index)

    less_relevant2 = test_image(
        'My office in my home',
        [{'name': 'office'}, {'name': 'home'}],
        'Gordon',
        TaskTypes.LESS_RELEVANT.value
    )
    less_relevant2.save(index=index)

    not_relevant = test_image(
        'Mastiff', [{'name': 'dog'}], 'Liam', TaskTypes.NOT_RELEVANT.value
    )
    not_relevant.save(index=index)

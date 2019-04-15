import uuid
import random
from ingestion_server.elasticsearch_models import Image


def create_search_qa_index():
    test_idx = 'search-qa'
    _phrase_relevance(test_idx)


def test_image(title, tags, creator):
    _id = random.randint(0, 1000000000)
    sample_url = 'https://example.com/'
    img = Image(
        _id=_id,
        id=_id,
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
    target = test_image('My home office', target_tags, 'John Fooson')
    target.save(index=index)

    less_relevant1 = test_image(
        'A picture of my office',
        [{'name': 'office'}],
        'Alice Foo'
    )
    less_relevant1.save(index=index)

    less_relevant2 = test_image(
        'My office in my home',
        [{'name': 'office'}, {'name': 'home'}],
        'Gordon'
    )
    less_relevant2.save(index=index)


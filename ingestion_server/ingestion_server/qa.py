import random
from enum import Enum

from ingestion_server.elasticsearch_models import Image, Audio


class QAScores(Enum):
    TARGET = 1
    LESS_RELEVANT = 2
    NOT_RELEVANT = 3


def create_search_qa_index(table):
    # This changes search-qa for images to search-qa-image
    test_idx = f'search-qa-{table}'
    if table == 'image':
        _phrase_relevance_images(test_idx)
    elif table == 'audio':
        _phrase_relevance_audio(test_idx)


def _test_doc_attrs(title, tags, creator, relevance):
    _id = random.randint(0, 1000000000)
    sample_url = 'https://example.com/'
    return {
        '_id': _id,
        'id': _id,
        'title': title,
        'identifier': relevance,
        'creator': creator,
        'creator_url': sample_url,
        'tags': tags,
        'created_on': None,
        'url': sample_url,
        'thumbnail': '',
        'provider': 'test',
        'source': sample_url,
        'license': 'by',
        'license_version': '3.0',
        'foreign_landing_url': sample_url,
        'metadata': None,
        'view_count': 0
    }


def _test_image(title, tags, creator, relevance):
    img = Image(**_test_doc_attrs(title, tags, creator, relevance))
    return img


def _test_audio(title, tags, creator, relevance):
    aud = Audio(**_test_doc_attrs(title, tags, creator, relevance))
    return aud


def _phrase_relevance_images(index):
    """
    Creates documents for images with varying relevance in the given index.
    """

    less_relevant_1 = _test_image(
        title='A picture of my office',
        tags=[{'name': 'office'}],
        creator='Alice Foo',
        relevance=QAScores.LESS_RELEVANT.value
    )
    less_relevant_1.save(index=index)

    less_relevant_2 = _test_image(
        title='My office in my home',
        tags=[{'name': 'office'}, {'name': 'home'}],
        creator='Gordon',
        relevance=QAScores.LESS_RELEVANT.value
    )
    less_relevant_2.save(index=index)

    not_relevant = _test_image(
        title='Mastiff',
        tags=[{'name': 'dog'}],
        creator='Liam',
        relevance=QAScores.NOT_RELEVANT.value
    )
    not_relevant.save(index=index)

    # This should be the top result.
    target = _test_image(
        title='My home office',
        tags=[{'name': 'home office'}, {'name': 'noise'}, {'name': 'clutter'}],
        creator='John Fooson',
        relevance=QAScores.TARGET.value
    )
    target.save(index=index)


def _phrase_relevance_audio(index):
    """
    Creates documents for audio with varying relevance in the given index.
    """

    less_relevant_1 = _test_audio(
        title='Symphony No. 1 in C major, Op. 21',
        tags=[{'name': 'symphony'}, {'name': 'c.major'}],
        creator='Ludvig van Beethoven',
        relevance=QAScores.LESS_RELEVANT.value,
    )
    less_relevant_1.save(index=index)

    less_relevant_2 = _test_audio(
        title='Symphony No. 9 in C major, D 944',
        tags=[{'name': 'symphony'}, {'name': 'c.major'}],
        creator='Franz Schubert',
        relevance=QAScores.LESS_RELEVANT.value,
    )
    less_relevant_2.save(index=index)

    not_relevant = _test_audio(
        title='Serenade No. 13 for strings in G major, K. 525',
        tags=[{'name': 'serenade'}, {'name': 'g.major'}],
        creator='Wolfgang Amadeus Mozart',
        relevance=QAScores.NOT_RELEVANT.value,
    )
    not_relevant.save(index=index)

    # This should be the top result.
    target = _test_audio(
        title='Symphony No. 5 in C minor, Op. 67',
        tags=[{'name': 'symphony'}, {'name': 'c.minor'}],
        creator='Ludwig van Beethoven',
        relevance=QAScores.TARGET.value
    )
    target.save(index=index)

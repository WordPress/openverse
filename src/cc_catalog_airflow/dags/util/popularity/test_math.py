import os
import io
import statistics
from datetime import datetime as dt
from datetime import timedelta
from util.popularity.math import generate_popularity_tsv, _validate_percentiles

RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'test_resources'
)


def _parse_normalized_tsv(tsv):
    """
    Convert an output TSV to a more convenient in-memory representation. Each
    row will be mapped to its index.
    """
    rows = tsv.readlines()
    del rows[0]
    row_types = [str, float]
    kv = {}
    for idx, row in enumerate(rows):
        row = row.rstrip()
        vals = row.split('\t')
        for vidx, val in enumerate(vals):
            kv[idx] = row_types[vidx](val)
    return kv


def test_gen_tsv():
    output_tsv = io.StringIO()
    percentiles = {'views': 60, 'global_usage_count': 10}
    pop_fields = ['views', 'global_usage_count']
    with open(os.path.join(RESOURCES, 'mock_popularity_dump.tsv'), 'r') as tsv:
        generate_popularity_tsv(tsv, output_tsv, percentiles, pop_fields)
        output_tsv.seek(0)
    scores = _parse_normalized_tsv(output_tsv)

    # Scores should be floats ranging from 0 to 100.
    for _, score in scores.items():
        assert 0 < score < 100
    # The score of the third row should be the average of the first and second
    assert statistics.mean([scores[0], scores[1]]) == scores[2]


def test_expire_validation():
    mocked = {
        'expires': dt(1928, 12, 7).isoformat(),
        'percentiles': {'views': 1}
    }
    assert not _validate_percentiles(mocked, ['views'])


def test_field_validation_missing_field():
    expires = dt.now() + timedelta(days=1)
    mocked = {
        'expires': expires.isoformat(),
        'percentiles': {
            'views': 1,
        }
    }
    assert not _validate_percentiles(mocked, ['global_usage_count'])
    assert _validate_percentiles(mocked, ['views'])

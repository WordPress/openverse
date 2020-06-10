import csv
import json
import logging as log
import os
import boto3
import botocore
import statistics
from datetime import datetime, timedelta
from numbers import Real
from util.popularity.sql import select_percentiles
"""
In order to improve the quality of images in search results, we want to
generate a score for each image indicating how "popular" it is. Popularity is
loosely defined as how successful it is on its parent platform. Some examples:
    - an image has 20,000 views on Flickr
    - an image has 7 views on Flickr
    - an image has been included in a met exhibition 10 times
    - an image has never been included in an article on Wikipedia
    - an image has been included in 20 different articles

To meaningfully compare these different metrics, we have to "normalize" each
metric – convert each result to a score from 0 to 100. So, the above metrics get
turned into:
    - an image has a score of 98
    - an image has a score of 2
    - an image has a score of 85
    - an image has a score of 0
    - an image has a score of 99

The intuition behind this is that we are trying to determine how much each
sample deviates from the mean.

The exact definitions:
For any given metric, the popularity is given by:
    popularity(x): x / (x + C), where x is the raw metric and C is a constant.

C is computed for each metric with the formula:
    C = ((1 - r / r) * V)
where r is a percentile (e.g. .85) and V is a rth percentile value sampled from
the raw metric.

For example, let's say we are ranking Wikimedia Commons works based on how often
they are included in Wikipedia articles. The 85th percentile for usages in
Wikimedia Commons in our database is 1. So, for Wikimedia Commons, the
score is given by:
    p(x) = x / (x + 0.17647)
where x is the number of times the image has appeared in any article. Something
cited twice will have a score of 0.9189.
    p(2) = (2 / (2 + 0.17647) = 0.918918169

Computing the percentile of each metric is an expensive operation, so we
only recompute it once every few months under the assumption that the
distribution of each metric does not change radically from day to day.
"""


PERCENTILE_S3_BUCKET = os.getenv('PERCENTILE_BUCKET', 'percentiles-cache')

PERCENTILE_FILE = os.getenv('PERCENTILE_FILE', 'percentiles.json')

# The percentile used to compute the normalizing constant
PERCENTILE = 0.85

# Cache provider constant so it doesn't need to be recomputed for every row
constants = {}


def compute_popularity(metric_value: Real, source_constant: Real):
    return metric_value / (metric_value + source_constant)


def compute_constant(percentile: float, percentile_value: Real):
    """
    Compute normalizing constant for each popularity source.
    :param percentile: The target percentile for each source (ex: 0.85)
    :param percentile_value: The value of the percentile (e.g.for
    `percenile=0.85`, this should be the 85th percentile of the metric)
    :return: A float representing the constant 'C' in the popularity formula.
    """
    return ((1 - percentile) / percentile) * percentile_value


def _read_percentiles():
    s3 = boto3.resource('s3')
    try:
        f = s3.Object(PERCENTILE_S3_BUCKET, PERCENTILE_FILE)
        file_content = f.get()['Body'].read().decode('utf-8')
        percentiles = json.loads(file_content)
        return percentiles
    except botocore.exceptions.ClientError:
        log.info('Percentile cache not found.')
        return {}


def _update_percentiles_cache(postgres_conn_id, popularity_fields):
    s3 = boto3.resource('s3')
    _json = {}
    # Don't recompute the cache for 60 days
    cached_date = datetime.utcnow()
    expire_time = timedelta(days=60)
    cache_expires_date = cached_date + expire_time
    _json['expires'] = cache_expires_date.isoformat()
    percentiles = select_percentiles(
        postgres_conn_id, popularity_fields, PERCENTILE
    )
    _json['percentiles'] = percentiles
    log.info(f'New percentiles file: {_json}')
    f = s3.Object(PERCENTILE_S3_BUCKET, PERCENTILE_FILE)
    f.put(Body=bytes(json.dumps(_json).encode('utf-8')))


def _validate_percentiles(percentiles, popularity_fields):
    if not percentiles:
        return False
    valid = True
    for popfield in popularity_fields:
        if popfield not in percentiles['percentiles']:
            log.info('Percentile cache missing expected field. Recomputing.')
            valid = False
    now = datetime.utcnow()
    if datetime.fromisoformat(percentiles['expires']) < now:
        log.info('Percentile cache expired and needs to be recomputed.')
        valid = False
    return valid


def get_percentiles(postgres, popularity_fields, attempts=0):
    """ Return the PERCENTILEth value for each metric in a dictionary. """
    if attempts > 1:
        raise RuntimeError('Failed to generate percentiles file.')
    percentiles = _read_percentiles()
    valid = _validate_percentiles(percentiles, popularity_fields)
    if not percentiles or not valid:
        # If the cache has expired or a field is missing, the cache will be
        # refreshed.
        _update_percentiles_cache(postgres, popularity_fields)
        attempts += 1
        return get_percentiles(postgres, popularity_fields, attempts)
    else:
        return percentiles['percentiles']


def _cache_constant(metric, constant):
    constants[metric] = constant


def _get_constant(metric, percentile, value):
    """ Get the constant from the cache or compute it. """
    try:
        constant = constants[metric]
    except KeyError:
        constant = compute_constant(percentile, value)
        _cache_constant(metric, constant)
    return constant


def generate_popularity_tsv(input_tsv, output_tsv, percentiles, pop_fields):
    """
    Compute the popularity score for each image and save it to a TSV. If there
    are multiple popularity metrics, the average of each normalized score is
    taken.

    :param input_tsv: A file containing raw popularity data.
    :param output_tsv: A file that will serve as the destination for
    normalized popularity data.
    :param percentiles: A dictionary mapping each field to its PERCENTILEth
    value
    :param pop_fields: The fields used to compute the popularity score.
    """
    input_tsv_length = sum(1 for _ in input_tsv) or -1
    progress = 0
    input_tsv.seek(0)
    popularity_tsv = csv.DictReader(input_tsv, delimiter='\t')
    fieldnames = ['identifier', 'normalized_popularity']
    _output_tsv = csv.DictWriter(
        output_tsv, delimiter='\t', fieldnames=fieldnames
    )
    _output_tsv.writeheader()
    for row in popularity_tsv:
        normalized_scores = []
        for metric in pop_fields:
            percentile_value = percentiles[metric]
            constant = _get_constant(
                metric, PERCENTILE, percentile_value
            )
            if metric in row:
                if not row[metric]:
                    continue
                float_metric = float(row[metric])
                normalized = compute_popularity(float_metric, constant) * 100
                normalized_scores.append(normalized)
        popularity = statistics.mean(normalized_scores)
        output_row = {
            'identifier': row['identifier'],
            'normalized_popularity': popularity
        }
        _output_tsv.writerow(output_row)
        progress += 1
        # Log progress every 5%
        checkpoint = round(input_tsv_length / 20) or 1
        if progress % checkpoint == 0:
            log.info(
                f'Popularity calc progress: '
                f'{round((progress / input_tsv_length) * 100)}%'
            )

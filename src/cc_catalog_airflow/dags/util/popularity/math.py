import csv
import json
import logging as log
import os
import statistics
from datetime import datetime, timedelta
from numbers import Real
from util.popularity.sql import select_percentiles


PERCENTILE_FILE_CACHE = os.path.join(
    os.getenv('OUTPUT_DIR', '/tmp/'), 'percentiles.json'
)

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


def get_percentiles(postgres, popularity_fields, attempts=0):
    """ Return the PERCENTILEth value for each metric in a dictionary. """
    if attempts > 1:
        raise RuntimeError('Failed to generate percentiles file.')
    try:
        with open(PERCENTILE_FILE_CACHE, 'r') as percentile_f:
            percentiles = json.load(percentile_f)
            for popfield in popularity_fields:
                if popfield not in percentiles['percentiles']:
                    raise KeyError(
                        f'Expected field missing from popularity percentiles '
                        f'file cache: {popfield}. Actual: {percentiles}'
                    )
            now = datetime.utcnow()
            if datetime.fromisoformat(percentiles['expires']) < now:
                msg = 'Percentile cache expired and needs to be recomputed'
                log.info(msg)
                raise ValueError(msg)
            return percentiles['percentiles']
    except (FileNotFoundError, KeyError, ValueError) as e:
        # If the cache has expired or a field is missing, the cache will be
        # refreshed.
        log.info(f'Recomputing percentiles file because: {e}')
        _compute_percentiles_file(postgres, popularity_fields)
        attempts += 1
        return get_percentiles(postgres, popularity_fields, attempts)


def _compute_percentiles_file(postgres_conn_id, popularity_fields):
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
    with open(PERCENTILE_FILE_CACHE, 'w+') as percentile_f:
        percentile_f.write(json.dumps(_json))


def _cache_constant(provider, metric, constant):
    constants[f'{provider}_{metric}'] = constant


def _get_constant(provider, metric, percentile, value):
    """ Get the constant from the cache or compute it. """
    try:
        constant = constants[f'{provider}_{metric}']
    except KeyError:
        constant = compute_constant(percentile, value)
        _cache_constant(provider, metric, constant)
    return constant


def generate_popularity_tsv(input_tsv, output_tsv, percentiles, pop_fields):
    """
    Compute the popularity score for each image and save it to a CSV. If there
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
                row['provider'], metric, PERCENTILE, percentile_value
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

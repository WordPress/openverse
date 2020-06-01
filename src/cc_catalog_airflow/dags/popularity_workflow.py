import csv
import statistics
import json
import os
from numbers import Real

# The percentile used to compute the normalizing constant
PERCENTILE = 0.85

PERCENTILE_FILE_CACHE = os.path.join(
    os.getenv('OUTPUT_DIR'), 'percentiles.json'
)

# Fields indicating popularity expected in the meta_data column
popularity_fields = [
    'global_usage_count',
    'views'
]

# Cache provider constant so it doesn't need to be recomputed for every row
constants = {}


def _compute_percentiles_file():
    pass


def _get_percentiles():
    try:
        with open(PERCENTILE_FILE_CACHE, 'r') as percentile_f:
            percentiles = json.load(percentile_f)
            return percentiles
    except (FileNotFoundError,):
        _compute_percentiles_file()
        return _get_percentiles()


percentiles = _get_percentiles()


def _cache_constant(provider, metric, constant):
    constants[f'{provider}_{metric}'] = constant


def _get_constant(provider, metric, percentile, value):
    """ Get the constant from the cache or compute it. """
    try:
        constant = constants[f'{provider}_{metric}']
    except KeyError:
        constant = _compute_constant(percentile, value)
        _cache_constant(provider, metric, constant)
    return constant


def _compute_constant(percentile: float, percentile_value: Real):
    """
    Compute normalizing constant for each popularity source.
    :param percentile: The target percentile for each source (ex: 0.85)
    :param percentile_value: The value of the percentile (e.g.for
    `percenile=0.85`, this should be the 85th percentile of the metric)
    :return: A float representing the constant 'C' in the popularity formula.
    """
    return ((1 - percentile) / percentile) * percentile_value


def _compute_popularity(metric_value, source_constant):
    return metric_value / (metric_value + source_constant)


def _generate_popularity_tsv(input_tsv, output_tsv):
    """
    :param input_tsv: A file containing raw popularity data.
    :param output_tsv: A file that will serve as the destination for
    normalized popularity data.
    """
    popularity_tsv = csv.DictReader(input_tsv, delimiter=',')
    fieldnames = ['identifier', 'normalized_popularity']
    output_tsv = csv.DictWriter(
        output_tsv, delimiter='\t', fieldnames=fieldnames
    )
    output_tsv.writeheader()
    for idx, row in enumerate(popularity_tsv):
        if idx == 0:
            continue
        normalized_scores = []
        for metric in popularity_fields:
            percentile_value = percentiles[metric]
            constant = _get_constant(
                row['provider'], metric, PERCENTILE, percentile_value
            )
            if metric in row:
                if not row[metric]:
                    continue
                float_metric = float(row[metric])
                normalized = _compute_popularity(float_metric, constant) * 100
                normalized_scores.append(normalized)
        popularity = statistics.mean(normalized_scores)
        output_row = {
            'identifier': row['identifier'],
            'normalized_popularity': popularity
        }
        output_tsv.writerow(output_row)

import os
import logging as log
from util.popularity.sql import (
    upload_normalized_popularity, build_popularity_dump_query,
    dump_selection_to_tsv
)
from util.popularity.math import (
    generate_popularity_tsv, get_percentiles
)

# The fields in the `meta_data` column that factor into the popularity data
# calculation.
popularity_fields = [
    'global_usage_count',
    'views'
]

DB_CONN_ID = os.getenv('OPENLEDGER_CONN_ID', 'postgres_openledger_testing')

POPULARITY_DUMP_DEST = os.path.join(
    os.getenv('OUTPUT_DIR'), 'popularity_dump.tsv'
)
NORMALIZED_POPULARITY_DEST = os.path.join(
    os.getenv('OUTPUT_DIR'), 'normalized_popularity_dump.tsv'
)


def main():
    log.info('Starting popularity job. Fetching percentiles. . .')
    percentiles = get_percentiles(DB_CONN_ID, popularity_fields)
    dump_query = build_popularity_dump_query(popularity_fields)
    log.info('Creating TSV of popularity data. . .')
    with open(POPULARITY_DUMP_DEST, 'w+') as in_tsv, \
            open(NORMALIZED_POPULARITY_DEST, 'w+') as out_tsv:
        dump_selection_to_tsv(DB_CONN_ID, dump_query, POPULARITY_DUMP_DEST)
        log.info('Normalizing popularity data. . .')
        generate_popularity_tsv(in_tsv, out_tsv, percentiles, popularity_fields)
        log.info('Finished normalizing popularity scores. Uploading. . .')
        upload_normalized_popularity(DB_CONN_ID, NORMALIZED_POPULARITY_DEST)
        log.info('Popularity normalization complete.')

"""
This module has a couple of temporarily-needed methods to add an
ingestion_type column to TSV files before uploading them to S3 or
PostgreSQL.
"""
import logging
import os
logger = logging.getLogger(__name__)


def check_and_fix_tsv_file(tsv_file_name):
    """
    This function will check whether a TSV has the right number of
    columns for the new DB schema, and attempt to add an ingestion_type
    column if the number is one short.

    It will also log a warning if the number is completely wrong.
    """
    logger.info(f'Checking for ingestion_type column in {tsv_file_name}')
    old_cols_number = 17
    new_cols_number = old_cols_number + 1
    with open(tsv_file_name) as f:
        test_line = f.readline()
    line_list = [word.strip() for word in test_line.split('\t')]
    if len(line_list) == old_cols_number:
        _add_ingestion_type(tsv_file_name, line_list[-1])
    elif len(line_list) == new_cols_number:
        logger.info(
            f'Found correct number of columns:  {new_cols_number}.'
            '  Leaving file unchanged.'
        )
    else:
        logger.warning(
            'Wrong number of columns in file!  This cannot be fixed...'
        )


def _add_ingestion_type(tsv_file_name, source):
    COMMON_CRAWL = 'commoncrawl'
    PROVIDER_API = 'provider_api'
    ingestion_type = source if source == COMMON_CRAWL else PROVIDER_API
    logger.debug(f'Found source:  {source}')
    logger.info(
        f'Adding ingestion_type:  {ingestion_type} to {tsv_file_name}'
    )
    temp_tsv = tsv_file_name + '.new'
    with open(tsv_file_name, 'r') as old_tsv, open(temp_tsv, 'w') as new_tsv:
        old_line = old_tsv.readline().strip()
        while old_line:
            if ingestion_type == COMMON_CRAWL:
                line_list = [word.strip() for word in old_line.split('\t')]
                new_tsv.write(
                    '\t'.join(line_list[:-1] + line_list[-2:]) + '\n'
                )
            else:
                new_tsv.write(old_line + '\t' + ingestion_type + '\n')
            old_line = old_tsv.readline().strip()

    os.rename(tsv_file_name, tsv_file_name + '.old')
    os.rename(temp_tsv, tsv_file_name)

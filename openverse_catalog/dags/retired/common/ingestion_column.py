"""
This module has a method necessary to add an
ingestion_type column to TSV files before uploading them to S3 or
PostgreSQL. This is used for legacy TSV versions which did not have
ingestion_type column
"""
import logging
import os


logger = logging.getLogger(__name__)


def _fix_ingestion_column(filepath: str) -> None:
    """The oldest TSV files have no `ingestion_type` column"""

    logger.info(f"File to fix: {filepath}")
    with open(filepath) as f:
        test_line = f.readline().strip()
    columns = test_line.split("\t")
    column_count = len(columns)
    old_cols_number = 17
    new_cols_number = old_cols_number + 1
    if column_count == new_cols_number:
        return
    elif column_count != old_cols_number:
        logger.warning(
            f"Wrong number of columns ({column_count}) "
            f"for a legacy TSV file. Cannot fix the file..."
        )
        raise TypeError(f"Wrong number of columns ({column_count}) for TSV")
    source = columns[-1]
    ingestion_type = source if source == "commoncrawl" else "provider_api"
    logger.info(f"Adding ingestion type {ingestion_type} to {filepath}")
    temp_tsv = filepath + ".new"
    with open(filepath, "r") as old_tsv, open(temp_tsv, "w") as new_tsv:
        old_line = old_tsv.readline().strip()
        while old_line:
            if ingestion_type == "commoncrawl":
                line_list = [word.strip() for word in old_line.split("\t")]
                new_tsv.write("\t".join(line_list[:-1] + line_list[-2:]) + "\n")
            else:
                new_tsv.write(old_line + "\t" + ingestion_type + "\n")
            old_line = old_tsv.readline().strip()

    os.rename(filepath, filepath + ".old")
    os.rename(temp_tsv, filepath)

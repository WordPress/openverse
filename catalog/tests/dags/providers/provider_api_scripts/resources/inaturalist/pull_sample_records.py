"""
Some hacky code to pull sample data from large TSV files from inaturalist.

First download the full datasets from aws s3://inaturalist-open-data/, and adjust
RAW_DATA to fit where you saved them.
Assumes that large files are saved outside of the Openverse repo to take pressure off
git and linting.
"""

import csv
import gzip
import os
from datetime import datetime as dt
from pathlib import Path

import pandas as pd


# Because this is unlikely to be reused, I didn't want to change the git ignore
BASE_DIR = Path(__file__).parents[7]
DATA_FOR_TESTING = BASE_DIR / "openverse-catalog/tests/s3-data/inaturalist-open-data"
RAW_DATA = BASE_DIR / "inaturalist-june-22"
MID_SIZE_FILE_PATH = BASE_DIR / "inaturalist-june-22/mid-sized"
SMALL_FILE_PATH = BASE_DIR / "inaturalist-june-22/small"


def pull_sample_records(
    file_name,
    id_name,
    id_list,
    is_unique=True,
    every_nth_record=None,
    output_path=MID_SIZE_FILE_PATH,
    input_path=RAW_DATA,
):
    """
    Read through a full gzip file and keeps just the selected ID records

    This is not wildly efficient for large ID lists and large files.
    """
    # can we read the stuff? (should assert that id_name is a valid field name, but...)
    assert len(id_list) > 0
    assert len(id_list) < 10000
    working_input_file = input_path / file_name
    assert os.path.exists(working_input_file)
    output_file_name = output_path / file_name
    # read in the selected records
    sample_records = []
    remaining_ids = set(id_list)
    print(
        "Starting to read",
        working_input_file,
        "at",
        dt.now().strftime("%d/%m/%Y %H:%M:%S"),
    )
    with gzip.open(working_input_file, "rt") as in_file:
        records = csv.DictReader(in_file, delimiter="\t")
        lines_read = 0
        keep_random = False
        for record in records:
            if every_nth_record:
                keep_random = lines_read % every_nth_record == 0
            if (record[id_name] in remaining_ids) or keep_random:
                sample_records += [record]
                if is_unique:
                    remaining_ids.remove(record[id_name])
            lines_read += 1
            if lines_read % 10**7 == 0:
                print(
                    "Read line number",
                    lines_read,
                    "at",
                    dt.now().strftime("%d/%m/%Y %H:%M:%S"),
                )
    # write them to the sample output file
    sample_df = pd.DataFrame(sample_records)
    with gzip.open(output_file_name, "wt") as out_file:
        sample_df.to_csv(out_file, sep="\t", header=True, index=False)
    print(len(sample_df), "sample records saved in", output_file_name)
    return output_file_name


def get_sample_id_list(sample_file, joined_on):
    """
    sample_file:    from a table that you have already drawn sample records
                    a file object so that you can handle if it's compressed or not, set
                    up to read text
    joined_on:      the string name of the field they have in common
    """
    records = csv.DictReader(sample_file, delimiter="\t")
    sample_values = set()
    for record in records:
        sample_values.add(record[joined_on])
    return sample_values


if __name__ == "__main__":
    # PHOTOS
    photo_ids = [
        str(i)
        for i in [
            20314159,
            10314159,
            30314159,
            40314159,
            60314159,
            80314159,
            90314159,
            110314159,
            120314159,
            130314159,
            150314159,
            160314159,
            170314159,
            191019692,
            191018903,
            191018870,
            191016506,
            191015547,
            191015484,
            191012628,
            191001500,
            190995656,
            190995604,
            191028942,
            191028931,
            191024617,
            200352737,
        ]
    ]
    pull_sample_records(
        file_name="photos.csv.gz",
        id_name="photo_id",
        id_list=photo_ids,
        is_unique=False,
        every_nth_record=50_000,
        output_path=MID_SIZE_FILE_PATH,
    )

    # ASSOCIATED OBSERVATIONS
    with gzip.open(f"{MID_SIZE_FILE_PATH}/photos.csv.gz", "rt") as photo_output:
        sample_observations = get_sample_id_list(photo_output, "observation_uuid")
    pull_sample_records(
        "observations.csv.gz",
        "observation_uuid",
        sample_observations,
        False,
        None,
        MID_SIZE_FILE_PATH,
    )

    # ASSOCIATED OBSERVERS
    with gzip.open(f"{MID_SIZE_FILE_PATH}/photos.csv.gz", "rt") as photo_output:
        sample_observers = get_sample_id_list(photo_output, "observer_id")
    pull_sample_records(
        "observers.csv.gz",
        "observer_id",
        sample_observers,
        False,
        None,
        MID_SIZE_FILE_PATH,
    )

    # ASSOCIATED TAXA (including ancestry for photo tags)
    with gzip.open(
        f"{MID_SIZE_FILE_PATH}/observations.csv.gz", "rt"
    ) as observation_output:
        sample_taxa = get_sample_id_list(observation_output, "taxon_id")
    sample_taxa_with_ancestors = set(sample_taxa)
    with gzip.open(f"{RAW_DATA}/taxa.csv.gz", "rt") as all_taxa:
        records = csv.DictReader(all_taxa, delimiter="\t")
        for t in records:
            if t["taxon_id"] in sample_taxa:
                sample_taxa_with_ancestors.update(t["ancestry"].split("/"))
    pull_sample_records(
        "taxa.csv.gz",
        "taxon_id",
        list(sample_taxa_with_ancestors),
        False,
        None,
        MID_SIZE_FILE_PATH,
    )

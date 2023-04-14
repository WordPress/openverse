"""
Couple of additional data quality checks before merging this PR
https://github.com/WordPress/openverse-catalog/pull/745
"""

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).parents[7]
FULL_DOWNLOADS = BASE_DIR / "inaturalist-downloads/dec-2022"
PHOTOS_CSV = FULL_DOWNLOADS / "photos.csv.gz"
OBSERVERS_CSV = FULL_DOWNLOADS / "observers.csv.gz"


observers = pd.read_csv(OBSERVERS_CSV, delimiter="\t")
print(f"The file has {len(observers)} observer records, and")
print(observers[["login", "name"]].count())
# # results 1/13/2023
# The file has 589290 observer records, and
# login    589290
# name     107840

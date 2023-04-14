"""
Ad hoc exploratory analysis for identifying test cases for the API workflow.
To execute this, download MetObjects.csv from here:
https://github.com/metmuseum/openaccess/blob/master/MetObjects.csv
"""

from pathlib import Path
from time import sleep

import pandas as pd
import requests


pd.set_option("display.min_rows", 500)
pd.set_option("display.width", None)

DIR = Path(__file__).parent
raw_data_file_name = "MetObjects.csv"

raw_data = pd.read_csv(
    DIR / raw_data_file_name,
    header=0,
    usecols=[
        "Is Public Domain",
        "Object ID",
        "Object Number",
        "Department",
        "Object Name",
        "Title",
        "Culture",
        "Artist Display Name",
        "Medium",
        "Credit Line",
        "Classification",
        "Link Resource",
        "Tags",
        "Period",
        "Object Date",
        "Artist Wikidata URL",
        "Artist ULAN URL",
    ],
)

# *** object_number is never missing.
# is_highlight is never missing.
# is_timeline_work is never missing.
# gallery_number is missing 85% of values, see 860873
# *** department is never missing.
# accessionyear is missing 0% of values, see 854659
# *** object_name is missing 0% of values, see 854659
# *** title is missing 10% of values, see 856958
# *** culture is missing 42% of values, see 860873
# --> period is missing 71% of values, see 860873
# dynasty is missing 95% of values, see 860873
# reign is missing 97% of values, see 860873
# portfolio is missing 96% of values, see 860873
# constituent_id is missing 56% of values, see 857718
# artist_role is missing 57% of values, see 857718
# artist_prefix is missing 56% of values, see 857718
# *** artist_display_name is missing 56% of values, see 857718
# artist_display_bio is missing 57% of values, see 857718
# artist_suffix is missing 56% of values, see 857718
# artist_alpha_sort is missing 56% of values, see 857718
# artist_nationality is missing 56% of values, see 857718
# artist_begin_date is missing 56% of values, see 857718
# artist_end_date is missing 56% of values, see 857718
# artist_gender is missing 86% of values, see 860873
# artist_ulan_url is missing 64% of values, see 860873
# artist_wikidata_url is missing 65% of values, see 860873
# --> object_date is missing 3% of values, see 856790
# object_begin_date is never missing.
# object_end_date is never missing.
# *** medium is missing 0% of values, see 854659
# dimensions is missing 13% of values, see 856203
# *** credit_line is missing 0% of values, see 853970
# geography_type is missing 84% of values, see 860873
# city is missing 93% of values, see 860873
# state is missing 99% of values, see 860873
# county is missing 97% of values, see 860873
# country is missing 81% of values, see 860873
# region is missing 92% of values, see 860873
# subregion is missing 94% of values, see 860873
# locale is missing 96% of values, see 860873
# locus is missing 98% of values, see 860873
# excavation is missing 96% of values, see 860873
# river is missing 99% of values, see 860873
# *** classification is missing 13% of values, see 854659
# rights_and_reproduction is missing 99% of values, see 860873
# *** link_resource is never missing.
# object_wikidata_url is missing 93% of values, see 860873
# metadata_date is always missing.
# --> repository is never missing, but 1 val: 'Metropolitan Museum of Art, New York, NY'
# *** tags is missing 41% of values, see 857718
# tags_aat_url is missing 41% of values, see 857718
# tags_wikidata_url is missing 41% of values, see 857718

new_column_names = {col: col.lower().replace(" ", "_") for col in raw_data.columns}
raw_data.rename(columns=new_column_names, inplace=True)

print("--> Column names:", "\n".join(raw_data.columns), sep="\n")
print("--> Licensing:", raw_data.is_public_domain.value_counts(dropna=False), sep="\n")

raw_data.set_index("object_id", inplace=True)
raw_data.drop(raw_data[raw_data["is_public_domain"] == 0].index, inplace=True)
raw_data.drop(["is_public_domain"], axis=1, inplace=True)

raw_data["possible_creator_url"] = raw_data.artist_ulan_url.fillna(
    raw_data.artist_wikidata_url
)

total_records = len(raw_data)
print(f"--> Total CC0 records: {total_records}")
print("--> Percent populated for different fields...")
sample_cases = set()
for c in raw_data.columns:
    m = raw_data[c].isna().sum()
    if m == total_records:
        print(f"{c} is always missing.")
    elif m > 0:
        example = max(raw_data[raw_data[c].isna()].index)
        sample_cases.add(example)
        print(f"{c} is missing {int(100.0*m/total_records)}% of values, see {example}")
    else:
        print(f"{c} is never missing.")

# add existing test cases
sample_cases = sample_cases.union([45733, 45734, 1027])
# from https://github.com/WordPress/openverse-catalog/issues/641
sample_cases = sample_cases.union([855619, 479, 747045, 5915, 4542])

for object_id in sample_cases:
    print(f"Requesting {object_id}... ", end="")
    file_name = f"sample_response_{object_id}.json"
    object_url = (
        f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"
    )
    response = requests.get(object_url)
    if response.json():
        with open(DIR / file_name, "w") as f:
            f.write(response.text)
        print(":) YAY!")
    else:
        print(":( no response")
    sleep(5)

print("handle missing titles...")
print(
    raw_data[["title", "object_name", "classification", "artist_display_name"]].query(
        "not(title == title)"
    )
)

print("artist display names...")
print(
    raw_data.query(
        "artist_display_name == 'Unidentified' "
        + "or artist_display_name == 'Unidentified artist'"
    ).artist_display_name.value_counts()
)

print("medium...")
print(raw_data.medium.value_counts())

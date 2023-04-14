from pathlib import Path

import pandas as pd


EXTERNAL_ROOT = Path(__file__).parents[7]

# catalog of life data downloaded manually from
# https://api.checklistbank.org/dataset/9840/export.zip?format=ColDP
# renamed, and stored in this folder
SOURCE_DATA_PATH = EXTERNAL_ROOT / "inaturalist-june-22/catalog_of_life"
local_zip_file = "COL_archive.zip"
name_usage_file = "NameUsage.tsv"
vernacular_file = "VernacularName.tsv"


# prettying up the output
def print_header(header):
    padding = int((88 - len(header)) / 2)
    print("\n", "=" * padding, header, "=" * padding)


# handle common formatting for reading these files
def load_to_pandas(file_name):
    df = pd.read_csv(
        SOURCE_DATA_PATH / file_name,
        delimiter="\t",
        quotechar="\b",
    )
    df.columns = [c[4:] for c in df.columns]
    return df


# Just for an overview
def basic_stats(df, df_name):
    print_header(df_name)
    num_records = len(df)
    print(f"{num_records=}")
    col_width = max([len(c) for c in df.columns])
    for c in df.columns:
        col_padding = col_width - len(c)
        print("  ", c, " " * col_padding, num_records - df[c].isna().sum())


# Can't remember if pd can read a specific file within a zip file, so unzipping first
# with zipfile.ZipFile(SOURCE_DATA_PATH / local_zip_file) as z:
#     with open(SOURCE_DATA_PATH / name_usage_file, "wb") as f:
#         f.write(z.read(name_usage_file))
#     with open(SOURCE_DATA_PATH / vernacular_file, "wb") as f:
#         f.write(z.read(vernacular_file))
NameUsageDF = load_to_pandas(name_usage_file)
basic_stats(NameUsageDF, "NameUsageDF")

VernacularDF = load_to_pandas(vernacular_file)
basic_stats(VernacularDF, "VernacularDF")

JoinedDF = (
    VernacularDF[
        [
            "name",
            "language",
            "sourceID",
            "taxonID",
        ]
    ]
    .merge(
        NameUsageDF[
            [
                "ID",
                "scientificName",
                "scrutinizerDate",
                "temporalRangeEnd",
                "genericName",
            ]
        ],
        how="inner",
        left_on="taxonID",
        right_on="ID",
    )
    .drop(columns=["ID"])
)
basic_stats(JoinedDF, "JoinedDF")

print_header("Name Usage IDs")
print("Length\n", NameUsageDF.ID.str.len().value_counts())
print("Is Numeric\n", NameUsageDF.ID.str.isnumeric().value_counts())
print(
    f"Max length of a taxon id in the vernacular table is "
    f"{max(VernacularDF.taxonID.str.len())}"
)
print(
    "ID outlier(s)\n",
    NameUsageDF.loc[
        NameUsageDF.ID.str.len() > max(VernacularDF.taxonID.str.len()), "ID"
    ],
)

print_header("Vernacular Name Counts")
total_names = JoinedDF.scientificName.value_counts()
english_names = JoinedDF.loc[
    JoinedDF.language == "eng", :
].scientificName.value_counts()
# name_stats = pd.merge(total_names, english_names, how="left")
# print(len(name_stats))
print(
    f"{len(total_names)} scientificName values, "
    f"{len(english_names)} have English names."
)
print("Total name counts\n", total_names.value_counts().sort_index())
print("English name counts\n", english_names.value_counts().sort_index())

print_header("Length of / joining on Scientific Name")
print(JoinedDF.scientificName.str.len().value_counts().sort_index())

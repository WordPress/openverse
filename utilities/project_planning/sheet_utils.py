from pathlib import Path

import pandas as pd


def read_file(input_file: Path) -> tuple[dict[str, pd.DataFrame], pd.Series]:
    """
    Read a structured input excel document and return the various frames and a
    list of projects from it. This makes several assumptions about the format of the
    file, namely that 5 rows should be skipped, that the document has a "Template" sheet
    that can be used for determine the project lists, and that the project lists
    are in a column called "Name".
    """
    print(f"Reading input file: {input_file}")
    # Read the input file
    frames = pd.read_excel(
        input_file,
        # Include all sheets
        sheet_name=None,
        # Skip the first 5 rows, which are the instructional text
        skiprows=5,
        # Use the first row as the header
        header=0,
    )
    # Pull the project names out of the template sheet
    projects = frames["Template"]["Name"]

    return frames, projects


def get_columns_by_members(
    frames: dict[str, pd.DataFrame],
    members: list[str],
    projects: pd.Series,
    column: str,
):
    """
    Create a new DataFrame which pulls out the provided column from each of the member
    sheets, and sets the index to the project names.
    """
    data = pd.DataFrame([frames[name][column] for name in members], index=members)
    # The data is transposed here because the DataFrame constructor creates a DataFrame
    # with the projects as the columns, and the members as the index, whereas we want
    # the projects as the index.
    return data.T.set_index(projects)

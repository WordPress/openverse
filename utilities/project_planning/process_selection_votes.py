"""
Script for gathering project selection votes and sharing the results

See the README for more information.
"""

from datetime import datetime
from pathlib import Path

import click
import pandas as pd
import sheet_utils


INPUT_FILE = Path(__file__).parent / "data" / "selection_votes.xlsx"

COLUMN_VOTED = "Included"
SKIP_SHEETS = {
    # Ignore the template sheet
    "Template",
    # Ignore the reference
    "_ref",
    # If present, ignore the team's final decisions
    "Team",
}


def _print_series(s: pd.Series) -> None:
    """Shorthand for printing a series"""
    for name, count in s.items():
        print(f"{name} ({count})")


@click.command()
@click.option(
    "--input-file",
    help="Input Excel document to use",
    type=click.Path(path_type=Path),
    default=INPUT_FILE,
)
def main(input_file: Path):
    frames, projects = sheet_utils.read_file(input_file)
    members = list(set(frames.keys()) - SKIP_SHEETS)

    # Get the "voted for" column
    included = sheet_utils.get_columns_by_members(
        frames, members, projects, COLUMN_VOTED
    )
    # This is planning for the *next* year, e.g. one beyond the current one
    datetime.now().year + 1

    # Get the sum of all the "Yes" votes for each project
    votes = included.eq("Yes").sum(axis=1)

    # Bin by certain ranges
    all_voted = votes[votes == 7]
    most_voted = votes[(votes >= 4) & (votes < 7)].sort_values(ascending=False)
    some_voted = votes[(votes >= 2) & (votes < 4)].sort_values(ascending=False)
    few_no_voted = votes[votes <= 1].sort_values(ascending=False)

    # Print results
    print("\n### Projects everyone voted for")
    _print_series(all_voted)
    print("\n### Projects most voted for (4-6)")
    _print_series(most_voted)
    print("\n### Projects some voted for (2-3)")
    _print_series(some_voted)
    print("\n### Projects 1 or nobody voted for (0-1)")
    _print_series(few_no_voted)


if __name__ == "__main__":
    main()

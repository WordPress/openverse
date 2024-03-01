"""
Script for generating average weeks of work based on estimations made by all team
members.

See the README for more information.
"""

from pathlib import Path

import click
import pandas as pd
import sheet_utils


INPUT_FILE = Path(__file__).parent / "data" / "week_votes.xlsx"
OUTPUT_PATH = Path(__file__).parent / "output"

COLUMN_WEEKS = "Total weeks"
COLUMN_CONFIDENCE = "Confidence (1-3)"
SKIP_SHEETS = {
    # Ignore the template sheet
    "Template",
    # Design hours were provided separate from dev hours and will be used elsewhere
    "Francisco",
}


def calculate_weighted_average(
    weeks: pd.DataFrame, confidence: pd.DataFrame
) -> pd.DataFrame:
    """
    Use the confidence values provided to compute a weighted average, first by averaging
    all values that share the same confidence score, then by performing a conditional
    weighted average. The weighting is conditional because not all projects have votes
    across all 3 confidence values (for instance, a large complex project only having
    confidence values 2 and 1).
    """
    # Average the 3 votes, 2 votes and 1 votes individually
    high_confidence_avg = weeks[confidence == 3].mean(axis=1).fillna(0)
    med_confidence_avg = weeks[confidence == 2].mean(axis=1).fillna(0)
    low_confidence_avg = weeks[confidence == 1].mean(axis=1).fillna(0)

    # Mask for determining weighted sum
    high_mask = (high_confidence_avg > 0) * 3
    med_mask = (med_confidence_avg > 0) * 2
    low_mask = (low_confidence_avg > 0) * 1

    # Compute the weighted average across rows, using the sum (if it exists!) of
    # weights across that row
    weighted_average_weeks = (
        high_confidence_avg * 3 + med_confidence_avg * 2 + low_confidence_avg * 1
    ) / (high_mask + med_mask + low_mask)
    return weighted_average_weeks.round().astype(int)


def _write_file(data: pd.DataFrame, filename: str) -> None:
    """Small wrapper for writing dataframes for this script."""
    path = OUTPUT_PATH / filename
    print(f"Writing file to {path}")
    data.to_csv(path, header=True)


@click.command()
@click.option(
    "--output",
    help="Output directory",
    type=click.Path(path_type=Path),
    default=OUTPUT_PATH,
)
@click.option(
    "--input-file",
    help="Input Excel document to use",
    type=click.Path(path_type=Path),
    default=INPUT_FILE,
)
def main(output: Path, input_file: Path):
    # Ensure the output folder exists
    output.mkdir(parents=True, exist_ok=True)

    frames, projects = sheet_utils.read_file(input_file)
    members = list(set(frames.keys()) - SKIP_SHEETS)

    weeks = sheet_utils.get_columns_by_members(frames, members, projects, COLUMN_WEEKS)
    confidence = sheet_utils.get_columns_by_members(
        frames, members, projects, COLUMN_CONFIDENCE
    )

    average_weeks = weeks.mean(axis=1).round().astype(int)
    weighted_average_weeks = calculate_weighted_average(weeks, confidence)

    _write_file(average_weeks, "average_weeks.csv")
    _write_file(weighted_average_weeks, "weighted_average_weeks.csv")


if __name__ == "__main__":
    main()

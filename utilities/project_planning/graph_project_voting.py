"""
Script for generating graphs of project voting results.

See the README for more information.
"""
from datetime import datetime
from pathlib import Path

import click
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import pandas as pd


INPUT_FILE = Path(__file__).parent / "data" / "votes.xlsx"
OUTPUT_PATH = Path(__file__).parent / "output"

COLUMN_EFFORT = "Effort (fib)"
COLUMN_IMPACT = "Impact (fib)"
COLUMN_CONFIDENCE = "Confidence (1-3)"


def get_columns_by_members(
    frames: dict[str, pd.DataFrame],
    members: list[str],
    projects: pd.Series,
    column: str,
):
    data = pd.DataFrame([frames[name][column] for name in members], index=members)
    return data.T.set_index(projects)


def plot_votes(
    data: pd.DataFrame, color_by: pd.Series, column: str, year: int, output_path: Path
):
    ax, bp = data.T.boxplot(
        figsize=(10, 10),
        showfliers=False,
        patch_artist=True,
        return_type="both",
    )
    # Set the x-axis labels vertically
    ax.set_xticklabels(ax.get_xmajorticklabels(), rotation=90)
    # Only show the labeled values on the y-axis
    plt.yticks([2, 3, 5, 8, 13])
    # Set the title
    ax.set_title(f"Vote Distribution: {column} - {year}")
    # Create a colormap that transitions from red to green
    cmap = mcolors.LinearSegmentedColormap.from_list("", ["red", "lime"])
    # Create a color normalizer.
    norm = mcolors.Normalize(vmin=1, vmax=3)
    # Apply colors to each box plot.
    for i, color_value in enumerate(color_by.values):
        color = cmap(norm(color_value))
        # Get current box
        box = bp["boxes"][i]
        # Set box face color
        box.set_facecolor(color)
        # Change color of the whiskers
        for whisker in bp["whiskers"][i * 2 : (i + 1) * 2]:
            whisker.set_color(color)
            whisker.set_linewidth(2)
        # Change color of the caps
        for cap in bp["caps"][i * 2 : (i + 1) * 2]:
            cap.set_color(color)
            cap.set_linewidth(2)

    plt.tight_layout()
    output_file = output_path / f"{column.split()[0]}_{year}.png"
    print(f"Saving file {output_file}")
    plt.savefig(output_file)


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
    output.mkdir(parents=True, exist_ok=True)

    print(f"Reading input file: {input_file}")
    frames = pd.read_excel(input_file, sheet_name=None, header=0, skiprows=5)
    projects = frames["Template"]["Name"]
    members = list(frames.keys())[1:]
    planning_year = datetime.now().year + 1

    effort = get_columns_by_members(frames, members, projects, COLUMN_EFFORT)
    impact = get_columns_by_members(frames, members, projects, COLUMN_IMPACT)
    confidence = get_columns_by_members(frames, members, projects, COLUMN_CONFIDENCE)
    average_confidence = confidence.mean(axis=1)

    plot_votes(effort, average_confidence, COLUMN_EFFORT, planning_year, output)
    plot_votes(impact, average_confidence, COLUMN_IMPACT, planning_year, output)


if __name__ == "__main__":
    main()

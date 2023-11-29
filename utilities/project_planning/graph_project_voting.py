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
import sheet_utils


INPUT_FILE = Path(__file__).parent / "data" / "votes.xlsx"
OUTPUT_PATH = Path(__file__).parent / "output"

COLUMN_EFFORT = "Effort (fib)"
COLUMN_IMPACT = "Impact (fib)"
COLUMN_CONFIDENCE = "Confidence (1-3)"


def plot_votes(
    data: pd.DataFrame, color_by: pd.Series, column: str, year: int, output_path: Path
):
    """
    Create and save a box plot of the provided data, with the boxes colored by the
    provided color_by data.
    """
    # Create the box plot
    ax, bp = data.T.boxplot(
        # Specify a large figure size to both increase the resolution of the image, and
        # provide enough space for the x-axis labels.
        figsize=(10, 10),
        # Specific parameter needed in order to color the boxes
        patch_artist=True,
        # Return both the axes and boxplot objects, rather than just the axes
        return_type="both",
    )
    # Set the x-axis labels (project names) vertically to prevent collision
    ax.set_xticklabels(ax.get_xmajorticklabels(), rotation=90)
    # Only show the Fibonacci values labeled on the y-axis
    plt.yticks([2, 3, 5, 8, 13])
    # Set the title of the graph
    ax.set_title(f"Vote Distribution: {column} - {year}")
    # Create a colormap that transitions from red to green (lime is used specifically
    # because it creates a more vibrant green than green does).
    cmap = mcolors.LinearSegmentedColormap.from_list("", ["red", "lime"])
    # Create a color normalizer (confidence values are between 1 and 3)
    norm = mcolors.Normalize(vmin=1, vmax=3)
    # Apply colors to each box plot.
    for i, color_value in enumerate(color_by.values):
        # Compute the color using the colormap and normalizer
        color = cmap(norm(color_value))
        # Get current box
        box = bp["boxes"][i]
        # Set box face color
        box.set_facecolor(color)
        # Change color of the whiskers & caps (the actual list of each is twice as long
        # as # the number of boxes, because there are two each per box)
        for aspect_name in ["whiskers", "caps"]:
            for aspect in bp[aspect_name][i * 2 : (i + 1) * 2]:
                aspect.set_color(color)
                aspect.set_linewidth(2)

    # This is required in order to ensure nothing is cut off
    plt.tight_layout()
    output_file = output_path / f"{column.split()[0]}_{year}.png"
    print(f"Saving file {output_file}")
    plt.savefig(output_file)
    # Clear the figure so the next one starts fresh
    plt.close()


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

    # Use the name of the frames as the list of voting members
    members = list(frames.keys())[1:]
    # This is planning for the *next* year, e.g. one beyond the current one
    planning_year = datetime.now().year + 1

    effort = sheet_utils.get_columns_by_members(
        frames, members, projects, COLUMN_EFFORT
    )
    impact = sheet_utils.get_columns_by_members(
        frames, members, projects, COLUMN_IMPACT
    )
    confidence = sheet_utils.get_columns_by_members(
        frames, members, projects, COLUMN_CONFIDENCE
    )
    average_confidence = confidence.mean(axis=1)

    plot_votes(effort, average_confidence, COLUMN_EFFORT, planning_year, output)
    plot_votes(impact, average_confidence, COLUMN_IMPACT, planning_year, output)


if __name__ == "__main__":
    main()

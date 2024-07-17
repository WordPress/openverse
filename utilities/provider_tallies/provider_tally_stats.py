"""
Retrieves provider result tallies from Openverse API Redis.

This script assumes that the API Redis instance you care about is present
on localhost (usually via tunneling). It will run through the provider result count
entries in Redis and output them to CSV.
"""

import pprint
from datetime import datetime
from pathlib import Path

import click
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from redis import Redis


MATCH_PREFIX = "provider*"
TALLY_DATABASE = 3
COLUMNS = ["match_type", "media_type", "start_of_week", "provider", "count"]


def handle_matches(matches, redis: Redis, tallies, errors):
    values = redis.mget(matches)
    for value, match in zip(values, matches):
        try:
            # The match is of the form
            # "provider_<match_type>:<media_type>:<start_of_week>:<provider>"
            tallies.append((*match.split(":"), value))
        except Exception as e:
            errors[value] = e


def _format_name(value: str) -> str:
    return value.replace("_", " ").title()


@click.command()
@click.option(
    "--output",
    help="Output directory",
    type=click.Path(path_type=Path),
    default=Path(__file__).parent,
)
@click.option(
    "--start-date",
    help="Start date for the tally, in the form of YYYY-MM-DD. "
    "Results in Redis are grouped by the start of the week.",
    type=str,
)
def main(output: Path, start_date: str | None):
    redis = Redis("localhost", port=6399, decode_responses=True, db=TALLY_DATABASE)
    cursor = 0
    should_continue = True
    iter_count = 1
    run_date = datetime.now().strftime("%Y-%m-%d")

    tallies = []
    errors = dict()

    while should_continue:
        cursor, matches = redis.scan(cursor=cursor, match=MATCH_PREFIX, count=250)
        handle_matches(matches, redis, tallies, errors)
        iter_count += 1
        if iter_count % 10 == 0:
            print(f"Processed {iter_count * 250} matches, cursor @ {cursor}")
        should_continue = cursor != 0

    df = pd.DataFrame(tallies, columns=COLUMNS)
    df = df.sort_values(by=COLUMNS[:4])
    df["count"] = df["count"].astype(int)
    if start_date:
        df = df[df["start_of_week"] >= start_date]
    # In order to create percentage bar graphs, we need to group the data by
    # the match type and media type, then calculate the percentage of each count
    # within the total for the week.
    for (match_type, media_type), gdf in df.groupby(COLUMNS[:2]):
        # Calculate the percent of each provider's count within the total for the week
        gdf["percent_per_week"] = (
            gdf["count"] / gdf.groupby("start_of_week")["count"].transform("sum") * 100
        )
        # Most visualizations for percentage bar graphs require that the columns be
        # the providers, and the rows be the start of week. We can do this by pivoting
        # the data. This transforms the data from:
        # start_of_week, provider, percent_per_week
        # 2023-01-01, provider1, 50
        # 2023-01-01, provider2, 50
        # 2023-01-02, provider1, 25
        # 2023-01-02, provider2, 75
        # To:
        # start_of_week, provider1, provider2
        # 2023-01-01, 50, 50
        # 2023-01-02, 25, 75
        gdf = gdf.pivot(
            index="start_of_week", columns="provider", values="percent_per_week"
        )
        # Create the stacked bar graph
        ax = gdf.plot.bar(
            rot=0,
            stacked=True,
            figsize=(10, 6),
            title=f"{_format_name(match_type)} - {_format_name(media_type)}",
        )
        handles, labels = ax.get_legend_handles_labels()
        ax.set_xlabel("Start of week")
        high_columns = len(gdf.columns) > 10
        text_size = 8 if high_columns else 10
        # Add the percentage values to each bar
        # Based on https://stackoverflow.com/a/51497791/3277713
        for date_idx, row in enumerate(gdf.index):
            for row_idx, col in enumerate(gdf.columns):
                cumsum = gdf.loc[row].cumsum()
                value = gdf[col][date_idx]
                # If the value is too small, don't display it
                if value < 1:
                    continue
                # If there are a lot of columns, display the column name with the value
                percent = f"{np.round(value, 2)}%"
                if high_columns:
                    percent = f"{percent} ({col})"
                plt.text(
                    # The x position is the index of the current column
                    # e.g. 0, 1, 2, 3, etc.
                    date_idx,
                    # The y position is the cumulative sum of the components below
                    # plus half the current value
                    # e.g. for provider 2 in the previous example, 75 + (75/2)
                    # <current-cumsum> + <current-value> / 2
                    cumsum[row_idx] - value / 2,
                    # The text is the current value, formatted to 2 decimal places
                    percent,
                    va="center",
                    ha="center",
                    fontsize=text_size,
                )
        # Add a legend to the right of the graph, but reverse the order of the labels
        # so that it matches the order of the stacks
        plt.legend(
            reversed(handles),
            reversed(labels),
            loc="upper left",
            bbox_to_anchor=(1.0, 1.0),
            prop={"size": text_size},
        )
        # Make sure the graph is not cut off
        plt.tight_layout()
        # Save the graph to a file
        plt.savefig(output / f"{run_date}_{match_type}_{media_type}.png")
        # Save the data
        gdf.to_csv(output / f"{run_date}_{match_type}_{media_type}.csv")

    print("\n\n\n\n============= FINAL RESULTS ============= \n\n")
    pprint.pprint(tallies)

    print("\n\n\n==================== ERRORS ===============\n\n")
    pprint.pprint(errors)

    print(f"\n\n\nOutputting to CSV at {output.absolute()}")


if __name__ == "__main__":
    main()

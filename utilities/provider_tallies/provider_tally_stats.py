"""
Retrieves provider result tallies from Openverse API Redis.

This script assumes that the API Redis instance you care about is present
on localhost (usually via tunneling). It will run through the provider result count
entries in Redis and output them to CSV.
"""
import pprint
from pathlib import Path

import click
import pandas as pd
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


@click.command()
@click.option(
    "--output",
    help="Output file path",
    type=click.Path(path_type=Path),
    default="provider_tally_stats.csv",
)
@click.option(
    "--start-date",
    help="Start date for the tally, in the form of YYYY-MM-DD. "
    "Results in Redis are grouped by the start of the week.",
    type=str,
)
def main(output: Path, start_date: str | None):
    redis = Redis("localhost", decode_responses=True, db=TALLY_DATABASE)
    cursor = 0
    should_continue = True
    iter_count = 1

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

    df.to_csv(output, index=False)

    print("\n\n\n\n============= FINAL RESULTS ============= \n\n")
    pprint.pprint(tallies)

    print("\n\n\n==================== ERRORS ===============\n\n")
    pprint.pprint(errors)

    print(f"\n\n\nOutputting to CSV at {output.absolute()}")


if __name__ == "__main__":
    main()

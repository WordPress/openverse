# Provider Tally script

This script is used to extract the per-provider counts for both total results
and appearances within searches from the Openverse API redis.

The script assumes that the API Redis instance you care about is present on
localhost (usually via tunneling).

## Usage

1. `../../ov pdm install`
2. `../../ov pdm run provider_tally_stats.py`

By default, the script will output the results to `provider_tally_stats.csv` in
the current directory. Use the `--output` flag to specify a different output
file.

This script can also be used to extract information acquired _after_ a certain
date. Use the `--start-date` flag to specify a date in the format `YYYY-MM-DD`.

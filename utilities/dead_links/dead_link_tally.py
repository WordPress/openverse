"""
Retrieves dead link tallies from Openverse API Redis.

This script assumes that the API Redis instance you care about is present
on localhost (usually via tunneling). It will run through the link validation
entries in Redis.
"""

import pprint
from collections import defaultdict
from urllib.parse import urlparse

import click
from redis import Redis
from tqdm import tqdm


def handle_matches(redis, matches, tallies, errors):
    values = redis.mget(matches)
    for value, match in zip(values, matches):
        try:
            url = urlparse(match.split("valid:")[1])
            split = url.hostname.split(".")
            if len(split) > 2:
                # skip the first in an effort to remove subdomains 🤞
                hostname = ".".join(split[1:])
            else:
                hostname = url.hostname

            status = "alive" if value.startswith("2") else "dead"

            # don't use defaultdict to prevent pretty printing from looking horrible
            if status not in tallies[hostname]:
                tallies[hostname][status] = 0

            tallies[hostname][status] += 1
        except Exception as e:
            errors[value] = e


@click.command()
@click.option(
    "--host",
    help="Redis host to connect to",
    type=str,
    default="localhost",
)
@click.option(
    "--port",
    help="Port to connect to",
    type=int,
    default=None,
    show_default=True,
)
def main(host: str, port: int | None):
    port_str = f":{port}" if port is not None else ""
    click.echo(f"Connecting to Redis cluster at {host}{port_str}")

    redis_params = {"host": host, "decode_responses": True}
    if port is not None:
        redis_params["port"] = port

    redis = Redis(**redis_params)
    try:
        redis.ping()
    except Exception as e:
        click.echo(f"Error connecting to Redis: {e}")
        return

    tallies = defaultdict(dict)
    errors = dict()

    total_to_process = redis.eval("return #redis.pcall('keys', 'valid:*')", 0)

    with tqdm(total=total_to_process, miniters=10) as pbar:
        cursor, matches = redis.scan(cursor=0, match="valid:*", count=250)
        handle_matches(redis, matches, tallies, errors)
        pbar.update(len(matches))
        iter_count = 1

        while cursor != 0:
            cursor, matches = redis.scan(cursor=cursor, match="valid:*", count=250)
            handle_matches(redis, matches, tallies, errors)
            pbar.update(len(matches))
            iter_count += 1
            if iter_count % 10 == 0:
                # only print each 10 iterations to ease I/O time spent
                tqdm.write(
                    pprint.pformat(dict(cursor=cursor, **tallies), compact=True) + "\n"
                )
    print("\n\n\n\n============= FINAL RESULTS ============= \n\n")
    pprint.pprint(tallies)

    print("\n\n\n==================== ERRORS ===============\n\n")
    pprint.pprint(errors)


if __name__ == "__main__":
    main()

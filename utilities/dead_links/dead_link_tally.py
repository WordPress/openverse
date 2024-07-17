"""
Retrieves dead link tallies from Openverse API Redis.

This script assumes that the API Redis instance you care about is present
on localhost (usually via tunneling). It will run through the link validation
entries in Redis.
"""

import pprint
from collections import defaultdict
from urllib.parse import urlparse

from redis import Redis
from tqdm import tqdm


redis = Redis("localhost", port=6399, decode_responses=True)

cursor = 0

tallies = defaultdict(dict)
errors = dict()


def handle_matches(matches):
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


total_to_process = redis.eval("return #redis.pcall('keys', 'valid:*')", 0)

with tqdm(total=total_to_process, miniters=10) as pbar:
    cursor, matches = redis.scan(cursor=0, match="valid:*", count=250)
    handle_matches(matches)
    pbar.update(len(matches))
    iter_count = 1

    while cursor != 0:
        cursor, matches = redis.scan(cursor=cursor, match="valid:*", count=250)
        handle_matches(matches)
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

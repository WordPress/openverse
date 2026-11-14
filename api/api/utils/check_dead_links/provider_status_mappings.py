"""Per-provider HTTP status mappings for link availability."""

from collections import defaultdict
from dataclasses import dataclass


@dataclass
class StatusMapping:
    # Status codes that don't clearly indicate live/dead
    unknown: tuple[int] = (429, 403)

    # Status codes that indicate a working link
    live: tuple[int] = (200,)

    # Status codes that indicate a dead link (should be filtered out)
    dead: tuple[int] = (404, 410, 451, 500, 502, 503, 504)


provider_status_mappings = defaultdict(
    StatusMapping,
    thingiverse=StatusMapping(
        # https://github.com/WordPress/openverse/issues/900
        unknown=(429,),
    ),
    flickr=StatusMapping(
        # https://github.com/WordPress/openverse/issues/1200
        unknown=(429,),
    ),
    europeana=StatusMapping(
        # https://github.com/WordPress/openverse/issues/2417
        unknown=(429,),
    ),
)

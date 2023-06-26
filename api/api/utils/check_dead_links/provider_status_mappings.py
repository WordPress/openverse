"""Per-provider HTTP status mappings for link availability."""

from collections import defaultdict
from dataclasses import dataclass


@dataclass
class StatusMapping:
    unknown: tuple[int] = (429, 403)
    live: tuple[int] = (200,)


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

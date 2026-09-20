"""
Per-provider HTTP status mappings for link availability.

This module defines how different HTTP status codes are interpreted when
validating image links. Status codes are categorized as:

- live: Images that are accessible and should be included in results (default: 200)
- unknown: Ambiguous status codes that may be temporary issues like rate limiting 
  or blocking, where we should not filter the image but log a warning (default: 429, 403)
- dead: Any status code not in 'live' or 'unknown' is considered dead and will be
  filtered out from search results. This includes:
  * 404 (Not Found)
  * 410 (Gone) - specifically addresses GitHub issue #5466
  * 500 (Internal Server Error)
  * Any other HTTP error status

The dead link filtering helps ensure that WordPress block editor and other clients
don't receive broken image URLs that would fail to load.
"""

from collections import defaultdict
from dataclasses import dataclass


@dataclass
class StatusMapping:
    """
    Defines how HTTP status codes are categorized for link validation.
    
    Any status code not in 'live' or 'unknown' is considered 'dead' and will
    be filtered out from search results.
    """
    unknown: tuple[int] = (429, 403)  # Rate limiting, blocking - don't filter but warn
    live: tuple[int] = (200,)         # Accessible images - include in results


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

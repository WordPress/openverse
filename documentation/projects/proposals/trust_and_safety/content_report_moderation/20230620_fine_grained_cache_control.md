# 2023-06-20 Implementation Plan: Fine-grained API cache control

**Author**: @sarayourfriend

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [ ] @krysal - Redis experience
- [ ] TBD -

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- [Project Thread](https://github.com/WordPress/openverse/issues/383)
- [Project Proposal](/projects/proposals/trust_and_safety/content_report_moderation/20230411-project_proposal_content_report_moderation.md)

## Expected Outcomes

<!-- List any succinct expected products from this implementation plan. -->

- Tools accessible to the Django admin API exist that can manually invalidate
  cached responses related to a given search result
- An index of result to cache key exists for routes that need it so that cache
  keys related to a particular result are easily retrieved

## Overview

<!-- An overview of the implementation plan, if necessary. Save any specific steps for the section(s) below. -->

### Result/Cache-Key Index

In order to invalidate cached responses related to a particular result, we must
track cache keys for a given result. This index only needs to be maintained for
routes that need it, as covered in the
[appendix describing per-route cache requirements](/projects/proposals/trust_and_safety/content_report_moderation/appendixes/route_cache_requirements.md#django-managed-cache).
Please refer to that document for an explanation of why the endpoints discussed
in this section are the ones that require the managed cache.

When caching a response from one of the endpoints with Django-managed cache, we
will also update the result/cache-key index. For the search and related
endpoints, this will mean iterating through each result in the response body and
adding a new cache-key entry for that result:

```py
# See "Cleanup" section for explanation of `unix_time_expiry` and usage
cache_key, unix_time_expiry = calculate_cache_key(request)
result_cache_index_template = "rescachekeys:{identifier}"

pipe = redis.pipe()
for result in response.body["results"]:
    key = result_cache_index_template.format(identifier=result["id"].replace("-" ""))
    pipe.zadd(key, score=unix_time_expiry, member=cache_key)

pipe.execute()
```

The request should then be cached with the key returned by
`calculate_cache_key`.

#### Cleanup

Redis does not support any feature to automatically expire set members, so the
cache key in the result/cache-key index must be coupled with an expiry token (a
Unix timestamp indicating when the key expires) that can be used to determine
which keys should be cleaned. We will create a DAG to run daily that scans daily
(scheduled to coincide with low traffic periods) to remove expired cache keys
from the result/cache-key index. The DAG will `SCAN` through the `rescachekeys`
prefix and for each key, call `ZREMRANGEBYSCORE {key} {current unix time} 0`.
This will remove all sorted set elements with scores lower than the current Unix
time. Because member scores are set to the expiration time, this effectively
removes all entries that have expired.

### Managed Cache Middleware

### Evaluate cache necessity

How much is a cache necessary for our API to be performant. If we reduced search
cache TTL to 1 day, would our API fall over? What about 1 hour? What if we
removed it entirely?

### Route overview

Please refer to
[the route cache requirements appendix](/projects/proposals/trust_and_safety/content_report_moderation/appendixes/route_cache_requirements.md)
for a complete summary of how I've determined which routes require fine-grained
cache control and which can be managed via Cloudflare.

### Data Refresh

When a data refresh happens, cached results relevant to the data refresh must be
invalidated. We will add a new DAG triggered at the end of the filtered index
creation DAGs that invalidates cached search results for the media type, cached
embed responses (if image), and the cached `/stats/` endpoint for the media
type.

Embed and search results will be cached via the new Redis approach and will have
a stable key prefix that can be used to delete the cached responses from Redis:

````py
# CC BY-SA StackOverflow user Patrick Collins
# https://stackoverflow.com/a/34166690
import redis
from itertools import izip_longest

r = redis.StrictRedis(host='localhost', port=6379, db=0)

# iterate a list in batches of size n
def batcher(iterable, n):
    args = [iter(iterable)] * n
    return izip_longest(*args)

for keybatch in batcher(r.scan_iter(f"{image_search_cache_prefix}:*"), 500):
    r.delete(*keybatch)```
````

```{important}
We should benchmark this in production to see how long this operation takes and what the toll is on our production Redis. Redis's `DEL` command is O(n) where n is the number of keys being deleted, so it is potentially non-trivial to expire this many keys at once. If the performance impact of this makes it ultimately non-viable, then we can simply fall back to the 1 month TTL and accept that new and updated results will take 1 month to appear in our search results.
```

The stats' endpoint will be cached in Cloudflare and will require a call to the
Cloudflare cache API to invalidate it:

```js
// POST https://api.cloudflare.com/client/v4/zones/{zone-identifier}/purge_cache

{
  "files": [
    "https://api.openverse.engineering/v1/{media-type}/stats/",
    "https://api-production.openverse.engineering/v1/{media-type}/stats/",
  ]
}
```

### Cloudflare Cache Invalidation

If a work is deindexed from Openverse, we need to remove cached responses
related to it. These are:

- Thumbnail
- Waveform (if audio)
- The single result endpoint (`/v1/{media_type}/{identifier}/`)
- The related endpoint (`/v1/{media_type}/{identifier}/related/`)

The list is basically just a list of the routes that include the result
identifier in the path. Waveform is essentially unnecessary because it cannot
include any sensitive information. However, for the sake of consistent behaviour
from our API, we'll invalidate it anyway.

To invalidate pages from Cloudflare's cache, we'll do something along the
following lines from our Django app when needed:

```py
import CloudFlare

cf = CloudFlare.CloudFlare(token=settings.CF_TOKEN)

subdomains = ["api", "api-production"]
shared_file_templates = [
  "/v1/{media_type}/{identifier}/",
  "/v1/{media_type}/{identifier}/related/",
  "/v1/{media_type}/{identifier}/thumbnail/",
]
media_type_file_templates = {
  "image": [],
  "audio": [
    "/v1/{media_type}/{identifier}/waveform/",
  ],
}

file_templates = shared_file_templates + media_type_file_templates[media_type]

file_template = "https://{subdomain}.openverse.engineering{file}"
files = [
  file_template.format(
    subdomain=subdomain,
    file=_file.format(media_type=media_type, identifier=identifier),
  )
  for subdomain in subdomains
  for _file in file_templates
]

cf.zones.purge_cache.post(zone_id, data={"files": files})
```

### When Should Cache Invalidation Happen

Cache invalidation should happen automatically when any moderation decision is
made that modifies the index. There are two such actions in our application
today: marking the result as sensitive or deindexing the result entirely. This
will be implemented in the `AbstractMediaReport::save` method any time the
status is set to filtered or deindexed.

Additionally, for the sake of debugging and to anticipate needs we haven't yet
discovered, we will also expose a utility in Django admin to manually trigger
cache invalidation for a result. This will be implemented as a
[`ModelAdmin` action on the `ImageAdmin` and `AudioAdmin` classes](https://docs.djangoproject.com/en/4.2/ref/contrib/admin/actions/#actions-as-modeladmin-methods).
For ease of reuse and to ensure future media types automatically implement this
feature, we will add a `AbstractMediaModelAdmin` base class that implements the
action.

Both of these areas should share the implementation, which will live in a new
`api.utils.cache_management` module. The module should export a single function
with the following API:

```py
def invalidate_cache_for_result(media_type: MediaType, result: AbstractMedia) -> None:
    ...
```

The implementation should be based off of the sample code in the
[previous section](#cloudflare-cache-invalidation) and should handle calculating
the correct routes to invalidate for the result.

`AbstractMediaReport::save` and the new model admin action should both call to
the new `invalidate_cache_for_result` method.

```{note}
I feel it is simpler to have a separate module and function responsible for cache management
rather than adding this functionality to the `AbstractMedia` base class.
```

## Outlined Steps

<!-- Describe the implementation step necessary for completion. -->

1. Create the `invalidate_cache_for_result` function and call it from
   `AbstractMediaReport::save`
2. Add the Django model admin action to manually invalidate cache for a result

## Dependencies

### Infrastructure

<!-- Describe any infrastructure that will need to be provisioned or modified. In particular, identify associated potential cost changes. -->

### Tools & packages

<!-- Describe any tools or packages which this work might be dependent on. If multiple options are available, try to list as many as are reasonable with your own recommendation. -->

We will add the official Cloudflare API python client package to the API
dependencies: <https://github.com/cloudflare/python-cloudflare>

### Other projects or work

<!-- Note any projects this plan is dependent on. -->

## Alternatives

<!-- Describe any alternatives considered and why they were not chosen or recommended. -->

## Design

<!-- Note any design requirements for this plan. -->

## Parallelizable streams

<!-- What, if any, work within this plan can be parallelized? -->

## Blockers

<!-- What hard blockers exist which might prevent further work on this project? -->

## API version changes

<!-- Explore or mention any changes to the API versioning scheme. -->

## Accessibility

<!-- Are there specific accessibility concerns relevant to this plan? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

## Privacy

<!-- How does this approach protect users' privacy? -->

## Localization

<!-- Any translation or regional requirements? Any differing legal requirements based on user location? -->

## Risks

<!-- What risks are we taking with this solution? Are there risks that once taken can’t be undone?-->

## Prior art

<!-- Include links to documents and resources that you used when coming up with your solution. Credit people who have contributed to the solution that you wish to acknowledge. -->

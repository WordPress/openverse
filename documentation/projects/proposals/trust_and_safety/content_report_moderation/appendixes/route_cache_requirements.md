# Route Cache Requirements

This is a supporting document for the
[fine-grained API cache control implementation plan](/projects/proposals/trust_and_safety/content_report_moderation/20230620-fine-grained-cache-control.md).
It lists each Openverse API route pattern and usage and describes (1) its cache
requirements (TTL, etc) and (2) whether it is possible to manage the cache for
the route in Cloudflare or if it requires the Django managed cache. Please refer
to the implementation plan and the project plan (linked in the plan) for details
about why any of this is necessary in the first place.

## Routes

Here are all the possible methods and routes in our app:

- `GET /v1/audio/`
- `GET /v1/audio/{identifier}/`
- `GET /v1/audio/{identifier}/related/`
- `POST /v1/audio/{identifier}/report/`
- `GET /v1/audio/{identifier}/thumb/`
- `GET /v1/audio/{identifier}/waveform/`
- `GET /v1/audio/stats/`
- `POST /v1/auth_tokens/register/`
- `POST /v1/auth_tokens/token/`
- `GET /v1/images/`
- `GET /v1/images/{identifier}/`
- `GET /v1/images/{identifier}/related/`
- `POST /v1/images/{identifier}/report/`
- `GET /v1/images/{identifier}/thumb/`
- `GET /v1/images/{identifier}/watermark/`
- `GET /v1/images/oembed/`
- `GET /v1/images/stats/`
- `GET /v1/rate_limit/`

Routes shared by media type behave identically, authentication endpoints
(`auth_tokens/*` and `rate_limit`) should not be cached, and only routes that
retrieve data need caching. Therefore, we can condense the list of relevant
routes to:

- `GET /v1/{media_type}/`
- `GET /v1/{media_type}/{identifier}/`
- `GET /v1/{media_type}/{identifier}/related/`
- `GET /v1/{media_type}/{identifier}/thumb/`
- `GET /v1/audio/{identifier}/waveform/`
- `GET /v1/{media_type}/stats/`
- `GET /v1/images/oembed/`

```{information}
The audio media type has a unique waveform route not shared by the image media type.

Likewise, the image media type has a unique `oembed` route that is not shared by the
audio media type.
```

### Django managed cache

```{information}
Keep in mind the goal of fine-grained cache control: the ability to invalidate
cached responses related to a particular result. This not only includes results
identified specifically in the path, but most critically those returned in the
API response.
```

Of the routes that need caching listed above, only three routes share a path
between multiple results. Therefore, these routes are the ones that will need to
be tracked in the result/cache-key index and must therefore have their cache
managed in Django:

- `GET /v1/{media_type}/` (search)
  - All search results for a media type share the same path but have significant
    query parameters
- `GET /v1/images/oembed/`
  - All image embed responses share the same path. The `url` parameter
    determines the returned response, which can contain textual content that
    should be treated as sensitive.
- `GET /v1/{media_type}/{identifier}/related/`

The thumbnail endpoint, while it has significant query parameters, has a stable
path that can be used to expire cached responses for an individual result.
Therefore, it does _not_ need the result/cache-key index because if we need to
invalidate the cache for a result, we will want to invalidate all cached
thumbnails for the result at once.

All other routes should be cached using Cloudflare.

### General baseline cache requirements

Routes that return catalogue data must have a minimum TTL that matches the data
refresh latency for the media type, which is currently one
week[^data-refresh-latency]. Anything lower does not make sense because there
wouldn't be any relevant changes to the data[^dynamic-ttl]. However, for the
search, embed, and stats endpoints we can manually invalidate the cache after a
data refresh is completed (including filtered index creation) to prevent stale
results after a data refresh. While the data refresh latency is ideally 1 week,
sometimes we cannot run data refreshes at that regular cadence, so 1 month TTL
is suggested below, to be manually invalidated after data refresh.

Thumbnail and waveform data, should not change unless the underlying work
changes. At the moment we have no way to identify when a specific result has
changed, and because I suspect it is very rare for the related thumbnail or
waveform to change for a work, I've suggested a relatively long stable TTL for
those endpoints.

[^data-refresh-latency]:
    This intentionally ignores the current (mid-2023) difficulties with image
    data refresh which have prevented us from running the image data refresh for
    longer periods of time.

[^dynamic-ttl]:
    Hypothetically this implies that the ideal TTL for these routes should be
    configured to be calculated relative to the next relevant data refresh and
    not a constant value. That is, while data refresh latency is currently one
    week, results cached the day before the data refresh takes effect should
    have a TTL that expires after the data refresh is finished. Cloudflare
    doesn't let us dynamically calculate the TTL in this way, so we would only
    be able to take this approach for
    [search and embed](#fine-grained-cache-control). However, in practice this
    won't be necessary because we'll manually invalidate the cache for these
    results at the end of data refresh anyway, so a dynamic cache value just
    overcomplicates things.

The following routes should have 1 month TTL:

- `GET /v1/{media_type}/` (search)
- `GET /v1/{media_type}/{identifier}/`
- `GET /v1/{media_type}/{identifier}/related/`
- `GET /v1/{media_type}/stats/`
- `GET /v1/images/oembed/`

The following routes should have 1 year TTL:

- `GET /v1/{media_type}/{identifier}/thumb/`
- `GET /v1/audio/{identifier}/waveform/`

The following routes should have no caching whatsoever:

- `POST /v1/audio/{identifier}/report/`
- `POST /v1/auth_tokens/register/`
- `POST /v1/auth_tokens/token/`
- `GET /v1/rate_limit/`

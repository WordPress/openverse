# 2024-12-09 Implementation Plan: Proxy Frontend API Requests Through Nuxt

**Author**: @obulat

## Reviewers

- [ ] @dhruvkb
- [x] @krysal

## Project Links

- [Project Thread](https://github.com/WordPress/openverse/issues/3473)
- [Project Milestone](https://github.com/WordPress/openverse/milestone/35)

This project does not have a project proposal because the scope and rationale of
the project are clear, as defined in the project thread.

## Overview

Currently, client requests[^1] from the frontend to the API are sent without
authentication. As a result, strict API rate limiting on unauthenticated
requests would inadvertently throttle legitimate traffic from openverse.org
users. By proxying all client requests[^1] through the Nuxt server, we can
authenticate them and thus distinguish them from the anonymous traffic in the
API.

This implementation plan outlines how we will route all frontend traffic to the
API through Nuxt server routes, which authenticates these requests at the API
level, and limit these routes in the Nitro server to protect them from excessive
automated traffic that is against Openverse Terms of Service.

This plan does not lower the unauthenticated rate limits in the API. It lays the
groundwork, and the [follow-up work](#follow-up-work) describes what remains.
This keeps the API stable and fair for everyone, and frontend users shouldn't
notice a difference.

## Expected Outcomes

1. **Distinguishable frontend requests in the Django API**: For the Django API,
   the frontend requests are authenticated and no longer constrained by
   unauthenticated rate limits.

2. **The proxy is not a way around the API rate limits**: The Nitro server
   limits requests per visitor and per IP address, and the API limits the
   frontend's total usage. Legitimate users, including those on shared IP
   addresses at schools and libraries, keep reliable access.

## Request Flow

The `openverse.org` DNS record is not proxied by Cloudflare, so browsers connect
directly to the Nuxt server. The API hosts are proxied.

When a user loads a page, Nuxt renders it on the server (SSR) and sets a session
cookie if the user doesn't have one. During SSR, the stores call the `/api`
routes in-process, so these calls don't make a network request. After the first
load, the stores call the same routes from the browser, and the session cookie
is sent with them. In both cases, the Nitro route adds the frontend credentials
and sends the request to the Django API.

```{mermaid}
sequenceDiagram
    participant U as Browser
    participant N as Nuxt (Nitro)
    participant A as API
    U ->> N: Page load or /api request
    alt under the rate limits
        N ->> A: Request authenticated with frontend credentials
        A ->> N: Response
        N ->> U: Response
    else over a rate limit
        N ->> U: 429 with a message
    end
```

## Rate limiting

The proxy routes are public and use the frontend's credentials, so without
limits of their own, a script blocked by the anonymous API limits could use them
instead.

Cloudflare can't limit these routes while the `openverse.org` record isn't
proxied. We will limit them in Nitro first, and put Cloudflare in front of
`openverse.org` if usage stays too high. See
[the follow-up work](#follow-up-work).

### Counters

The session cookie lets Nitro separate the people who share an IP address, such
as in a library. Every request that counts also counts toward the per-IP
ceiling.

| Request                                      | Counted by | Limit                         |
| -------------------------------------------- | ---------- | ----------------------------- |
| `/api` request with a session                | Session    | Normal use by one person      |
| `/api` request without a session             | IP         | Low                           |
| Page load that calls the API, with a session | Session    | Normal use by one person      |
| All of the above                             | IP         | Very high, the per-IP ceiling |

- A page load without a session counts only toward the per-IP ceiling, because
  every new visitor arrives this way and many can share one IP address.
- SSR calls to the `/api` routes are not counted separately, because their page
  load is already counted. SSR search pages call the API, so if page loads
  weren't counted, a script could request `/search?q=cat` to avoid the limits.
- Browsers that block cookies share the low limit for their IP address, so some
  of these users can receive a 429.
- The counters are in memory and are per Nuxt task, so the limits are
  approximate. This is enough for generous limits.

### Backstop in the API

The frontend's API application gets a high but finite rate limit. If a script
gets past the Nitro limits, for example by using many IP addresses, this limit
protects the API. openverse.org search can degrade for everyone when it's
reached, so we need an alert before that point.

### Impact on the Nuxt Server

- **Load on Nuxt CPU/memory** Proxying the requests by the Nuxt server will
  increase the server load. We need to ensure that the server can handle that
  load by monitoring and adjusting the values if necessary. The server proxy
  routes should be written in such a way that they are not consuming CPU
  resources heavily.

## Step-by-step plan

1. [Add the frontend feature flag](#add-the-frontend-feature-flag)
2. [Give the frontend's API application its own rate limit](#give-the-frontends-api-application-its-own-rate-limit)
3. [Add a route from Nitro to the API that Cloudflare can't challenge](#add-a-route-from-nitro-to-the-api-that-cloudflare-cant-challenge)
4. [Add session to the init plugin](#add-session-to-the-init-plugin)
5. [Add the server plugin to create the Openverse API client and add it to the event context](#add-the-server-plugin-to-initialize-the-openverse-api-client-and-add-it-to-the-event-context)
6. [Set up Nuxt server proxy routes](#set-up-nuxt-server-proxy-routes)
7. [Add the rate limiting to Nitro in log-only mode](#add-the-rate-limiting-to-nitro-in-log-only-mode)
8. [Use Nuxt server routes instead of the `api-client` in the frontend when the feature flag is on](#use-server-routes-in-the-frontend-when-the-feature-flag-is-on)
9. [Switch on the flag in production](#switch-the-feature-flag-on-in-production)
10. [Monitor usage and enforce the limits](#monitor-usage-and-enforce-the-limits)
11. [Remove the feature flag and the direct API client](#remove-the-feature-flag-and-the-direct-api-client)

## Step Details

### Add the frontend feature flag

Add `proxy_requests` feature flag to `frontend/feat/feature-flags.json`:

```json
{
  "proxy_requests": {
    "description": "Proxy frontend requests through Nuxt server",
    "status": {
      "staging": "switchable",
      "production": "disabled"
    },
    "defaultState": "off",
    "storage": "cookie"
  }
}
```

### Give the frontend's API application its own rate limit

All openverse.org traffic will use one API `client_id`, so it will share one set
of API rate limits. The existing models don't fit: `standard` allows 100
requests per minute, `enhanced` allows 200, and `exempt` has no limit and so no
backstop.

- Add a new `rate_limit_model` to `ThrottledApplication`, with burst and
  sustained throttles sized from the frontend's current API request rate.
- In the Django admin (_maintainers only_), confirm that the frontend's
  application is `verified`, uses the new model, and has no `privileges`,
  because the proxy doesn't need the larger page size and result depth that they
  unlock.
- Add an alert for when usage gets close to the limit.

### Add a route from Nitro to the API that Cloudflare can't challenge

The API hosts are proxied by Cloudflare, and the frontend reads the API address
from `public.apiUrl`, so it may call the API through Cloudflare from a small set
of IP addresses. The rate limiting rules on the API hosts could then count all
users' requests against those addresses. The rules for repeated 400, 401, and
403 responses and for `/v1/auth_tokens/token/` are the most likely to fire.
Nitro can't solve a managed challenge, so this would break search for all users.

- Confirm the production value of `NUXT_PUBLIC_API_URL`.
- Add a private `apiUrl` to `runtimeConfig` for Nitro, pointing at an internal
  API address. If there's no internal route, exclude Nuxt's outbound IP
  addresses from these rules using `ip.src`. This requires stable outbound
  addresses.

### Add session to the `init` plugin

When the user sends the first request to any Openverse frontend URL, the Nuxt
server initializes their session, which makes their later requests identifiable
as one user's requests, even on a shared IP address. Add this to the
`frontend/src/plugins/02.init.server.ts` plugin, the entry point for SSR
requests.

Add a session using the `unjs/h3`
[`useSession`](https://h3.unjs.io/examples/handle-session) hook. The session
should:

- use the `HMAC_SIGNING_SECRET` env variable to sign the session, so that a
  script can't make up session values.
- be named `ovSession`, and the session cookie should be `HttpOnly`, `Secure`,
  and `SameSite=Lax`, and have a short maximum age. With `SameSite=Strict`,
  users arriving from an external link wouldn't send the cookie and would get a
  new session.

### Add the server plugin to initialize the Openverse API client and add it to the event context

Create a nitro plugin using
[`defineNitroPlugin`](https://nuxt.com/docs/guide/directory-structure/server#server-plugins)
in `server/plugins/proxy.ts`. This plugin should:

- initialize the
  [`OpenverseApiClient`](https://github.com/WordPress/openverse/tree/347878acf7620548a0628d6833885a479c30b9c1/packages/js/api-client).
  If the API secrets are set, use authenticated client. Otherwise, in
  development environment, use unauthenticated client, and in
  staging/production, throw an error, as the API requests from the frontend
  should always be authenticated. To access the secrets, the plugin should use
  the `process.env.[VARIABLE_NAME]`, not `runtimeConfig.VARIABLE_NAME` since the
  `runtimeConfig` is not available in the plugin body.
- add a middleware using `defineEventHandler` that adds the `OpenverseApiClient`
  to the event context as `event.context.apiClient`.

### Set up Nuxt Server proxy routes

These routes are public and use the frontend's credentials, so they must not
give visitors more access than a direct anonymous API request. Authenticated
requests can use a `page_size` of up to 50, while anonymous requests can use up
to 20. Passing parameters straight through would give every visitor the higher
limit.

- Create the Nuxt server routes under `/api/`:

  - `/api/search/[type]` - for search requests
  - `/api/[type]/[id]` - for single result requests
  - `/api/[type]/related/[id]` - for related media requests

- Create a `proxyApiRequest` function that accepts the H3 `event` object and
  forwards the request to the API.
  - `validateRequest` function should:
    - ensure that the media type is one of the supported media types, and that
      the media id is a valid UUID, so that the routes can't reach any other API
      endpoints.
    - keep only the query parameters that the frontend sends, using an
      allowlist, and drop all others.
    - reject a `page_size` above the anonymous maximum, or drop the parameter if
      the frontend doesn't need it.
  - `generateApiUrl` function should generate the API request URL based on the
    request details (for example, `/api/search/image/?q=cat` should be converted
    to `<apiUrl>/v1/images/?q=cat`).
  - send the request to the API using the Openverse API client from
    `event.context.apiClient`. Do not forward the browser's cookies to the API.
  - handle errors, extract data necessary for the search time Plausible event,
    and return the appropriate response to the client.

### Use server routes in the frontend when the feature flag is on

Create two fetch functions in the stores: one that uses the current direct API
requests with `api-service`, and the other that sends the request to the Nuxt
server route. The fetch function to use should be selected based on the feature
flag status.

Use `useRequestFetch` for the server route requests. During SSR it calls the
Nitro route in-process, and in the browser it behaves like `$fetch`, so SSR and
client requests share one code path.

The change will need to be added to the `related`, `single-media` and `media`
stores. Here's sample implementation in the media store,
`frontend/src/stores/media/index.ts`:

```ts
if (featureFlagStore.isOn("proxy_requests")) {
  const requestFetch = useRequestFetch()
  const result = await getProxiedResponse(requestFetch, mediaType, queryParams)
} else {
  const client = useApiClient()
  const result = await getApiClientResponse(client, mediaType, queryParams)
  if (result.error) {
    // handle the error
    return null
  }
  // handle the response
}

const getProxiedResponse = async (
  requestFetch: typeof $fetch,
  mediaType: string,
  queryParams: Record<string, string>
) => {
  try {
    const { eventPayload, data } = await requestFetch(
      `/api/search/${mediaType}/?${queryParams}`
    )
    return { eventPayload, data }
  } catch (error) {
    if (isRateLimited(error)) {
      // show the rate limit message, using the Retry-After header
    }
    // return the $fetch error
  }
}

const getApiClientResponse = async (
  client: ApiClient,
  mediaType: string,
  queryParams: Record<string, string>
) => {
  try {
    const { eventPayload, data } = await client.search(mediaType, queryParams)
    return { eventPayload, data }
  } catch (error) {
    // return the error
  }
}
```

The new functions should not call any composables that require the Nuxt context
(e.g., `useNuxtApp`) because `[nuxt]` is not available in nested functions. This
is why `useRequestFetch` is called before them.

`isRateLimited` checks for a 429 response. The frontend shows a message that
explains the limit and when to try again, instead of the regular error page.

### Add the rate limiting to Nitro in log-only mode

Add the [counters](#counters) to the `/api` routes and to the pages that call
the API, using a server middleware. Use a `runtimeConfig` setting to switch
between logging and enforcing, and start with logging.

- Read the client IP from the `X-Forwarded-For` entry added by our load
  balancer. Earlier entries come from the client and can be faked.
- Identify in-process SSR calls in a way that a client can't fake.
- Do not log session values or IP addresses. Log which counter a request hit and
  whether it would have been limited.
- When enforcing, return a 429 with a `Retry-After` header. The frontend must
  show a clear message for this response, including on SSR pages.

### Switch the feature flag on in production

Set the `proxy_requests` feature flag to `enabled` in the production
environment. This will start routing all frontend requests through the Nuxt
server.

### Monitor usage and enforce the limits

Keep the limits in log-only mode long enough to see normal traffic from shared
IP addresses, ideally including school hours. Then set the numbers and switch to
enforcing. The following data need to be monitored:

- The number of requests that would be limited, by counter. Look for IP
  addresses with many sessions, which are likely to be institutions.
- The 429 rate after enforcing, and user reports of being blocked.
- The frontend application's usage against its API limit.
- Nuxt CPU and memory usage. In case the server is under heavy load, we might
  need to adjust the rate limits and/or frontend task values.
- API logs for unauthenticated search, single result, and related media requests
  from openverse.org. These must drop to about zero before the
  [anonymous limits are tightened](#follow-up-work).

### Remove the feature flag and the direct API client

Once the flag has been stable in production, remove the `proxy_requests` flag,
the direct fetch functions in the stores, `frontend/src/data/api-service.ts`,
and the `01.api-token.server.ts` plugin. The API credentials then exist only in
the Nitro server.

## Follow-up work

This project does not change the anonymous limits. These changes come after the
flag is on:

- **Search, single result, and related media:** Lower `THROTTLE_ANON_BURST` and
  `THROTTLE_ANON_SUSTAINED`, after confirming the current production values.
  Audio waveforms are covered because they come from the `peaks` parameter on
  these requests.
- **Thumbnails:** Browsers load thumbnails directly from the API, so they remain
  anonymous and are counted by IP. Cloudflare serves them, but a request that
  misses its cache still reaches Django. The default `THROTTLE_ANON_THUMBS` is
  150 requests per minute, and 30 students each loading a page of 20 results
  make about 600 requests. Check the cache hit rate and the thumbnail 429 rate,
  and keep this limit generous.
- **Openverse referrer throttles:** The `ov_referrer` throttles trust a
  `referrer: openverse.org` request header, which the frontend doesn't send. If
  something upstream adds this header, anyone can spoof it to avoid the
  anonymous limits. Remove these throttles when tightening the limits.
- **Cloudflare in front of `openverse.org`:** If usage stays too high, proxy
  this record and add rate limiting rules that count by IP with NAT support,
  with a per-IP ceiling. Requests are then rejected before they reach Nuxt, and
  a blocked user can solve a managed challenge. This requires restricting the
  origin to Cloudflare's IP ranges, reading the client IP from Cloudflare, and
  handling challenges on `fetch` requests. The zone has 2 free rate limiting
  rules, on the Business plan.

## Rejected Alternatives

- **Proxying thumbnail requests** The thumbnail requests from the frontend will
  remain anonymous on the API level. Cloudflare serves them, and proxying them
  would add load to the Nuxt server.

- **Tightening the anonymous limits without a proxy** This is the smallest
  change, but it throttles the shared IP addresses that this project is meant to
  protect.

- **Limiting only by IP in Nitro** This would recreate the shared IP problem at
  the proxy. Sessions let a library's users have separate counters.

- **Cloudflare in front of `openverse.org` as the first step** This would reject
  abusive requests earlier and give blocked users a challenge they can solve,
  but it moves all production traffic. We will do it if the Nitro limits aren't
  enough. See the [follow-up work](#follow-up-work).

## Dependencies

- **Feature Flags**:

  - `proxy_requests`

- **Infrastructure**: An internal route from the frontend to the API, a new API
  rate limit model, the `HMAC_SIGNING_SECRET` secret, and monitoring (Sentry).

- **Tools & Packages**:
  - `ofetch`: This would be a great occasion to move away from `axios`. `ofetch`
    is used internally by Nuxt, so it's a good choice for the server proxying.
    The store requests can be made with Nuxt helper wrapper over `ofetch`,
    `$fetch`[^2].
  - `h3` for server route handling and session management.

## Accessibility and Privacy

- **Accessibility**: The 429 message must be translated and available to screen
  readers.

- **Privacy**: The session cookie is anonymous and short-lived, and no personal
  data is stored. The in-memory counters use IP addresses only for as long as a
  counting window lasts.

## Rollback Strategy

- Set the `proxy_requests` feature flag to `off`. The frontend then calls the
  API directly again.
- To keep the proxy on but stop blocking users, switch the Nitro limits back to
  log-only mode.

[^1]:
    `Client requests` - Requests made by the frontend client to the API after
    the first page load. These requests are sent whenever a user submits a
    search, selects a filter or a search result. These requests are currently
    send directly to Openverse API without any authentication, because using the
    API credentials in the client code would expose them to the public.

[^2]: [Nuxt $fetch](https://nuxt.com/docs/api/utils/dollarfetch)

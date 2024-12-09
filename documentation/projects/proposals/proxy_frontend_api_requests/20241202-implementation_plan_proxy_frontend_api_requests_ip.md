# 2024-12-09 Implementation Plan: Proxy Frontend API Requests Through Nuxt

**Author**: @obulat

## Reviewers

- [ ] @dhruvkb
- [ ] @krysal

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
API through Nuxt server routes — effectively “authenticating” these requests at
the API level — and configure Cloudflare rate-limiting to protect these routes
from excessive automated traffic that is against Openverse Terms of Service.

While this plan does not include lowering unauthenticated rate limits in the
API, it establishes the groundwork for it. This approach will ensure better
stability and fairness of the API service, while also preserving the normal user
experience on the frontend.

## Expected Outcomes

1. **Distinguishable Frontend Requests in the API**: Frontend requests are
   authenticated at the API level and no longer constrained by unauthenticated
   rate limits.

2. **Protected Nuxt Server Routes and Fair Access**: Nuxt server routes are
   protected from automated abuse and suspicious traffic by Cloudflare
   rate-limiting, ensuring that legitimate users (including those in shared IP
   environments, such as schools and libraries) maintain reliable access without
   undue friction.

## Request Flow

From the Nuxt client perspective, the request flow will not change much: instead
of going directly to the API, requests will go to the Nuxt server routes
(`/api/**`). The main difference is that, when rate-limited, the client will
receive a Cloudflare challenge response that will be handled by
[Nuxt Turnstile Module](https://github.com/nuxt-modules/turnstile).

The Nuxt server routes will authenticate the requests by adding the API token,
and sign requests with HMAC to allow Cloudflare to apply rate-limiting on a
per-user basis, even when multiple users share the same IP (e.g., in NAT
environments).

```{mermaid}
sequenceDiagram
    participant O as Client
    participant C as Cloudflare
    participant NS as Nuxt Server
    participant A as API
    O ->> C: HMAC-signed request
    Note right of C: "Check the the rate limits based on cookie&IP"
    alt successful
        C ->> NS: request
        NS ->> A: authenticated request
        A ->> NS: response
        NS ->> O: response
    else rate-limited
        C ->> O: turnstile widget
        O ->> C: Cloudflare challenge cookie
        C ->> NS: request
        NS ->> A: authenticated request
        A ->> NS: response
        NS ->> O: response
    end
```

## Cloudflare Rate Limiting

Originally, I thought of using Cloudflare managed challenges to protect the Nuxt
server routes from abuse. However, this would have required issuing a challenge
to every new user, which would have been a poor user experience. Instead, we
will use Cloudflare rate limiting to protect the Nuxt server routes from abuse.
The rate limiting will be based on the IP and cookie combination, and will
trigger a managed challenge only when the request volume from a user exceeds the
defined threshold. This way, legitimate users will not be inconvenienced by
challenges, while automated traffic will be rate-limited and challenged.

- **Supported Browsers for Challenges**:
  [Cloudflare Documentation](https://developers.cloudflare.com/waf/reference/cloudflare-challenges/#supported-browsers)
  notes that managed challenges support modern browsers, but does not show the
  minimum supported versions. Users with older browsers may struggle,
  potentially creating accessibility issues.

- **Referer Header Changes After Challenge**: After passing a managed challenge,
  the referer header may change:
  [Referer Header after Challenge](https://developers.cloudflare.com/waf/reference/cloudflare-challenges/#referer-header)
  We must ensure this does not disrupt our request logic.

- **Multi-language Support**: Challenges support multiple languages [^2],
  although the number of supported languages is lower than the number of
  languages supported by Openverse.

### Impact on the Nuxt Server

- **Load on Nuxt CPU/memory** Proxying the requests by the Nuxt server will
  increase the server load. We need to ensure that the server can handle that
  load by monitoring and adjusting the values if necessary. The server proxy
  routes should be written in such a way that they are not consuming CPU
  resources heavily.

## Prior Art

- HMAC signing:
  [Sign k6 requests with HMAC to enable WAF bypass](https://github.com/WordPress/openverse/pull/4908)

## Step-by-step plan

We’ll implement this plan in the following order. I’ve noted which steps depend
on others, and included references to the detailed instructions below:

1. [Move API Token to Nuxt server middleware](#move-api-token-to-nuxt-server-middleware)
2. [Set up Nuxt Server proxy routes](#set-up-nuxt-server-proxy-routes)
3. [Add the frontend feature flag](#add-the-frontend-feature-flag)
4. [Set up Cloudflare rate limiting for staging](#set-up-cloudflare-rate-limiting-for-staging)
5. [Use server routes instead of the `api-client` in the frontend when the feature flag is on](#use-server-routes-in-the-frontend-when-the-feature-flag-is-on)
6. [Set up the Nuxt turnstile module](#set-up-the-nuxt-turnstile-module)
7. [Set up Cloudflare rate limiting for production](#set-up-cloudflare-rate-limiting-for-production)
8. [Switch on the flag in production](#switch-the-feature-flag-on-in-production)
9. [Monitor the Cloudflare dashboard and Sentry logs for challenge occurrences](#monitor-the-cloudflare-dashboard-and-sentry-logs-for-challenge-occurrences)

## Step Details

### Move API Token to Nuxt server middleware

Extract the functionality that generates the API token from
[`frontend/src/plugins/01.api-token.server.ts`](https://github.com/WordPress/openverse/blob/a9441f7e38fcf0d56f9732122c9d3106a87eabe5/frontend/src/plugins/01.api-token.server.ts)
to `frontend/server/utils/api-token.ts`.

Create the
[Nuxt server middleware](https://nuxt.com/docs/guide/directory-structure/server#server-middleware)
that requests the API token for every request, and adds the token to the event
context. In the new Nuxt server routes, we will be able to use it as
`event.context.apiToken`.

To use the token in the current frontend code, update the
[`use-api-client` composable](https://github.com/WordPress/openverse/blob/a9441f7e38fcf0d56f9732122c9d3106a87eabe5/frontend/src/composables/use-api-client.ts#L7)
to use the token from the event context:

```ts
/** Old code */
// const { $openverseApiToken: accessToken } = useNuxtApp()
/** New code */
const { apiToken } = useRequestEvent().context
```

### Set up Nuxt Server proxy routes

- Create the Nuxt server routes under `/api/`:

  - `/api/search/[type]` - for search requests
  - `/api/[type]/[id]` - for single result requests
  - `/api/[type]/related/[id]` - for related media requests

- Create a helper function that accepts the H3 `event` object, and extracts the
  request details to forward to the API:
  - media type
  - the API media type slug (i.e., the special case of "images" for "image")
  - media id, if applicable
  - search query
  - headers that should be passed on to the API
- From the
  [k6 implementation](https://github.com/WordPress/openverse/pull/4908), copy
  the helper function that signs the request with HMAC.

The server route handler should:

- generate the relevant API request URL (i.e., converting `/api/image/?q=cat` to
  `<apiUrl>/v1/images/?q=cat`)
- add the headers (headers from the original client request that can be proxied,
  authentication, HMAC)
- send the request using `ofetch` (or `ofetch.raw` to extract the response
  headers for `SEARCH_RESPONSE_TIME` Plausible event)
- handle errors and return the appropriate response to the client

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

### Set up Cloudflare rate limiting for staging

Add the initial rate limiting to the Nuxt server routes (`/api/**`) in the
infrastructure repository (_maintainers only_).

Cloudflare rules consist of two parts: the expression to match the request and
the action to take when the request matches the expression [^3].

#### Expression

The rate limiting expression should be opposite to the one we use in k6 tests:
we want to limit the requests that are not authenticated with HMAC.

```
http.host eq "staging.openverse.org"
and starts_with(http.request.uri.path, "/api/")
and not is_timed_hmac_valid_v0(...)
```

#### Action

The action should be `managed_challenge`, which will issue a challenge to the
user when the rate limit is exceeded.

#### Testing the rate limits

When testing this feature, we can adjust the staging limits using the UI. I
envisage that we will need to adjust the limits many times because testing the
Cloudflare rate limiting locally is not possible.

### Use server routes in the frontend when the feature flag is on

Create two fetch functions in the stores: one that uses the current direct API
requests with `api-service`, and the other that sends the request to the Nuxt
server route. The fetch function to use should be selected based on the feature
flag status.

The change will need to be added to the `related`, `single-media` and `media`
stores. Here's sample implementation in the media store,
`frontend/stores/media/index.ts`:

```ts
if (featureFlagStore.isOn("proxy_requests")) {
  const result = getProxiedResponse(mediaType, queryParams)
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
  mediaType: string,
  queryParams: Record<string, string>
) => {
  try {
    const { eventPayload, data } = await $fetch(
      `/api/search/${mediaType}/?${queryParams}`
    )
    return { eventPayload, data }
  } catch (error) {
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

### Set up the Nuxt turnstile module

When the Cloudflare rate limiting triggers a managed challenge, the client will
receive an HTML Cloudflare challenge response. To handle this response, we can
use the [Nuxt turnstile module](https://nuxt.com/modules/turnstile).

This is the part of the plan I'm most unsure about. I couldn't understand the
details of how this module works, so we would probably need to do a lot of
testing to make sure it works as expected. Unfortunately, we cannot test
Cloudflare challenge responses locally because the proxy is only set up in
staging/production. We will have to use staging for this, and to make the
testing easier, we can set the staging rate limits to be very low.

We should capture any problems with the turnstile module in Sentry to make sure
that no users are affected negatively by the rate-limiting. Sentry will also
give us an idea on how the older browsers are handling the challenges.

### Set up Cloudflare rate limiting for production

The rate limiting rule should be similar to that of the staging environment.

The rates should be generous enough to accommodate normal user behavior. Later,
they can be made stricter to deter automated abuse.

[More information on how request counts are calculated](https://developers.cloudflare.com/waf/rate-limiting-rules/request-rate/)

### Switch the feature flag on in production

Set the `proxy_requests` feature flag to `enabled` in the production
environment. This will start routing all frontend requests through the Nuxt
server.

### Monitor the Cloudflare dashboard and Sentry logs for challenge occurrences

The following data need to be monitored:

- Cloudflare dashboard (Security > WAF > Rate limiting rules) shows the number
  of issued challenges, and the
  [Challenge solve rate (CSR)](https://developers.cloudflare.com/bots/concepts/challenge-solve-rate/)
  for the rule. The CSR should be very high since we expect that most of the
  frontend usage is not automated.
- Nuxt CPU and memory usage. In case the server is under heavy load, we might
  need to adjust the rate limits and/or frontend task values.

## Rejected Alternatives

- **Always Issuing a Challenge Without Thresholds**: Issuing a managed challenge
  to every new user, regardless of load or conditions, would inconvenience users
  behind NATs and degrade the initial user experience. While simpler to
  implement (we would not need to calculate the exact rate limit), it fails our
  design goal of minimizing friction for normal users.

- **Proxying thumbnail requests** The thumbnail requests from the frontend will
  remain anonymous on the API level. Since controlling search and related
  requests naturally throttles excessive thumbnail retrieval, we consider it
  unnecessary to further load the Nuxt server.

## Dependencies

- **Feature Flags**:

  - `proxy_requests`

- **Infrastructure**: Cloudflare WAF rules, monitoring (Sentry, Cloudflare
  dashboard).

- **Tools & Packages**:
  - `ofetch` This would be a great occasion to move away from `axios`. `ofetch`
    is used internally by Nuxt, so it's a good choice for the server proxying.
    The store requests can be made with Nuxt helper wrapper over `ofetch`,
    `$fetch`.
  - `h3` for server route handling
  - [Nuxt turnstile module](https://nuxt.com/modules/turnstile) - the module for
    handling challenges returned by the Cloudflare rate limiting from the Nuxt
    server requests

## Accessibility and Privacy

- **Accessibility**:

  - Cloudflare challenges are generally accessible, but older browsers may fail.
  - Multilingual support helps non-English speakers.

- **Privacy**:
  - No personal data is stored, cookies are short-lived and anonymous.

## Rollback Strategy

- Set the `proxy_requests` feature flag to `off`. This will automatically
  deactivate the rate limiting rules, since the requests won't be going through
  the Nuxt server anymore.

[^1]:
    `Client requests` - Requests made by the frontend client to the API after
    the first page load. These requests are sent whenever a user submits a
    search, selects a filter or a search result. These requests are currently
    send directly to Openverse API without any authentication, because using the
    API credentials in the client code would expose them to the public.

[^2]:
    [Cloudflare multi-language support](https://developers.cloudflare.com/waf/reference/cloudflare-challenges/#multi-language-support)

[^3]:
    [Cloudflare rate limiting rules](https://developers.cloudflare.com/waf/rate-limiting-rules/)

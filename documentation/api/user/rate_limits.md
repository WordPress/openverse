# Rate limits

Please note that the API has imposed rate limits to prevent abuse. In the
response for each request that is subject to rate-limits, you can see the
`X-RateLimit-` headers for information about your permitted and available usage.
Exceeding the limit will result in '429: Too Many Requests' responses.

## Anonymous usage

Anonymous usage is subject to a rate limit of 100 requests per day and,
simultaneously, 5 requests per hour. This is fine for introducing yourself to
the API, but we strongly recommend that you obtain an API key as soon as
possible.

## Authenticated usage

Authorized clients have a higher rate limit of 10000 requests per day and 100
requests per minute. Additionally, Openverse can give your key an even higher
limit that fits your application's needs. See the docs on
[authentication](./authentication.md) for instructions on obtaining an API key.

### Key info

**Endpoint:**
<a href="../../api_docs/#tag/auth/operation/key_info"><code class="literal">/v1/rate_limit/</code></a>
(includes request and response samples)

As an authenticated user, you can use this endpoint to know your current
consumption and available limits.

# `@openverse/api-client`

Thoroughly typed JavaScript client for the Openverse API.

[![Repository](https://img.shields.io/badge/GitHub-@openverse%2Fapi--client-purple?logo=github)](https://github.com/WordPress/openverse/tree/HEAD/packages/js/api-client)
[![NPM Version](https://img.shields.io/npm/v/%40openverse%2Fapi-client)](https://www.npmjs.com/package/@openverse/api-client)

---

## Installation

```shell
npm install @openverse/api-client
```

By default, global fetch is used to make request. As such, there is no explicit
HTTP client library dependency.

## Usage

Create an Openverse API client using the `createClient` function exported by the
package.

```ts
import { createClient } from "@openverse/api-client"

const openverse = createClient()
```

`createClient` accepts the following options:

- `baseUrl`: The base URL for the Openverse API instance you wish to use. This
  defaults to the public Openverse API.
- `credentials`: An object definition optional credentials with which to
  authenticate the client's requests. See the
  ["Authentication" section](#authentication) for details of how this works when
  supplied. If credentials are not passed to `createClient`, requests will
  proceed anonymously.
- `fetch`: The `fetch` instance to use for the client. Defaults to
  `globalThis.fetch`.
- `headers`: Headers to send with every request.

For a description of how to use the request functions of the client, refer to
[the documentation for the library used to generate this client, `openapi-fetch`](https://openapi-ts.dev/openapi-fetch/api#fetch-options).

```ts
const images = await openverse.GET("/v1/images/", {
  params: {
    query: {
      q: "dogs",
      license: "by-nc-sa",
      source: ["flickr", "wikimedia"],
    },
  },
})

if (images.error) {
  throw images.error
}

images.data.results.forEach((image) => console.log(image.title))
```

### Rate limiting

The requester function does _not_ automatically handle rate limit back-off. To
implement this yourself, check the rate limit headers from the response
`response.headers`.

### Authentication

By default, the `createClient` function will return an unauthenticated client.

To use an authenticated client, pass a `credentials` object containing
`clientId` and `clientSecret` to the `createClient` function. The client will
automatically request tokens as needed, including upon expiration.

```ts
import { createClient } from "@openverse/api-client"

const authenticatedOpenverse = createClient({
  credentials: {
    clientId: "...",
    clientSecret: "...",
  },
})
```

The client automatically requests API tokens when authenticated, including
eagerly refreshing tokens to avoid halting ongoing requests. This is safe, as
the Openverse API does not immediately expire existing tokens when a new one
issued. This also means you do not need to share the same token between multiple
client instances (e.g., across multiple instances of the same application, as in
an application server cluster).

## Development and implementation details

The types used in this package for the Openverse REST API's route definitions
(including request parameter and response types) are generated based on the
Openverse REST API's OpenAPI Schema. Generation is managed with a thin wrapper
around [`openapi-typescript`](https://openapi-ts.dev/node).

Refer to <https://openapi-ts.dev/> for more details about the project and how it
works.

## Versioning

This package follows semantic versioning. Version numbers correspond to the API
of the package code, not the Openverse REST API.

## License

`@openverse/api-client` is distributed under the terms of the
[MIT license](https://spdx.org/licenses/MIT.html).

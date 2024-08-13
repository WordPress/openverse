# `openverse-api-client`

A thoroughly typed Python client for the Openverse API.

[![Repository](https://img.shields.io/badge/GitHub-openverse--api--client-purple?logo=github)](https://github.com/WordPress/openverse/tree/HEAD/packages/python/api-client)
[![PyPI - Version](https://img.shields.io/pypi/v/openverse-api-client.svg)](https://pypi.org/project/openverse-api-client)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/openverse-api-client.svg)](https://pypi.org/project/openverse-api-client)

## Installation

```shell
pip install openverse-api-client
```

## Usage

The Openverse API client has a single external dependency on `httpx`.
[HTTPx](https://www.python-httpx.org/) was chosen because the presence of both a
synchronous and asynchronous HTTP client from a single library, with nearly
identical APIs, made it easy to generate the Python client using the generator.

```python
from openverse_api_client import OpenverseClient, AsyncOpenverseClient

with OpenverseClient() as openverse:
    images = openverse.GET_v1_images(
        q="dogs",
        license="by-nc-sa",
        source=["flickr", "wikimedia"],
    )

with AsyncOpenverseClient() as async_openverse:
    audio = await async_openverse.GET_v1_audio(
        q="birds",
        license="by",
        source=["freesound"],
    )
```

Using the Openverse client as context managers will automatically close the
underlying HTTPx client. Call `close` on the Openverse client to manually close
the underlying HTTPx client when not using the context manager.

### Shared HTTPx client session

If you already use HTTPx and utilised a shared client session, you may pass this
to the Openverse client constructors.

```python
from openverse_api_client import OpenverseClient
import httpx

httpx_client = httpx.Client()

openverse = OpenverseClient(
    httpx_client=httpx_client,
)
```

The same API applies for the asynchronous Openverse client, but requires
`httpx.AsyncClient` instead.

When using a shared HTTPx client session **do not call close on the Openverse
client** as this will close the shared HTTPx instance. Likewise, **do not use
the Openverse client context manager if passing in a shared client**, the
context manager will close your shared HTTPx client on context exit.

### Authentication

By default, the clients will make unauthenticated requests. Pass `client_id` and
`client_secret` to the client constructor to authenticate requests. The client
automatically handles requesting tokens and token expiration.

```python
from openverse_api_client import OpenverseClient

# The same API applies to the async client
authenticated_openverse = OpenverseClient(
    client_id="...",
    client_secret="...",
)
```

### Alternative Openverse API instances

The clients reference the official production Openverse API instance by default,
https://api.openverse.org. If you would like to send requests to a different API
instance, pass `base_url` to the constructor:

```python
from openverse_api_client import OpenverseClient

# The same API applies to the async client
localhost_openverse = OpenverseClient(
    base_url="localhost:50280",
)
```

## Versioning

This package and the `@openverse/api-client` package follow
[semantic versioning](https://semver.org/). For both packages, the version of
the package reflects changes to the client APIs rather than tracking any
particular changes in the Openverse REST API. Any change to the client APIs to
support changes in the Openverse REST API will be reflected as major, minor, or
patch versions depending on their affect to the client API, rather than to
reflect the significance of changes in the Openverse REST API.

## Development and implementation details

This package and the `@openverse/api-client` package rely on types and code
generated based on the Openverse REST API's OpenAPI schema. You can access the
schema at <https://api.openverse.org/v1/schema/>.

An internal `openverse_api_client_generator` package is responsible for
interpreting the OpenAPI schema and translating it into Python data structures
used to generate Python and TypeScript code from Jinja2 templates.

To generate new code based on the latest OpenAPI schema, run:

```shell
ov just pdm api-client run generate --openverse-api-url https://api.openverse.org
```

This will update the Python and TypeScript code. Changes to the generated files
should be committed, even though they are generated artefacts. The rationale for
this is to support building the API clients without needing to have access to a
running Openverse API instance (for example, in CI/CD), otherwise every new
clone of the Openverse repository (including in CI) would need to generate the
API client code.

This also makes it easier to review changes in the generated code as it will
appear directly in pull request diffs.

The API clients are not strictly coupled to the latest code in the Openverse
API. New client code only needs to be generated when new features are available
in the production Openverse API. Decoupling these from each other allows
Openverse maintainers to verify new features in production before publishing API
clients that support them, in case those features need to be rolled back. This
means maintainers must intentionally generate new API client code for review in
PRs separate from the changes to the Openverse REST API itself.

## License

`openverse-api-client` is distributed under the terms of the
[MIT license](https://spdx.org/licenses/MIT.html).

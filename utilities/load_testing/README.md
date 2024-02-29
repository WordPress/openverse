# Load testing

This directory contains a collection of locust files for load testing the
Openverse application. Currently, only an API load test exists but in the future
we can also create load tests for the frontend or any other service we stand up.
These exist in this repository rather than one of the service specific ones for
this reason. We can reuse the base docker image we create for all our load
testing scripts.

**Note:** Production is throttled, so these scripts cannot be used as a shortcut
to DDoS our production stack.

## Running the tests

### Setup

#### API

The API load tests assume that you will be using an API key as it is impossible
to make unauthenticated requests large enough (`page_size=500`) to facilitate
easy flooding. Likewise, unless throttling is temporarily disabled in the
environment being tested, you'll probably want to exempt the API key from
throttling by adding it to the
[API Key throttle exemption](https://github.com/WordPress/openverse-api/blob/c09fd7e16a8eb104c311e8d4f0da08238570067c/api/catalog/api/utils/throttle.py#L77).
Please ping `@WordPress/openverse-maintainers` for help doing this in live
environments as it requires adding the key to a set in that environment's Redis
cache.

To make the API key accessible to the load testing script, copy the
`.env.sh.template` file and name it `.env.sh` and fill in the `ACCESS_TOKEN`
variable.

### Running

All load tests are accessible through `just` scripts in this directory's
`justfile`.

To run API load tests against a local API instance, use `just api`. You can
optionally specify a host (the default is to point to local). For example
`just api https://api-staging.openverse.engineering` will run the load tests
against the staging API.

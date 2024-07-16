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

#### Frontend

By default, the frontend load tests run against `https://openverse.org`. It is
important to disable the Cloudflare cache and WAF security settings for the
duration of the test to test the actual performance of the application instead
of testing Cloudflare cache or getting blocked by WAF. By default, the tests
request only the English static pages. You can specify other scenarios to run,
with `ov just load_testing/k6 all` being the most comprehensive test that
requests static and search pages in English. The `locales` tests request pages
in 3 other locales.

### Running

All load tests are accessible through `just` scripts in this directory's
`justfile`.

To run API load tests against a local API instance, use
`ov just load_testing/api`. You can optionally specify a host (the default is to
point to local). For example
`ov just load_testing/api https://api-staging.openverse.org` will run the load
tests against the staging API.

To run the frontend load tests, use `ov just load_testing/k6-frontend`. You can
optionally specify the scenarios to run, for example,
`ov just load_testing/k6-frontend all`. To specify a host (the default is to
point to the `openverse.org`), set the `FRONTEND_URL` environment variable. For
example,
`ov env FRONTEND_URL=https://staging.openverse.org just load_testing/k6-frontend`
will run the load tests against the staging frontend.

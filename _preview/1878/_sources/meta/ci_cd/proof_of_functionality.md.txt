# Proof-of-functionality

In the CI + CD workflow, the concept of proof-of-functionality is used to
determine if the build assets of a service are fit for
[three use cases](./flow.md).

- [Docs publish](./flow.md#documentation)
- [GHCR publish](./flow.md#docker-publishing)
- [Staging deploy](./flow.md#deployment)

For different services, different tests are considered to establish
proof-of-functionality for different use-cases.

| Service          | Docs publish                                      | GHCR publish                                      | Staging deploy                                                                                |
| ---------------- | ------------------------------------------------- | ------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Catalog          | [`test-cat`](./jobs/catalog.md#test-cat)          | [`test-cat`](./jobs/catalog.md#test-cat)          | [`test-cat`](./jobs/catalog.md#test-cat)                                                      |
| Ingestion server | [`test-ing`](./jobs/ingestion_server.md#test-ing) | [`test-ing`](./jobs/ingestion_server.md#test-ing) | [`test-ing`](./jobs/ingestion_server.md#test-ing)                                             |
| API              | [`test-api`](./jobs/api.md#test-api)              | [`test-api`](./jobs/api.md#test-api)              | [`test-api`](./jobs/api.md#test-api)                                                          |
| Frontend         | [`nuxt-build`](./jobs/frontend.md#nuxt-build)     | [`nuxt-build`](./jobs/frontend.md#nuxt-build)     | [`nuxt-build`](./jobs/frontend.md#nuxt-build) + [`playwright`](./jobs/frontend.md#playwright) |

## Rationales

### Catalog

The tests for the catalog in `test-cat` are very comprehensive and rigourous,
including extended test suites using the `--extended` flag. Passing these tests
conclusively proves that the catalog works as intended.

### Ingestion server

The ingestion server integration test in `test-ing` invokes all the key
functionality of the ingestion server. Passing these tests conclusively proves
that the ingestion server works as intended.

### API

The API tests in `test-api` include both unit tests for the API and integration
tests that explore the API's functionality. These tests also include example
tests wherein the API's output is compared to known-good output. Passing these
tests conclusively proves that the API works as intended.

### Frontend

The frontends difference between criteria for GHCR publish and staging deploy is
a controversial choice. 🚧 We will revise this.

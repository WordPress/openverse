# Proof-of-functionality

In the CI + CD workflow, the concept of proof-of-functionality is used to
determine if the build assets of a service are fit for
[three use cases](/meta/ci_cd/flow.md).

- [Docs publish](/meta/ci_cd/flow.md#documentation-emit)
- [GHCR publish](/meta/ci_cd/flow.md#docker-publishing)
- [Staging deploy](/meta/ci_cd/flow.md#deployment)

For different services, different tests are considered to establish
proof-of-functionality for different use-cases.

| Service          | Docs publish                                                 | GHCR publish                                                | Staging deploy                                              |
| ---------------- | ------------------------------------------------------------ | ----------------------------------------------------------- | ----------------------------------------------------------- |
| Catalog          | [`test-cat`](/meta/ci_cd/jobs/catalog.md#test-cat)           | [`test-cat`](/meta/ci_cd/jobs/catalog.md#test-cat)          | [`test-cat`](/meta/ci_cd/jobs/catalog.md#test-cat)          |
| Ingestion server | [`test-ing`](/meta/ci_cd/jobs/ingestion_server.md#test-ing)  | [`test-ing`](/meta/ci_cd/jobs/ingestion_server.md#test-ing) | [`test-ing`](/meta/ci_cd/jobs/ingestion_server.md#test-ing) |
| API              | [`test-api`](/meta/ci_cd/jobs/api.md#test-api)               | [`test-api`](/meta/ci_cd/jobs/api.md#test-api)              | [`test-api`](/meta/ci_cd/jobs/api.md#test-api)              |
| Frontend         | [`playwright`](/meta/ci_cd/jobs/frontend.md#playwright)      | [`playwright`](/meta/ci_cd/jobs/frontend.md#playwright)     | [`playwright`](/meta/ci_cd/jobs/frontend.md#playwright)     |
| Documentation    | [`build-docs`](/meta/ci_cd/jobs/documentation.md#build-docs) |                                                             |                                                             |

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

The Playwright tests for the frontend in `playwright` include E2E tests, visual
regression tests for the pages, and also tests for the Storybook stories.
Passing these tests conclusively proves that each individual component, and also
the frontend as a whole, looks and works as intended.

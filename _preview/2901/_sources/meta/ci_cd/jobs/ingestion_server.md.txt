# Ingestion server jobs

## `test-ing`

Runs tests for the ingestion server using the `ingestion_server/test-local`
recipe. Tests are run on the host so Python needs to be installed and set up.

This job is skipped if the ingestion server codebase has not changed. Its
counterparts are

- [`test-cat`](/meta/ci_cd/jobs/catalog.md#test-cat) for the catalog
- [`test-api`](/meta/ci_cd/jobs/api.md#test-api) for the API
- [`nuxt-build`](/meta/ci_cd/jobs/frontend.md#nuxt-build) for the frontend
- [`build-docs`](/meta/ci_cd/jobs/documentation.md#build-docs) for the
  documentation

This job exports the [`ing_logs` artifact](/meta/ci_cd/artifacts.md#logs).

```{note}
This job is treated as the proof of functionality for publishing Docker images
for the ingestion server.
```

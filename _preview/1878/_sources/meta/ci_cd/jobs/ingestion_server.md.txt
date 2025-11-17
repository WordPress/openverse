# Ingestion server jobs

### `test-ing`

Runs tests for the ingestion server using the `ingestion_server/test-local`
recipe. Tests are run on the host so Python needs to be installed and set up.

This job is skipped if the ingestion server codebase has not changed. Its
counterparts are [`test-cat`](#test-cat) for the catalog,
[`test-api`](#test-api) for the API and [`nuxt-build`](#nuxt-build) for the
frontend.

```{note}
This job is treated as the proof of functionality for publishing Docker images
for the ingestion server.
```

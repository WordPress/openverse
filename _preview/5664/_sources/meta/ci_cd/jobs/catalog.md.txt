# Catalog jobs

## `test-cat`

Runs tests for the catalog using the `catalog/test` recipe. Tests are run inside
a Docker container so neither Python nor Node.js needs to be installed.

This job is skipped if the catalog codebase has not changed. Its counterparts
are [`test-ing`](/meta/ci_cd/jobs/ingestion_server.md#test-ing) for the
ingestion server, [`test-api`](/meta/ci_cd/jobs/api.md#test-api) for the API and
[`nuxt-build`](/meta/ci_cd/jobs/frontend.md#nuxt-build) for the frontend.

```{note}
This job is treated as the proof of functionality for publishing Docker images
for the catalog.
```

## `catalog-checks`

Runs tests for the catalog using the `catalog/generate-docs` recipe. The job
runs inside a Docker container so Python does not need to be installed. However,
the job generates a new documentation page that must be linted, so
[`setup-env`](/meta/ci_cd/actions.md#setup-env) in invoked to set up Node.js and
linting dependencies.

This job is skipped if the catalog codebase has not changed.

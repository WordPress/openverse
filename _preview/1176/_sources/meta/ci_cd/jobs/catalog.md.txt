# Catalog jobs

## `test-cat`

Runs tests for the catalog using the `catalog/test` recipe. Tests are run inside
a Docker container so neither Python nor Node.js needs to be installed.

This job is skipped if the catalog codebase has not changed. Its counterparts
are [`test-ing`](#test-ing) for the ingestion server, [`test-api`](#test-api)
for the API and [`nuxt-build`](#nuxt-build) for the frontend.

```{note}
This job is treated as the proof of functionality for publishing Docker images
for the catalog.
```

## `catalog-checks`

Runs tests for the catalog using the `catalog/generate-dag-docs` recipe. The job
runs inside a Docker container so Python does not need to be installed. However,
the job generates a new documentation page that must be linted, so
[`setup-env`](#setup-env) in invoked to set up Node.js and linting dependencies.

This job is skipped if the catalog codebase has not changed.

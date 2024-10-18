# API jobs

```{mermaid}
flowchart TB
  get-changes{{get-changes}} -- API unchanged --> bypass-django-checks
  get-changes -- API changed --- x[&nbsp] --> deploy-api & test-api & django-checks

  get-changes --> determine-images
  determine-images & get-image-tag & lint --> build-images --> test-api & django-checks --> publish-images --> deploy-api

  style x height:0
```

The API flow uses the following other jobs.

- [`get-changes`](./helpers.md#get-changes)
- [`determine-images`](./docker.md#determine-images)
- [`get-image-tag`](./helpers.md#get-image-tag)
- [`lint`](./helpers.md#lint)
- [`build-images`](./docker.md#build-images)
- [`publish-images`](./docker.md#publish-images)

## `test-api`

Initialises the API using the `api/init` recipe and runs tests for the API using
the `api/test` recipe. Tests are run inside a Docker container so neither Python
nor Node.js needs to be installed.

This job is skipped if the API codebase has not changed. Its counterparts are
[`test-cat`](#test-cat) for the catalog, [`test-ing`](#test-ing) for the
ingestion server and [`nuxt-build`](#nuxt-build) for the frontend.

```{note}
This job is treated as the proof of functionality for publishing Docker images
for the API. Since the job also initialises the API, it provides a basic
verification of the ingestion server's core functionality of populating the API
database and Elasticsearch.
```

## `django-checks`

Runs a matrix of various Django checks for the API using the following `just`
recipes.

- `api/dj check`
- `api/dj validateopenapischema`
- `api/dj makemigrations --check --noinput --merge`
- `api/doc-test`

This job is skipped if the API codebase has not changed. Its counterpart is
[`nuxt-checks`](#nuxt-checks) for the frontend.

Since this is a required check for a matrix job, it has a bypass counterpart.
Refer to the documentation for [bypass jobs](#bypass-jobs).

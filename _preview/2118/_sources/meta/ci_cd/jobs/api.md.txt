# API jobs

The API flow uses the following other jobs.

- [`get-changes`](/meta/ci_cd/jobs/preparation.md#get-changes)
- [`determine-images`](/meta/ci_cd/jobs/docker.md#determine-images)
- [`get-image-tag`](/meta/ci_cd/jobs/preparation.md#get-image-tag)
- `lint`
- [`build-images`](/meta/ci_cd/jobs/docker.md#build-images)
- [`publish-images`](/meta/ci_cd/jobs/docker.md#publish-images)

## `test-api`

Initialises the API using the `api/init` recipe and runs tests for the API using
the `api/test` recipe. Tests are run inside a Docker container so neither Python
nor Node.js needs to be installed.

This job is skipped if the API codebase has not changed. Its counterparts are

- [`test-cat`](/meta/ci_cd/jobs/catalog.md#test-cat) for the catalog
- [`test-ing`](/meta/ci_cd/jobs/ingestion_server.md#test-ing) for the ingestion
  server
- [`nuxt-build`](/meta/ci_cd/jobs/frontend.md#nuxt-build) for the frontend
- [`build-docs`](/meta/ci_cd/jobs/documentation.md#build-docs) for the
  documentation

This job exports the [`api_logs` artifact](/meta/ci_cd/artifacts.md#logs).

```{note}
This job is treated as the proof of functionality for publishing Docker images
for the API. Since the job also initialises the API, it provides a basic
verification of the ingestion server's core functionality of populating the API
database and Elasticsearch.
```

## `django-checks`

Runs a matrix of various Django checks for the API using the following `just`
recipes.

| Name               | Recipe                                                                    |
| ------------------ | ------------------------------------------------------------------------- |
| `check_django`     | `api/dj check`                                                            |
| `validate_openapi` | `api/dj spectacular --format openapi-json --validate --file openapi.json` |
| `check_migrations` | `api/dj makemigrations --check --noinput --merge`                         |
| `test_doc`         | `api/doc-test`                                                            |

This job is skipped if the API codebase has not changed. Its counterpart is
[`nuxt-checks`](/meta/ci_cd/jobs/frontend.md#nuxt-checks) for the frontend.

Since this is a required check for a matrix job, it has a bypass counterpart.
Refer to the documentation for [bypass jobs](/meta/ci_cd/flow.md#bypass-jobs).

The job with the name `test_doc` in this matrix exports the
[`openapi.json` artifact](/meta/ci_cd/artifacts.md#documentation).

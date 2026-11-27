# Frontend jobs

## `nuxt-build`

Builds the frontend to raise any major issues that could cause the build to
fail. If the build succeeds, no such issues exist.

This job is skipped if the frontend codebase has not changed. Its counterparts
are

- [`test-cat`](/meta/ci_cd/jobs/catalog.md#test-cat) for the catalog
- [`test-api`](/meta/ci_cd/jobs/api.md#test-api) for the API
- [`test-ing`](/meta/ci_cd/jobs/ingestion_server.md#test-ing) for the ingestion
  server
- [`build-docs`](/meta/ci_cd/jobs/documentation.md#build-docs) for the
  documentation

```{note}
This job is treated as the proof of functionality for publishing Docker images
for the frontend.

This job, combined with the [`playwright` job](#playwright), is treated as the
proof of functionality for deploying frontend to staging.
```

## `nuxt-checks`

Runs a matrix for various Nuxt checks for the frontend using the following
Node.js scripts.

| Name                   | Script            |
| ---------------------- | ----------------- |
| `unit_test`            | `test:unit`       |
| `storybook_smoke_test` | `storybook:smoke` |

This job is skipped if the frontend codebase has not changed. Its counterpart is
[`django-checks`](/meta/ci_cd/jobs/api.md#django-checks) for the API.

Since this is a required check for a matrix job, it has a bypass counterpart.
Refer to the documentation for [bypass jobs](/meta/ci_cd/flow.md#bypass-jobs).

## `playwright`

Runs a matrix of various Playwright tests for the frontend using the following
Node.js scripts.

| Name             | Script                              |
| ---------------- | ----------------------------------- |
| `playwright_vr`  | `test:playwright visual-regression` |
| `playwright_e2e` | `test:playwright e2e`               |
| `storybook_vr`   | `test:storybook`                    |

This job is skipped if the frontend codebase has not changed.

```{note}
This job, combined with the [`nuxt-build` job](/meta/ci_cd/jobs/frontend.md#nuxt-build), is treated as the
proof of functionality for deploying frontend to staging.
```

Since this is a required check for a matrix job, it has a bypass counterpart.
Refer to the documentation for [bypass jobs](/meta/ci_cd/flow.md#bypass-jobs).

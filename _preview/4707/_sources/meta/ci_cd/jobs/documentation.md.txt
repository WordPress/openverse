# Documentation jobs

## `build-docs`

Builds the developer documentation and uploads it as an artifact.

This job is skipped if neither the documentation nor the frontend codebase has
changed. Its counterparts are

- [`test-cat`](/meta/ci_cd/jobs/catalog.md#test-cat) for the catalog
- [`test-api`](/meta/ci_cd/jobs/api.md#test-api) for the API
- [`test-ing`](/meta/ci_cd/jobs/ingestion_server.md#test-ing) for the ingestion
  server
- [`nuxt-build`](/meta/ci_cd/jobs/frontend.md#nuxt-build) for the frontend

This job exports the
[`documentation` artifact](/meta/ci_cd/artifacts.md#documentation).

```{note}
This job is treated as the proof of functionality for the publishing the
documentation.
```

## `emit-docs`

Downloads the documentation artifact and publishes it to an appropriate target.
For PRs, the target is a subdirectory under `_preview/` of the docs site, e.g.
the docs for PR #420 will be published at
<https://docs.openverse.org/_preview/420/>. For commits to `main`, the target is
the <https://docs.openverse.org/> site itself.

```{caution}
This job only publishes developer documentation. The API documentation hosted at
<https://api.openverse.org/v1/> is provided by the API service itself.
```

This job is skipped if neither the documentation nor the frontend codebase has
changed. It is also not executed on forks and for PRs made by Dependabot.

Documentation is only emitted if all the following conditions are met.

- the event is one of the following
  - a `push` to `main` and
    - the repo is `WordPress/openverse` and not a fork
  - a PR and
    - the source is a branch of `WordPress/openverse` and not a fork
    - the author of the PR is not Dependabot
- either the documentation or the frontend has changed (for Storybook)
- all the primary tests ([`test-cat`](/meta/ci_cd/jobs/catalog.md#test-cat),
  [`test-ing`](/meta/ci_cd/jobs/ingestion_server.md#test-ing),
  [`test-api`](/meta/ci_cd/jobs/api.md#test-api),
  [`nuxt-build`](/meta/ci_cd/jobs/frontend.md#nuxt-build)) succeeded, implying
  that their changes are valid, or were skipped, implying that they have no
  changes.

A comment is also published linking to the generated preview, and any new or
modified pages.

## `clean-gh-pages`

This job is executed when a PR is closed
([see the GitHub workflow](https://github.com/WordPress/openverse/blob/main/.github/workflows/pr_closed.yml)).
If a docs preview was generated, this job deletes the preview and pushes the
removal commit to the associated branch.

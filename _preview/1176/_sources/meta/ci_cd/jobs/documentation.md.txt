# Documentation jobs

## `emit-docs`

Builds the developer documentation and publishes it to an appropriate target.
For PRs, the target is a subdirectory under `_preview/` of the docs site, e.g.
the docs for PR #420 will be published at
<https://docs.openverse.org/_preview/420/>. For commits to `main`, the target is
the <https://docs.openverse.org/> site itself.

```{caution}
This job only publishes developer documentation. The API documentation hosted at
<https://api.openverse.engineering/v1/> is provided by the API service itself.
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
- either the documentation or the frontend has changed (for the Storybook and
  Tailwind Config Viewer)
- all the primary tests ([`test-cat`](#test-cat), [`test-ing`](#test-ing),
  [`test-api`](#test-api), [`nuxt-build`](#nuxt-build)) succeeded, implying that
  their changes are valid, or were skipped, implying that they have no changes.

## `clean-gh-pages`

This job is executed when a PR is closed
([see the GitHub workflow](https://github.com/WordPress/openverse/blob/main/.github/workflows/pr_closed.yml)).
If a docs preview was generated, this job deletes the preview and pushes the
removal commit to the associated branch.

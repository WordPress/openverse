# Preparation jobs

## `get-changes`

Triggers the [`get-changes`](#get-changes) action to determine the changes. In
addition to the `changes` from the action output, it emits some additional
outputs that are used by subsequent jobs.

**Outputs:**

Each of the `boolean` properties denote whether the PR or commit includes
changes for the corresponding stack.

```typescript
{
  changes: string // JSON-encoded array of modified changesets
  catalog: boolean
  ingestion_server: boolean
  api: boolean
  frontend: boolean
  documentation: boolean
}
```

## `get-image-tag`

Determines the tag to use for the Docker images. If the job is triggered via a
workflow dispatch, the images are tagged with the `image_tag` input taken by the
dispatch. If the job is triggered via a PR or a commit pushed to `main`, the
images are tagged with the full 40-char hash
([`github.sha`](https://docs.github.com/en/actions/learn-github-actions/contexts#github-context))
of the last commit.

**Outputs:**

```typescript
{
  image_tag: string // the tag to use for the Docker images
}
```

## `lint`

Runs the linting steps defined in the repository's
[pre-commit configuration](https://github.com/WordPress/openverse/blob/main/.pre-commit-config.yaml).
This is executed via `just lint`.

## `validate-codeowners`

This job should be considered a complement to `lint` and would ideally be part
of it, as a pre-commit hook. However, the docker image we relied on for the
pre-commit hook causes issues with arm64 computers (which includes recent Apply
devices). Therefore, we run the hook as a CI step instead.

It is still possible to run this hook locally, assuming the docker image works
on your computer's architecture, by invoking the `lint-codeowners` just recipe:

```bash
ov just lint-codeowners
```

````{tip}
In CI we run the set of "experimental" checks as well, which are disabled
in the just recipe because they fail if there are uncommitted changes.
To run precisely the check that CI uses, enable experimental checks:

```bash
ov just lint-codeowners all
```

````

## `add-stack-label`

```{note}
This job only runs on PRs.
```

Use the outputs from the [`get-changes`](#get-changes) job to add an appropriate
`stack` label to the PR. If a label cannot be determined from the changes, the
`🚦 status: awaiting triage` and `🏷 status: label work required` labels are
added instead.

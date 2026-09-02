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

# CI + CD workflow

The CI + CD workflow is the primary pipeline of the project. It runs the tests
for all layers of the stack (which have changed in the current PR or commit)
and, if the tests pass, publishes the documentation to the docs site and deploys
the API and frontend to their respective staging ECS targets.

It's a complex workflow with many jobs that depend on each other and the number
of paths it can take becomes huge because jobs can be skipped based on the
contents of a PR or commit.

## Output

The CI + CD workflow has four main outputs when new commits are pushed to the
`main` branch, although not all outputs are expected on each commit. The first
of these, "documentation" is also applicable to PRs.

- **Documentation:** For each PR which affects the documentation, the
  documentation is built and deployed to a preview site. When a new commit is
  pushed to `main` that affects the documentation, the documentation is built
  and deployed to the [root of the docs site](https://docs.openverse.org).

  See job [`emit-docs`](#emit-docs) for details.

- **Docker images:** When a new commit is pushed to `main`, the Docker images
  for each of the affected services is pushed to
  [GHCR](https://github.com/orgs/WordPress/packages?repo_name=openverse). These
  images are tagged with the SHA of the commit.

  See job [`publish-images`](#publish-images).

- **Frontend staging:** When a new commit is pushed to `main` which affects the
  frontend service and the tests for the frontend pass, a new
  [staging deployment of the frontend](https://staging.openverse.org/) is
  triggered. The deployment uses the image published above.

  See job [`deploy-frontend`](#deploy-frontend).

- **API staging:** When a new commit is pushed to `main` which affects the API
  service and the tests for the API pass, a new
  [staging deployment of the API](https://api-staging.openverse.engineering/) is
  triggered. The deployment uses the image published above.

  See job [`deploy-api`](#deploy-api).

## Actions

The workflow depends on four actions that have been taken out of the workflow
for reuse and readability.

### `get-changes`

Determines the changes made to the codebase for a PR or commit. Based on the
changeset, only a subset of the workflow is executed, both in the interest of
speed and to avoid wasteful consumption of resources.

**Outputs:**

```typescript
{
  changes: string // JSON-encoded array of modified changesets
}
```

### `setup-env`

Sets up the runtime environment for a job. It sets up our task runner of choice,
[`just`](../guides/general_setup.md#just) and also the specified languages and
their respective package managers.

- Python (and Pipenv)
- Node.js (and pnpm)

By default, both Python and Node.js are installed and configured by this action
but it's recommended to use `setup_python` and `setup_nodejs` inputs to only
install the runtime needed by a job.

By default, it also runs `just install` so that the core dependencies needed on
the system are installed. This recipe can be customised via the `install_recipe`
input (or even disabled with a blank string, to speed up the process in case no
host dependencies are needed).

**Inputs:**

```typescript
{
  setup_python: "true" | "false" // default: "true"
  setup_nodejs: "true" | "false" // default: "true"
  install_deps: "true" | "false" // default: "true"
  install_recipe: string // default: "install"
}
```

### `load-img`

All Docker images needed throughout the CI + CD workflow are built by the
[`build-images`](#build-images) job matrix, saved as `.tar` files and uploaded
as artifacts. This action is used by subsequent jobs that need those images. It
downloads the artifact and load the `.tar` files into Docker as images.

By default, all images built by the Docker system will be loaded but if the job
only needs a subset of images, those can be set via the `setup_images` input,
passing a JSON encoded array of image names as strings.

**Inputs:**

```typescript
{
  setup_images: string // default: '["upstream_db", "ingestion_server", "catalog", "api", "api_nginx"]'
}
```

### `build-docs`

Builds the documentation, including this Sphinx site, the frontend Storybook and
the Tailwind config viewer and stores it at `/tmp/docs`. This compiled
documentation is deployed to an appropriate location by the
[`emit-docs`](#emit-docs) job.

It needs the inputs `glotpress_username` and `glotpress_password` to download
translations from GlotPress.

```typescript
{
  glotpress_username: string // required, use secret `MAKE_USERNAME`
  glotpress_password: string // required, use secret `MAKE_LOGIN_PASSWORD`
}
```

## Helper jobs

### `get-changes`

Triggers the [`get-changes`](#get-changes) action to determine the changes. In
addition to the `changes` from the action output, it emits some additional
outputs that are used by subsequent jobs.

**Outputs:**

```typescript
{
  changes: string // JSON-encoded array of modified changesets
  catalog: boolean // whether `changes` contains 'catalog'
  ingestion_server: boolean // whether `changes` contains 'ingestion_server'
  api: boolean // whether `changes` contains 'api'
  frontend: boolean // whether `changes` contains 'frontend'
  documentation: boolean // whether `changes` contains 'documentation'
}
```

### `get-image-tag`

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

### `determine-images`

Determines which images to build and publish as a part of the workflow run. To
speed up the workflow and avoid wasteful resource consumption, only a subset of
all images are built by the workflow and a only subset of those images are
published to GHCR. This job determines those images.

| Change             | `upstream_db` | `catalog` | `ingestion_server` | `api` | `api_nginx` | `frontend` |
| ------------------ | ------------- | --------- | ------------------ | ----- | ----------- | ---------- |
| `catalog`          | 🛠️            | 🚀        |                    |       |             |            |
| `ingestion_server` | 🛠️            |           | 🚀                 | 🛠️    |             |            |
| `api`              | 🛠️            |           | 🛠️                 | 🚀    | 🚀          |            |
| `frontend`         |               |           |                    |       |             | 🚀         |

🚀 implies that the image is published to GHCR. 🛠️ implies that the image is
built but not published.

```{note}
The `upstream_db` image is only built here and reused in other workflows for
convenience and speed, it is never published.
```

**Outputs:**

```typescript
interface Output {
  do_build: "true" | "false" // whether one or more images are to be built
  build_matrix: {
    image: (
      | "upstream_db"
      | "catalog"
      | "ingestion_server"
      | "api"
      | "api_nginx"
      | "frontend"
    )[] // the names of the image to be built
    include: (
      | { image: "upstream_db"; context: "docker/upstream_db"; target: "db" }
      | { image: "catalog"; context: "catalog"; target: "cat" }
      | {
          image: "ingestion_server"
          context: "ingestion_server"
          target: "ing"
        }
      | { image: "api"; context: "api"; target: "api" }
      | { image: "api_nginx"; context: "api"; target: "nginx" }
    )[] // additional information about images to be built
  }
  do_publish: "true" | "false" // whether one or more images are to be published
  publish_matrix: {
    image: ("catalog" | "ingestion_server" | "api" | "api_nginx" | "frontend")[] // the name of the image to be published
  }
}
```

## Universal jobs

### `build-images`

Builds images as dictated by the [`determine-images`](#determine-images) job.
Since the images are built in a matrix, some image-specific steps are
conditionally run using an `if` expression. Since any unused Docker build
arguments have no effect, the job simply populates all build arguments needed by
all images.

Images built by this job are published as `.tar` artifacts and can be loaded
into other jobs that need them using the [`load-img`](#load-img) action.

This job is only run if there is at least one image needed to build, based on
the `do_build` output of the [`determine-images`](#determine-images) job.

## Catalog jobs

### `test-cat`

Runs tests for the catalog using the `catalog/test` recipe. Tests are run inside
a Docker container so neither Python nor Node.js needs to be installed.

This job is skipped if the catalog codebase has not changed. Its counterparts
are [`test-ing`](#test-ing) for the ingestion server, [`test-api`](#test-api)
for the API and [`nuxt-build`](#nuxt-build) for the frontend.

```{note}
This job is treated as the proof of functionality for publishing Docker images
for the catalog.
```

### `catalog-checks`

Runs tests for the catalog using the `catalog/generate-dag-docs` recipe. The job
generates a new file from a Docker container so Python does not need to be
installed. However, the job runs linting on the new file, so Node.js needs to be
set up.

This job is skipped if the catalog codebase has not changed.

## Ingestion server jobs

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

## API jobs

### `test-api`

Initialises the API using the `api/init` recipe and runs tests for the API using
the `api/test` recipe. Tests are run inside a Docker container so neither Python
nor Node.js needs to be installed.

This job is skipped if the API codebase has not changed. Its counterparts are
[`test-cat`](#test-cat) for the catalog, [`test-ing`](#test-ing) for the
ingestion server and [`nuxt-build`](#nuxt-build) for the frontend.

```{note}
This job is treated as the proof of functionality for publishing Docker images
for the API. Since it also initialises the API, it also largely proves that the
ingestion server is working.
```

### `django-checks`

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

## Frontend jobs

### `nuxt-build`

```{note}
This job is treated as the proof of functionality for publishing Docker images
for the frotend.

This job, combined with the [`playwright` job](#playwright), is treated as the
proof of functionality for deploying frontend to staging.
```

### `nuxt-checks`

Runs a matrix for various Nuxt checks for the frontend using the following
Node.js scripts.

- `test:unit`
- `storybook:smoke`

This job is skipped if the frontend codebase has not changed. Its counterpart is
[`django-checks`](#django-checks) for the API.

Since this is a required check for a matrix job, it has a bypass counterpart.
Refer to the documentation for [bypass jobs](#bypass-jobs).

### `playwright`

Runs a matrix of various Playwright tests for the frontend using the following
Node.js scripts.

- `test:playwright visual-regression`
- `test:playwright e2e`
- `test:storybook`

This job is skipped if the frontend codebase has not changed.

```{note}
This job, combined with the [`nuxt-build` job](#nuxt-build), is treated as the
proof of functionality for deploying frontend to staging.
```

Since this is a required check for a matrix job, it has a bypass counterpart.
Refer to the documentation for [bypass jobs](#bypass-jobs).

## Documentation jobs

### `emit-docs`

Builds the documentation and publishes it to an appropriate target. For PRs, the
target is a subdirectory under `_preview/` of the docs site, e.g. the docs for
PR #420 will be published at <https://docs.openverse.org/_preview/420/>. For
commits to `main`, the target is the <https://docs.openverse.org/> site itself.

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

## Docker images jobs

### `publish-images`

Publishes images to GHCR as dictated by the
[`determine-images`](#determine-images) job. In a matrix, this job downloads the
images to be published from their `.tar` files using the [`load-img`](#load-img)
job and then tags and pushes them to GHCR.

Images are only published if all the following conditions are met.

- the event is a push to `main`
- the repo is `WordPress/openverse` and not a fork
- there is at least one image to publish as per the `do_publish` output of the
  [`determine-images`](#determine-images) job
- all the primary tests ([`test-cat`](#test-cat), [`test-ing`](#test-ing),
  [`test-api`](#test-api), [`nuxt-build`](#nuxt-build)) succeeded, implying that
  their changes are valid, or were skipped, implying that they have no changes.

## Deployment jobs

### `deploy-frontend`

Triggers a separate workflow using `workflow_dispatch` that deploys the staging
environment of the frontend service to AWS ECS. That workflow is given two
inputs.

- the tag of the image that was published by the
  [`publish-images`](#publish-images) job, which is the output of the
  [`get-image-tag`](#get-image-tag) job
- the actor of the CI + CD workflow, for tagging them in Slack messages

This deployment is only triggered if all the following conditions are met.

- the frontend codebase has changed
- the [`playwright`](#playwright) job has passed, implying no visual regressions
  have occurred
- the [`publish-images`](#publish-images) job has passed, publishing the latest
  frontend image to GHCR
  - The fact that [`publish-images`](#publish-images) ran implies
    [`nuxt-build`](#nuxt-build) passed.

### `deploy-api`

Triggers a separate workflow using `workflow_dispatch` that deploys the staging
environment of the API service to AWS ECS. That workflow is given two inputs.

- the tag of the image that was published by the
  [`publish-images`](#publish-images) job, which is the output of the
  [`get-image-tag`](#get-image-tag) job
- the actor of the CI + CD workflow, for tagging them in Slack messages

This deployment is only triggered if all the following conditions are met.

- the API codebase has changed
- the [`publish-images`](#publish-images) job has passed, publishing the latest
  frontend image to GHCR
  - The fact that [`publish-images`](#publish-images) ran implies
    [`test-api`](#test-api) passed.

## Notification jobs

### `send-report`

Sends a Slack report if the workflow did not do everything it was expected to
do. It lists the outcome for the 4 key outputs of the workflow for a push to
`main`.

This report is only sent if all the following conditions are met.

- the event is a push to `main`
- the repo is `WordPress/openverse` and not a fork
- one or more of the following expectations was not delivered
  - the documentation or frontend had changes, but new docs were not published
  - there were images meant to be published, but they were not published
  - the frontend codebase changed, but it was not deployed to staging
  - the API codebase changed, but it was not deployed to staging

The workflow sends a Slack message, listing the outcome of four jobs

- [`emit-docs`](#emit-docs)
- [`publish-images`](#publish-images)
- [`deploy-frontend`](#deploy-frontend)
- [`deploy-api`](#deploy-api)

Receiving this report in Slack is an indicator that the workflow did not
complete successfully. It is up to the MSR to investigate the cause of the
failure and take appropriate action.

## Bypass jobs

If a job is marked as a required check in GitHub it must
[either pass or be skipped](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/troubleshooting-required-status-checks#handling-skipped-but-required-checks)
to allow the PR to be merged. This is different for matrix jobs because if a
matrix is skipped due to an `if` condition, it is not expanded into individual
jobs but skipped as a whole, leaving the checks associated with that matrix in a
pending state, preventing PRs from being merged.

For such jobs, we use a bypass job, conventionally named `bypass-<job name>`,
that is run on the opposite of the condition of the original job. This bypass
job is an identical matrix, except it always succeeds, and satisfies the
required checks by having the same job names as the original.

# Actions

The CI + CD workflow is huge, so we broke off some reusable parts of it into
smaller, more manageable pieces in the form of composite actions.

These actions are located in the `.github/actions/` directory. To use them, the
repository must first be checked out using the
[`actions/checkout`](https://github.com/actions/checkout) action.

## `get-changes`

Determines the changes made to the codebase for a PR or commit. Based on the
changeset, only a subset of the workflow is executed, both in the interest of
speed and to avoid wasteful consumption of resources.

**Outputs:**

```typescript
{
  changes: string // JSON-encoded array of modified changesets
}
```

## `setup-env`

Sets up the runtime environment for a job. It sets up our task runner of choice,
[`just`](/general/general_setup.md#just) and also the specified languages and
their respective package managers.

- Python (and Pipenv)
- Node.js (and pnpm)

**Inputs:**

By default, both Python and Node.js are installed and configured by this action
but it's recommended to use `setup_python` and `setup_nodejs` inputs to only
install the runtime needed by a job.

By default, it also runs `just install` so that the core dependencies needed on
the system are installed. This recipe can be customised via the `install_recipe`
input (or even disabled with a blank string, to speed up the process in case no
host dependencies are needed).

```typescript
{
  setup_python: "true" | "false" // default: "true"
  setup_nodejs: "true" | "false" // default: "true"
  install_recipe: string // default: "install"
}
```

## `load-img`

All Docker images needed throughout the CI + CD workflow are built by the
[`build-images`](/meta/ci_cd/jobs/docker.md#build-images) job matrix, saved as
`.tar` files and uploaded as artifacts. This action is used by subsequent jobs
that need those images. It downloads the artifact and load the `.tar` files into
Docker as images.

**Inputs:**

By default, all images built by the Docker system will be loaded. However, if
the job only needs a subset of images, those can be set via the `setup_images`
input, passing a space-separated list of image names.

```typescript
{
  setup_images: string // default: 'upstream_db ingestion_server catalog api api_nginx frontend'
}
```

## `build-docs`

Builds the documentation, including this Sphinx site and the frontend Storybook
and stores it at `/tmp/docs`. This compiled documentation is deployed to an
appropriate location by the
[`emit-docs`](/meta/ci_cd/jobs/documentation.md#emit-docs) job.

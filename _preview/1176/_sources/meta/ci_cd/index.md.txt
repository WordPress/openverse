# CI + CD workflow

The CI + CD workflow is the primary pipeline of the project. It runs the tests
for all layers of the stack that have been changed by the PR or commit it is
being run against and, if the tests pass, publishes the documentation to the
docs site and deploys the API and frontend to their respective staging ECS
targets.

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

- **Docker images:** When a new commit is pushed to `main`, the Docker image for
  each of the affected services is pushed to
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

## Workflow components

```{toctree}
:maxdepth: 1

actions
jobs/index
flow
proof_of_functionality
```

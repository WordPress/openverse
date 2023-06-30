# Deployment jobs

## `deploy-api`

Triggers two separate workflows using `workflow_dispatch` that deploys the
staging environment of the API service and the thumbnails-specific API
deployment to AWS ECS. That workflows are given two inputs.

- the tag of the image that was published by the
  [`publish-images`](/meta/ci_cd/jobs/docker.md#publish-images) job, which is
  the output of the
  [`get-image-tag`](/meta/ci_cd/jobs/preparation.md#get-image-tag) job
- the actor of the CI + CD workflow, for tagging them in Slack messages

The deployments are only triggered if all the following conditions are met.

- the API codebase has changed
- the [`publish-images`](/meta/ci_cd/jobs/docker.md#publish-images) job has
  passed, publishing the latest frontend image to GHCR
  - The fact that [`publish-images`](/meta/ci_cd/jobs/docker.md#publish-images)
    ran implies [`test-api`](/meta/ci_cd/jobs/api.md#test-api) passed.

## `deploy-frontend`

Triggers a separate workflow using `workflow_dispatch` that deploys the staging
environment of the frontend service to AWS ECS. That workflow is given two
inputs.

- the tag of the image that was published by the
  [`publish-images`](/meta/ci_cd/jobs/docker.md#publish-images) job, which is
  the output of the
  [`get-image-tag`](/meta/ci_cd/jobs/preparation.md#get-image-tag) job
- the actor of the CI + CD workflow, for tagging them in Slack messages

This deployment is only triggered if all the following conditions are met.

- the frontend codebase has changed
- the [`playwright`](/meta/ci_cd/jobs/frontend.md#playwright) job has passed,
  implying no visual regressions have occurred
- the [`publish-images`](/meta/ci_cd/jobs/docker.md#publish-images) job has
  passed, publishing the latest frontend image to GHCR
  - The fact that [`publish-images`](/meta/ci_cd/jobs/docker.md#publish-images)
    ran implies [`nuxt-build`](/meta/ci_cd/jobs/frontend.md#nuxt-build) passed.

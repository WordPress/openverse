# Docker publishing jobs

## `publish-images`

Publishes images to GHCR as dictated by the
[`determine-images`](/meta/ci_cd/jobs/docker_preparation.md#determine-images)
job. In a matrix, this job downloads the images to be published from their
`.tar` files using the [`load-img`](/meta/ci_cd/actions.md#load-img) job and
then tags and pushes them to
[GHCR](https://github.com/orgs/WordPress/packages?repo_name=openverse).

Images are only published if all the following conditions are met.

- the event is a push to `main`
- the repo is `WordPress/openverse` and not a fork
- there is at least one image to publish as per the `do_publish` output of the
  [`determine-images`](/meta/ci_cd/jobs/docker_preparation.md#determine-images)
  job
- all the primary tests ([`test-cat`](/meta/ci_cd/jobs/catalog.md#test-cat),
  [`test-ing`](/meta/ci_cd/jobs/ingestion_server.md#test-ing),
  [`test-api`](/meta/ci_cd/jobs/api.md#test-api),
  [`nuxt-build`](/meta/ci_cd/jobs/frontend.md#nuxt-build)) succeeded, implying
  that their changes are valid, or were skipped, implying that they have no
  changes.

# Docker publishing jobs

## `publish-images`

Publishes images to GHCR as dictated by the
[`determine-images`](#determine-images) job. In a matrix, this job downloads the
images to be published from their `.tar` files using the [`load-img`](#load-img)
job and then tags and pushes them to
[GHCR](https://github.com/orgs/WordPress/packages?repo_name=openverse).

Images are only published if all the following conditions are met.

- the event is a push to `main`
- the repo is `WordPress/openverse` and not a fork
- there is at least one image to publish as per the `do_publish` output of the
  [`determine-images`](#determine-images) job
- all the primary tests ([`test-cat`](#test-cat), [`test-ing`](#test-ing),
  [`test-api`](#test-api), [`nuxt-build`](#nuxt-build)) succeeded, implying that
  their changes are valid, or were skipped, implying that they have no changes.
